from enum import Enum
from typing import List, Union, Optional, Tuple, Any, Dict, Literal
from pydantic import BaseModel, Field

class Action(Enum):
    # Computer Actions
    MOVE_MOUSE = "move_mouse"  #鼠标移动
    CLICK_MOUSE = "click_mouse" #鼠标点击
    DRAG_MOUSE = "drag_mouse" #鼠标拖拽
    TYPE_TEXT = "type_text" #键盘输入
    PRESS_KEY = "press_key" #按下键盘按键，可以是组合键，也可以是单个按键
    SCROLL = "scroll" #鼠标滚轮
    WAIT = "wait" #等待
    TAKE_SCREENSHOT = "take_screenshot" #获取屏幕截图

class FileAction(Enum):
    READ_FILE = "read" # 读取文件
    WRITE_FILE = "write" # 写入文件
    APPEND_FILE = "append" # 追加文件内容
    FILE_EXISTS = "exists" # 判断文件或目录是否存在
    LIST_FILES = "list" # 列出目录内容
    MKDIR = "mkdir" # 创建目录
    RMDIR = "rmdir" # 删除空目录
    DELETE_FILE_OR_DIR = "delete" # 删除文件或目录（可递归）
    MOVE_FILE_OR_DIR = "move" # 移动或重命名文件/目录
    COPY_FILE_OR_DIR = "copy" # 复制文件或目录
    CREATE_FILE = "create" # 创建新文件并写入内容

class ScreenshotResult(BaseModel):
    base_64_image: str
    width: Optional[int] = None
    height: Optional[int] = None

class ComputerActionArgs(BaseModel):
    action: Action
    coordinates: Optional[List[int]] = None # For move, click, scroll
    hold_keys: Optional[List[str]] = None # For move_mouse
    text: Optional[str] = None # For type_text
    button: Optional[str] = None # For click_mouse (left, right, middle, double_left)
    num_clicks: Optional[int] = 1 # For click_mouse
    path: Optional[List[List[int]]] = None # For drag_mouse
    delta_x: Optional[int] = None # For scroll
    delta_y: Optional[int] = None # For scroll
    keys: Optional[List[str]] = None # For press_key
    duration: Optional[Union[int, float]] = None # For press_key (hold duration), wait
    screenshot: bool = True # Whether to return a screenshot after the action
    press: bool = False # For click_mouse
    release: bool = False # For click_mouse
    scroll_direction: Optional[Literal["up", "down", "left", "right"]] = None # For scroll
    scroll_amount: Optional[int] = None # For scroll

class SandboxStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STARTING = "STARTING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"

class SandboxOsType(str, Enum):
    LINUX = "Linux"
    WINDOWS = "Windows"

class SandboxStreamDisplayType(str, Enum):
    VNC = "VNC"
    GUACAMOLE = "GUACAMOLE"

class SandboxDetails(BaseModel):
    id: str = Field(description="The ID of the sandbox",alias="SandboxId")
    primary_ip: str = Field(default=None, description="The primary IP address of the sandbox",alias="PrimaryIp")
    status: str = Field(description="The status of the sandbox",alias="Status")
    os_type: str = Field(description="The operating system type of the sandbox",alias="OsType")
    instance_type_id: str = Field(description="The instance type ID of the sandbox",alias="InstanceTypeId")
    tool_server_endpoint: str = Field(default=None, description="The tool server endpoint of the sandbox", alias="ToolServerEndpoint")
    tool_server_proxy_uri: str = Field(default=None, description="The tool server proxy uri from ecs manager", alias="ToolServerProxyUri")