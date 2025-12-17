import aiohttp
import requests
import os
import base64
from typing import Dict, Any, Literal
from ..models.common_models import Action, ComputerActionArgs
from ..models.tool_server_models import (
    MoveMouseRequest,
    ClickMouseRequest,
    PressMouseRequest,
    ReleaseMouseRequest,
    DragMouseRequest,
    ScrollRequest,
    PressKeyRequest,
    TypeTextRequest,
    WaitRequest,
    TakeScreenshotRequest,
    GetCursorPositionRequest,
    GetScreenSizeRequest,
    ChangePasswordRequest,
    BaseResponse,
    CursorPositionResponse,
    ScreenSizeResponse,
    ScreenshotResponse,
    ReadFileRequest,
    ReadFileResponse,
    ReadMultiFilesRequest,
    ReadMultiFilesResponse,
    ListDirectoryRequest,
    ListDirectoryResponse,
    SearchFileRequest,
    SearchFileResponse,
    SearchCodeResponse,
    GetFileInfoResponse,
    SearchCodeRequest,
    GetFileInfoRequest,
    CreateFileRequest,
    CreateFileResponse,
    ListSessionsRequest,
    ListSessionsResponse,
    ListProcessesRequest,
    ListProcessesResponse,
    ExecuteCommandRequest,
    ExecuteCommandResponse,
    FileOperationRequest,
    FileOperationResponse,
    StartVideoRecordingRequest,
    StopVideoRecordingRequest,
    StartVideoRecordingResponse,
    StopVideoRecordingResponse,
)


