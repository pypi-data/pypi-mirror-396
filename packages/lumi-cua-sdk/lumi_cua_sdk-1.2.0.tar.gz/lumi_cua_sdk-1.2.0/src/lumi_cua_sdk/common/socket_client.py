import asyncio
import websockets
import json
from typing import Optional
import logging
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RDPClient:
    def __init__(self, websocket_url: str, instance_id: str, ip_address: str,
                 password: str, username: str = "ecs", port: int = 3389,
                 token: Optional[str] = None, console_url: Optional[str] = None):
        """
        初始化RDP客户端

        Args:
            websocket_url: WebSocket服务器URL
            instance_id: 实例ID
            ip_address: 服务器IP地址
            password: 密码
            username: 用户名，默认为"ecs"
            port: RDP端口，默认为3389
            token: Token
            console_url: 控制台URL
        """
        self.websocket_url = websocket_url
        self.instance_id = instance_id
        self.ip_address = ip_address
        self.password = password
        self.username = username
        self.port = port
        self.websocket = None
        self.connected = False
        self._message_task = None
        self.token = token
        self.console_url = console_url or websocket_url

    async def connect(self):
        """连接到WebSocket服务器并建立RDP连接"""
        return await self._perform_rdp_login()

    async def _perform_rdp_login(self) -> bool:
        """执行RDP登录，参考前端实现"""
        try:
            logger.debug(f"Starting RDP login to: {self.websocket_url}")
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect to WebSocket with proper keep-alive settings and SSL bypass
            self.websocket = await websockets.connect(
                self.websocket_url, 
                ping_interval=20,
                ping_timeout=30,
                close_timeout=30,
                max_size=None,
                compression=None,
                ssl=ssl_context
            )
            logger.debug("WebSocket connection established for RDP login")
            
            # Prepare login instruction based on frontend implementation (app.dev.js line 14690)
            # Default screen size - can be made configurable if needed
            screen_width = 1920
            screen_height = 1080
            
            # Build login payload aligned with frontend
            login_instruction = {
                # Required by backend / frontend
                "ConsoleURL": self.console_url,
                "InstanceId": self.instance_id,
                "Ip": self.ip_address,
                "Password": self.password,
                "UserName": self.username,
                # Additional fields kept for compatibility
                "AuthType": "password",
                "NetworkType": "vpc",
                "Protocol": "rdp",
                "Port": self.port,
                "ScreenWidth": str(screen_width),
                "ScreenHeight": str(screen_height),
                "ConnectToNewSession": "1",
            }
            # Include Token if available
            if self.token:
                login_instruction["Token"] = self.token

            # Send login instruction
            await self.websocket.send(json.dumps(login_instruction))
            logger.debug(f"RDP login instruction sent: {login_instruction}")
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                logger.debug(f"RDP login response: {response}")
                
                # Check if this is Guacamole protocol response
                if self._is_guacamole_protocol_response(response):
                    logger.debug("Received Guacamole protocol response, waiting for RDP authentication...")

                    # 等待更多响应来确认RDP登录状态
                    login_success = await self._wait_for_rdp_authentication()
                    if login_success:
                        logger.debug("RDP authentication successful")
                        self.connected = True
                        # 启动消息处理任务来保持连接活跃
                        self._message_task = asyncio.create_task(self._handle_messages())
                        return True
                    else:
                        logger.error("RDP authentication failed")
                        return False
                else:
                    logger.warning(f"Received unexpected non-JSON response: {response[:100]}...")
                    return False
                    
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for RDP login response")
                return False

        except Exception as e:
            logger.error(f"RDP login failed with exception: {str(e)}")
            return False
    
    async def _wait_for_rdp_authentication(self) -> bool:
        """
        等待RDP认证完成的确认
        在收到初始Guacamole协议响应后，需要等待更多消息来确认RDP登录状态
        """
        try:
            # 等待更多消息来确认认证状态
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                    logger.debug(f"Authentication check {attempt + 1}: {response[:100]}...")
                    
                    # 检查是否包含认证失败的错误信息
                    if self._check_authentication_failure(response):
                        logger.error("RDP authentication failed - invalid credentials or connection error")
                        return False
                    
                    # 检查是否包含成功的屏幕内容（表示已成功连接到桌面）
                    if self._check_desktop_ready(response):
                        logger.debug("Desktop session ready - RDP authentication successful")
                        return True
                    
                    # 如果是正常的协议消息，继续等待
                    if self._is_guacamole_protocol_response(response):
                        continue
                    
                except asyncio.TimeoutError:
                    logger.debug(f"Timeout on authentication check {attempt + 1}")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.error("WebSocket connection closed during authentication")
                    return False
            
            # 如果没有明确的失败信号，假设认证成功
            logger.debug("No authentication failure detected, assuming success")
            return True
            
        except Exception as e:
            logger.error(f"Error during authentication check: {e}")
            return False

    @staticmethod
    def _check_authentication_failure(response: str) -> bool:
        """
        检查响应中是否包含认证失败的信号
        """
        failure_indicators = [
            'authentication failed',
            'login failed', 
            'invalid credentials',
            'access denied',
            'connection refused',
            'error',
            'Error',
            'FAILED',
            'failed'
        ]
        
        response_lower = response.lower()
        for indicator in failure_indicators:
            if indicator.lower() in response_lower:
                return True
        return False
    
    @staticmethod
    def _check_desktop_ready(response: str) -> bool:
        """
        检查是否收到了桌面就绪的信号
        通常表现为包含较大的屏幕图像数据
        """
        try:
            # 检查是否包含大量的图像数据（表示桌面屏幕）
            if 'blob' in response and len(response) > 1000:
                # 检查是否包含PNG图像数据
                if 'iVBORw0KGgo' in response:  # PNG header in base64
                    return True
            
            # 检查是否包含桌面相关的Guacamole指令
            desktop_indicators = ['.cursor,', '.display,', '.desktop,']
            for indicator in desktop_indicators:
                if indicator in response:
                    return True
                    
            return False
        except Exception:
            return False
    
    async def _handle_messages(self):
        """
        后台任务：持续处理来自WebSocket的消息，保持连接活跃
        这对于维持RDP会话至关重要
        """
        logger.debug("Starting WebSocket message handling task")
        try:
            while self.connected and self.websocket:
                try:
                    # 使用无限超时，依赖WebSocket内置的ping/pong机制
                    message = await self.websocket.recv()
                    
                    # 处理Guacamole协议消息
                    if self._is_guacamole_protocol_response(message):
                        logger.debug(f"Received Guacamole protocol message: {message}...")
                    else:
                        logger.debug(f"Received other message: {message}...")

                    await self._handle_guacamole_messages(message)

                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"WebSocket connection closed by server: {e}")
                    self.connected = False
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    # 检查连接是否仍然有效
                    if self.websocket and self.websocket.closed:
                        logger.warning("WebSocket connection is closed, stopping message handler")
                        self.connected = False
                        break
                    continue
                    
        except asyncio.CancelledError:
            logger.debug("Message handling task was cancelled")
            raise
        except Exception as e:
            logger.debug(f"Message handling task failed: {e}")
        finally:
            logger.debug("Message handling task ended")

    async def _handle_guacamole_messages(self, message):
        """处理Guacamole协议sync、ping消息并响应，避免连接断开"""
        try:
            # 解析指令
            parts = message.strip().split(',')
            if not parts:
                return

            instruction = parts[0]

            # 处理必须响应的指令
            if instruction.startswith('4.sync'):
                # 响应sync指令
                timestamp = parts[1].rstrip(';')
                response = f"4.sync,{timestamp};"
                await self.websocket.send(response)
                logger.debug("Responded to sync instruction")

            elif instruction.startswith('3.ping'):
                # 响应ping指令
                timestamp = parts[1].rstrip(';')
                response = f"3.pong,{timestamp};"
                await self.websocket.send(response)
                logger.debug("Responded to ping instruction")

        except Exception as e:
            logger.error(f"Error handling messages: {e}")

    def _is_guacamole_protocol_response(self, response: str) -> bool:
        """
        检查响应是否为Guacamole协议格式
        Guacamole协议格式: length.instruction,param1,param2,...;
        例如: 5.audio,1.1,31.audio/L16;rate=44100,channels=2;
        """
        try:
            # Guacamole协议特征:
            # 1. 包含数字.指令格式
            # 2. 常见指令: audio, size, img, blob, cursor, end
            # 3. 以分号结尾
            
            guacamole_instructions = ['audio', 'size', 'img', 'blob', 'cursor', 'end', 'ready', 'error']
            
            # 检查是否包含Guacamole协议的典型指令
            for instruction in guacamole_instructions:
                # 格式: 数字.指令名
                pattern = f".{instruction},"
                if pattern in response:
                    logger.debug(f"Found Guacamole instruction: {instruction}")
                    return True
            
            # 检查是否包含图像数据 (base64编码的PNG)
            if 'iVBORw0KGgo' in response:  # PNG文件头的base64编码
                logger.debug("Found PNG image data in response")
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error checking Guacamole protocol: {e}")
            return False

    async def disconnect(self):
        """断开连接"""
        logger.debug("Starting RDP client disconnect")
        self.connected = False
        
        # 取消消息处理任务
        if self._message_task and not self._message_task.done():
            logger.debug("Cancelling message handling task")
            self._message_task.cancel()
            try:
                await asyncio.wait_for(self._message_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            logger.debug("Message handling task cancelled")
        
        # 关闭WebSocket连接
        if self.websocket:
            try:
                logger.debug("Closing WebSocket connection")
                await self.websocket.close()
                logger.debug("WebSocket closed")
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
        else:
            logger.debug("WebSocket already closed or None")
            self.websocket = None

