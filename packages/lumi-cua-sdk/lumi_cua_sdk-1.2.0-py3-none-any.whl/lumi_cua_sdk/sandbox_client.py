from typing import List, Optional, Union, Dict, Any, Literal
import logging
import time
from contextlib import asynccontextmanager

from .models.common_models import (
    Action,
    ScreenshotResult,
    ComputerActionArgs,
    SandboxDetails,
    SandboxOsType,
    SandboxStreamDisplayType
)
from .models.tool_server_models import BaseResponse
from .services.sandbox_manager import SandboxManagerClient
from .services.sandbox_tool_server import AsyncToolServerClient
from .config import get_config
from .common.socket_client import RDPClient

logger = logging.getLogger(__name__)


class Sandbox:
    def __init__(self, details: SandboxDetails, auth_token: str=None, sandbox_manager_url: str=None):
        self.details = details
        _config = get_config()
        self.auth_token = auth_token or _config.auth_token
        self.sandbox_manager_url = sandbox_manager_url or _config.sandbox_manager_url
        if not self.auth_token:
            raise Exception("Conf: auth token is not provided")
        if not self.sandbox_manager_url:
            raise Exception("Conf: ecs manager url is not provided")
        self.sandbox_manager = SandboxManagerClient(endpoint=self.sandbox_manager_url, auth_token=self.auth_token)

        if details.tool_server_endpoint:
            tool_server_endpoint = details.tool_server_endpoint
        elif details.tool_server_proxy_uri:
            tool_server_endpoint = self.sandbox_manager_url + details.tool_server_proxy_uri
        else:
            logger.warning(f"Sandbox {details.id} initialized without a tool server endpoint. "
                           f"The CUA application may used a serverless gateway.")
            raise Exception("Get no tool server endpoint from sandbox detail info")

        self.tool_server_client = AsyncToolServerClient(tool_server_endpoint, auth_key=self.auth_token,
                                                        sandbox_id=self.details.id)
        
        # RDP connection management
        self._rdp_client: Optional[RDPClient] = None

    @property
    def id(self) -> str:
        return self.details.id

    @property
    def ip_address(self) -> Optional[str]:
        return self.details.primary_ip

    @property
    def os_type(self) -> Optional[str]:
        return self.details.os_type

    @property
    def tool_server_endpoint(self) -> Optional[str]:
        return self.tool_server_client.base_url

    @property
    async def display_type(self) -> Optional[str]:
        if self.details.os_type == SandboxOsType.LINUX.value:
            return "VNC"
        else:
            return await self._get_windows_sandbox_display_type()

    async def delete(self) -> Dict[str, Any]:
        """删除此实例。"""
        return await self.sandbox_manager.delete_sandbox(self.id)

    async def screenshot(self) -> ScreenshotResult:
        """获取屏幕截图。"""
        screenshot_response = await self.tool_server_client.take_screenshot()
        screen_size_response = await self.tool_server_client.get_screen_size()
        if not screen_size_response:
            raise Exception("Get screen shot failed")
    
        result = ScreenshotResult(
            width=screen_size_response.Result.width,
            height=screen_size_response.Result.height,
            base_64_image=screenshot_response.Result.screenshot
        )
        return result

    async def _get_windows_sandbox_display_type(self) -> str:
        response = await self.sandbox_manager.describe_sandbox_terminal_url(self.id)
        result = response.get('Result', {})
        return result.get("DisplayType", "GUACAMOLE")

    async def get_stream_url(self) -> str:
        """获取用于监控或交互的实例流式URL (例如 VNC/RDP over WebSocket or custom stream)。"""
        if not self.id:
            raise ValueError("Sandbox ID is not available to construct stream URL.")
        if not self.ip_address:
            raise ValueError("Sandbox IP address is not available to construct stream URL.")

        response = await self.sandbox_manager.describe_sandbox_terminal_url(self.id)
        result = response.get('Result', {})
        stream_url = result.get('Url')
        display_type = result.get('DisplayType')
        
        # Helper function to get base URL
        def get_base_url() -> str:
            if self.sandbox_manager_url.endswith("/mgr/"):
                return self.sandbox_manager_url.split("/mgr/")[0]
            elif get_config().web_ui_url:
                return get_config().web_ui_url
            else:
                logger.warning("No web ui endpoint provided")
                return ""
        
        def build_guacamole_url() -> str:
            windows_key = result.get('WindowsKey', self.id)
            base_url = get_base_url()
            return f"{base_url}/guac/index.html?url={stream_url}&instanceId={self.id}&ip={self.ip_address}&password={windows_key}&locale=zh"
        
        def build_vnc_url() -> str:
            token = result.get('Token')
            apig_url = ""
            if self.sandbox_manager_url.endswith("/mgr/"):
                apig_url = self.sandbox_manager_url.split("/mgr/")[0].lstrip("http://")
            elif get_config().vnc_proxy_url:
                apig_url = get_config().vnc_proxy_url.split("/vnc")[0].lstrip("http://")
            
            return (f"https://{apig_url}/novnc/vnc.html?host={apig_url}:443&"
                   f"autoconnect=true&resize=on&show_dot=true&resize=remote&path=vnc%3Ftoken%3D{token}")
        
        # Determine if this is Windows or should use Guacamole
        is_guacamole = (display_type == SandboxStreamDisplayType.GUACAMOLE.value or 
                     (not display_type and self.os_type == SandboxOsType.WINDOWS.value))
        
        if is_guacamole:
            if not stream_url:
                logger.warning("Get empty stream url from ecs manager. You may not have filled in AK/SK when creating the CUA application.")
                return ""
            return build_guacamole_url()
        else:
            # Linux/VNC case
            if stream_url:
                return stream_url
            else:
                logger.warning("Get empty stream url from ecs manager. In the case of non-standard gateways, "
                              "linux sandboxes currently do not support obtaining remote stream url.")
                return build_vnc_url()


    @asynccontextmanager
    async def rdp_session(self):
        """
        RDP 会话上下文管理器，用于保持长连接
        
        使用示例:
        async with sandbox.rdp_session() as rdp_client:
            await sandbox.computer(Action.CLICK, coordinates=[100, 100])
            await sandbox.computer(Action.TYPE, text="Hello World")
        """
        # 只支持 Windows 系统
        if self.os_type != SandboxOsType.WINDOWS.value:
            logger.warning("RDP session is only supported for Windows systems")
            yield None
            return

        rdp_client = None

        try:
            # 获取连接信息
            response = await self.sandbox_manager.describe_sandbox_terminal_url(self.id)
            result = response.get('Result', {})
            
            stream_url = result.get('Url')
            windows_key = result.get('WindowsKey', '')
            token = result.get('Token')
            console_url = result.get('ConsoleURL')
            
            if not stream_url or not windows_key:
                logger.error("Missing stream URL or Windows key for RDP connection")
                yield None
            else:
                # 创建 RDP 客户端
                rdp_client = RDPClient(
                    websocket_url=stream_url,
                    instance_id=self.id,
                    ip_address=self.ip_address,
                    password=windows_key,
                    username="ecs",
                    port=3389,
                    token=token,
                    console_url=console_url
                )
                
                # 建立连接
                if await rdp_client.connect():
                    logger.info("RDP session established successfully")
                    # wait tool server ready
                    time.sleep(1)
                    yield rdp_client
                else:
                    logger.error("Failed to establish RDP session")
                    yield None
        finally:
            # 清理连接
            if rdp_client and hasattr(rdp_client, 'connected') and rdp_client.connected:
                try:
                    await rdp_client.disconnect()
                    logger.info("RDP session closed")
                except Exception as cleanup_error:
                    logger.warning(f"Error during RDP cleanup: {cleanup_error}")

    async def computer(
        self,
        action: Action,
        coordinates: Optional[List[int]] = None,
        hold_keys: Optional[List[str]] = None,
        text: Optional[str] = None,
        button: Optional[str] = None,
        num_clicks: Optional[int] = 1,
        path: Optional[List[List[int]]] = None,
        delta_x: Optional[int] = None,
        delta_y: Optional[int] = None,
        keys: Optional[List[str]] = None,
        duration: Optional[Union[int, float]] = None,
        screenshot: bool = True,
        press: bool = False,
        release: bool = False,
        scroll_direction: Optional[Literal["up", "down", "left", "right"]] = None,
        scroll_amount: Optional[int] = None
    ) -> Optional[BaseResponse]:
        ts_client = self.tool_server_client
        args = ComputerActionArgs(
            action=action,
            coordinates=coordinates,
            hold_keys=hold_keys,
            text=text,
            button=button,
            num_clicks=num_clicks,
            path=path,
            delta_x=delta_x,
            delta_y=delta_y,
            keys=keys,
            duration=duration,
            screenshot=screenshot,
            press=press,
            release=release,
            scroll_direction=scroll_direction,
            scroll_amount=scroll_amount
        )
        return await ts_client.computer_action(args)

    def __repr__(self) -> str:
        return f"<Sandbox id='{self.id}' type='{self.details.os_type}' status='{self.details.status}' endpoint='{self.tool_server_endpoint}'>"