class ToolServerClient:
    """
    Client SDK for Sandbox Tool Server
    """

    def __init__(self, base_url: str = "http://localhost:8102", api_version: str = "2020-04-01", auth_key: str = ""):
        """
        Initialize the Sandbox SDK client

        Args:
            base_url: Base URL of the Sandbox Tool Server
            api_version: API version to use
        """
        self.base_url = base_url
        self.api_version = api_version
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if "proxy" in self.base_url:
            self.headers.update({"Authorization": auth_key})
        else:
            self.headers.update({"X-API-Key": auth_key})

    def _make_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Sandbox Tool Server

        Args:
            action: Action to perform
            params: Parameters for the action

        Returns:
            Response from the server
        """
        url = self.base_url
        response = requests.get(url, params={**params, "Version": self.api_version, "Action": action},
                                headers=self.headers, allow_redirects=False)
        response.raise_for_status()
        return response.json()

    def move_mouse(self, x: int, y: int) -> BaseResponse:
        """
        Move the mouse to the specified position

        Args:
            x: X position
            y: Y position

        Returns:
            Response from the server
        """
        request = MoveMouseRequest(PositionX=x, PositionY=y)
        response_data = self._make_request("MoveMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def click_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle", "double_click", "double_left",
            "Left", "Right", "Middle", "DoubleClick", "DoubleLeft"] = "left",
            press: bool = False,
            release: bool = False
    ) -> BaseResponse:
        """
        Click the mouse at the specified position

        Args:
            x: X position
            y: Y position
            button: Mouse button to click
            press: Whether to press the mouse button
            release: Whether to release the mouse button

        Returns:
            Response from the server
        """
        request = ClickMouseRequest(
            x=x,
            y=y,
            button=button,
            press=press,
            release=release
        )
        response_data = self._make_request(
            "ClickMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def press_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle",
            "Left", "Right", "Middle"] = "left"
    ) -> BaseResponse:
        """
        Press the mouse button at the specified position

        Args:
            x: X position
            y: Y position
            button: Mouse button to press

        Returns:
            Response from the server
        """
        request = PressMouseRequest(
            x=x,
            y=y,
            button=button
        )
        response_data = self._make_request(
            "PressMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def release_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle",
            "Left", "Right", "Middle"] = "left"
    ) -> BaseResponse:
        """
        Release the mouse button at the specified position

        Args:
            x: X position
            y: Y position
            button: Mouse button to release

        Returns:
            Response from the server
        """
        request = ReleaseMouseRequest(
            x=x,
            y=y,
            button=button
        )
        response_data = self._make_request(
            "ReleaseMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def drag_mouse(
            self,
            source_x: int,
            source_y: int,
            target_x: int,
            target_y: int
    ) -> BaseResponse:
        """
        Drag the mouse from source to target position

        Args:
            source_x: Source X position
            source_y: Source Y position
            target_x: Target X position
            target_y: Target Y position

        Returns:
            Response from the server
        """
        request = DragMouseRequest(
            source_x=source_x,
            source_y=source_y,
            target_x=target_x,
            target_y=target_y
        )
        response_data = self._make_request(
            "DragMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def scroll(
            self,
            x: int,
            y: int,
            scroll_direction: Literal["up", "down", "left", "right"] = "up",
            scroll_amount: int = 1
    ) -> BaseResponse:
        """
        Scroll at the specified position

        Args:
            x: X position
            y: Y position
            scroll_direction: Direction to scroll
            scroll_amount: Amount to scroll

        Returns:
            Response from the server
        """
        request = ScrollRequest(
            x=x,
            y=y,
            scroll_direction=scroll_direction,
            scroll_amount=scroll_amount
        )
        response_data = self._make_request(
            "Scroll", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def press_key(self, key: str) -> BaseResponse:
        """
        Press the specified key

        Args:
            key: Key to press

        Returns:
            Response from the server
        """
        request = PressKeyRequest(key=key)
        response_data = self._make_request(
            "PressKey", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def type_text(self, text: str) -> BaseResponse:
        """
        Type the specified text

        Args:
            text: Text to type

        Returns:
            Response from the server
        """
        request = TypeTextRequest(text=text)
        response_data = self._make_request(
            "TypeText", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def wait(self, duration: int) -> BaseResponse:
        """
        Wait for the specified duration in milliseconds

        Args:
            duration: Duration to wait in milliseconds

        Returns:
            Response from the server
        """
        request = WaitRequest(duration=duration)
        response_data = self._make_request(
            "Wait", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def take_screenshot(self) -> ScreenshotResponse:
        """
        Take a screenshot

        Returns:
            Response from the server with screenshot data
        """
        request = TakeScreenshotRequest()
        response_data = self._make_request(
            "TakeScreenshot", request.model_dump(by_alias=True))
        return ScreenshotResponse(**response_data)

    def get_cursor_position(self) -> CursorPositionResponse:
        """
        Get the current cursor position

        Returns:
            Response containing cursor position in Result.x and Result.y
        """
        request = GetCursorPositionRequest()
        response_data = self._make_request(
            "GetCursorPosition", request.model_dump(by_alias=True))
        return CursorPositionResponse(**response_data)

    def get_screen_size(self) -> ScreenSizeResponse:
        """
        Get the screen size

        Returns:
            Response containing screen size in Result.width and Result.height
        """
        request = GetScreenSizeRequest()
        response_data = self._make_request(
            "GetScreenSize", request.model_dump(by_alias=True))
        print(response_data)
        return ScreenSizeResponse(**response_data)

    def change_password(self, username: str, new_password: str) -> BaseResponse:
        """
        Change the password for the specified user

        Args:
            username: Username
            new_password: New password

        Returns:
            Response from the server
        """
        request = ChangePasswordRequest(
            username=username,
            new_password=new_password
        )
        response_data = self._make_request(
            "ChangePassword", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def computer_action(self, action: ComputerActionArgs, **kwargs) -> BaseResponse:
        """
        Perform a computer action
        Args:
            action: Action to perform
            **kwargs: Additional arguments for the action
        Returns:
            Response from the server
        """
        if action.action == Action.MOVE_MOUSE:
            return self.move_mouse(action.coordinates[0], action.coordinates[1])
        elif action.action == Action.CLICK_MOUSE:
            return self.click_mouse(action.coordinates[0], action.coordinates[1], action.button, action.press, action.release)
        elif action.action == Action.PRESS_KEY:
            return self.press_key(action.keys[0] if len(action.keys) == 1 else " ".join(action.keys))
        elif action.action == Action.TYPE_TEXT:
            return self.type_text(action.text)
        elif action.action == Action.WAIT:
            return self.wait(action.duration)
        elif action.action == Action.TAKE_SCREENSHOT:
            return self.take_screenshot()
        elif action.action == Action.SCROLL:
            return self.scroll(action.coordinates[0], action.coordinates[1], action.scroll_direction, action.scroll_amount)
        elif action.action == Action.DRAG_MOUSE:
            return self.drag_mouse(action.coordinates[0], action.coordinates[1], action.coordinates[2], action.coordinates[3])
        return BaseResponse()

    def file_operation(self, **params) -> FileOperationResponse:
        """
        Execute a file operation
        Args:
            **params: Parameters for the file operation
        Returns:
            Response from the server
        """
        params = FileOperationRequest.model_validate(
            params).encde_content().model_dump(by_alias=True, exclude_unset=True)
        response_data = self._make_request("FileOperation", params)
        return FileOperationResponse(**response_data).decode_content()

    def start_video_recording(
            self,
            quality: str = "",
            format: str = "",
            resolution: str = "",
            framerate: int = 0,
            max_duration: int = 0
    ) -> StartVideoRecordingResponse:
        """
        Start video recording

        Args:
            quality: Recording quality: low/medium/high/custom, empty means medium
            format: Recording format: mp4/avi/mkv, empty means mp4
            resolution: Custom resolution, e.g., '1920x1080', only valid when quality=custom
            framerate: Custom framerate, only valid when quality=custom
            max_duration: Max recording duration (seconds), 0 means use default value

        Returns:
            Response from the server
        """
        request = StartVideoRecordingRequest(
            Quality=quality,
            Format=format,
            Resolution=resolution,
            Framerate=framerate,
            MaxDuration=max_duration
        )
        response_data = self._make_request(
            "StartVideoRecording", request.model_dump(by_alias=True))
        return StartVideoRecordingResponse(**response_data)

    def stop_video_recording(self) -> StopVideoRecordingResponse:
        """
        Stop video recording

        Returns:
            Response from the server with recording file information
        """
        request = StopVideoRecordingRequest()
        response_data = self._make_request(
            "StopVideoRecording", request.model_dump(by_alias=True))
        return StopVideoRecordingResponse(**response_data)


class AsyncToolServerClient:
    """
    Asynchronous version of Sandbox Tool Server Client SDK
    """

    def __init__(self, base_url: str = "http://localhost:8102", api_version: str = "2020-04-01", auth_key: str = "", sandbox_id: str = ""):
        """
        Initialize the asynchronous Sandbox SDK client

        Args:
            base_url: Base URL of the Sandbox Tool Server
            api_version: API version to use
            auth_key: Authentication key
        """
        self.base_url = base_url
        self.api_version = api_version
        self.sandbox_id = sandbox_id
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if "proxy" in self.base_url:
            self.headers.update({"Authorization": auth_key})
        else:
            self.headers.update({"X-API-Key": auth_key})

        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _make_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an asynchronous request to the Sandbox Tool Server

        Args:
            action: Action to perform
            params: Parameters for the action

        Returns:
            Response from the server
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = self.base_url
        # Convert all parameters to strings

        str_params = {
            k: str(v.value).lower() if hasattr(v, 'value') else str(v).lower() if isinstance(v, bool) else str(v)
            for k, v in params.items()
        }
        str_params.update({
            "Version": self.api_version,
            "Action": action
        })

        if self.sandbox_id:
            str_params.update({
                "SandboxId": self.sandbox_id,
            })

        async with self._session.get(
                url,
                params=str_params,
                headers=self.headers,
                allow_redirects=False
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def move_mouse(self, x: int, y: int) -> BaseResponse:
        """Move the mouse to the specified position"""
        request = MoveMouseRequest(PositionX=x, PositionY=y)
        response_data = await self._make_request("MoveMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def click_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle", "double_click", "double_left",
            "Left", "Right", "Middle", "DoubleClick", "DoubleLeft"] = "left",
            press: bool = False,
            release: bool = False
    ) -> BaseResponse:
        """Click the mouse at the specified position"""
        request = ClickMouseRequest(
            x=x,
            y=y,
            button=button,
            press=press,
            release=release
        )
        response_data = await self._make_request("ClickMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def press_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle",
            "Left", "Right", "Middle"] = "left"
    ) -> BaseResponse:
        """Press the mouse button at the specified position"""
        request = PressMouseRequest(
            x=x,
            y=y,
            button=button
        )
        response_data = await self._make_request("PressMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def release_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle",
            "Left", "Right", "Middle"] = "left"
    ) -> BaseResponse:
        """Release the mouse button at the specified position"""
        request = ReleaseMouseRequest(
            x=x,
            y=y,
            button=button
        )
        response_data = await self._make_request("ReleaseMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def drag_mouse(
            self,
            source_x: int,
            source_y: int,
            target_x: int,
            target_y: int
    ) -> BaseResponse:
        """Drag the mouse from source to target position"""
        request = DragMouseRequest(
            source_x=source_x,
            source_y=source_y,
            target_x=target_x,
            target_y=target_y
        )
        response_data = await self._make_request("DragMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def scroll(
            self,
            x: int,
            y: int,
            scroll_direction: Literal["up", "down", "left", "right",
            "Up", "Down", "Left", "Right"] = "up",
            scroll_amount: int = 1
    ) -> BaseResponse:
        """Scroll at the specified position"""
        request = ScrollRequest(
            x=x,
            y=y,
            scroll_direction=scroll_direction,
            scroll_amount=scroll_amount
        )
        response_data = await self._make_request("Scroll", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def press_key(self, key: str) -> BaseResponse:
        """Press the specified key"""
        request = PressKeyRequest(key=key)
        response_data = await self._make_request("PressKey", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def type_text(self, text: str) -> BaseResponse:
        """Type the specified text"""
        request = TypeTextRequest(text=text)
        response_data = await self._make_request("TypeText", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def wait(self, duration: int) -> BaseResponse:
        """Wait for the specified duration in milliseconds"""
        request = WaitRequest(duration=duration)
        response_data = await self._make_request("Wait", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def take_screenshot(self) -> ScreenshotResponse:
        """Take a screenshot"""
        request = TakeScreenshotRequest()
        response_data = await self._make_request("TakeScreenshot", request.model_dump(by_alias=True))
        return ScreenshotResponse(**response_data)

    async def get_cursor_position(self) -> CursorPositionResponse:
        """Get the current cursor position"""
        request = GetCursorPositionRequest()
        response_data = await self._make_request("GetCursorPosition", request.model_dump(by_alias=True))
        return CursorPositionResponse(**response_data)

    async def get_screen_size(self) -> ScreenSizeResponse:
        """Get the screen size"""
        request = GetScreenSizeRequest()
        response_data = await self._make_request("GetScreenSize", request.model_dump(by_alias=True))
        return ScreenSizeResponse(**response_data)

    async def change_password(self, username: str, new_password: str) -> BaseResponse:
        """Change the password for the specified user"""
        request = ChangePasswordRequest(
            username=username,
            new_password=new_password
        )
        response_data = await self._make_request("ChangePassword", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def computer_action(self, action: ComputerActionArgs, **kwargs) -> BaseResponse:
        """
        Perform a computer action
        Args:
            action: Action to perform
            **kwargs: Additional arguments for the action
        Returns:
            Response from the server
        """
        if action.action == Action.MOVE_MOUSE:
            return await self.move_mouse(action.coordinates[0], action.coordinates[1])
        elif action.action == Action.CLICK_MOUSE:
            return await self.click_mouse(action.coordinates[0], action.coordinates[1], action.button, action.press, action.release)
        elif action.action == Action.PRESS_KEY:
            return await self.press_key(action.keys[0] if len(action.keys) == 1 else " ".join(action.keys))
        elif action.action == Action.TYPE_TEXT:
            return await self.type_text(action.text)
        elif action.action == Action.WAIT:
            return await self.wait(action.duration)
        elif action.action == Action.TAKE_SCREENSHOT:
            return await self.take_screenshot()
        elif action.action == Action.SCROLL:
            return await self.scroll(action.coordinates[0], action.coordinates[1], action.scroll_direction, action.scroll_amount)
        elif action.action == Action.DRAG_MOUSE:
            return await self.drag_mouse(action.coordinates[0], action.coordinates[1], action.coordinates[2], action.coordinates[3])
        return BaseResponse()

    async def file_operation(self, **params) -> FileOperationResponse:
        """
        Execute a file operation
        Args:
            **params: Parameters for the file operation
        Returns:
            Response from the server
        """
        response_data = await self._make_request("FileOperation", params)
        return FileOperationResponse(**response_data).decode_content()

def new_tool_server_client(endpoint: str, auth_key: str = "") -> ToolServerClient:
    """Create a new Sandbox Tool Server client instance"""
    return ToolServerClient(base_url=endpoint, auth_key=auth_key)


async def new_async_tool_server_client(endpoint: str, auth_key: str = "") -> AsyncToolServerClient:
    """Create a new asynchronous Sandbox Tool Server client instance"""
    client = AsyncToolServerClient(base_url=endpoint, auth_key=auth_key, sandbox_id=None)
    await client.__aenter__()
    return client