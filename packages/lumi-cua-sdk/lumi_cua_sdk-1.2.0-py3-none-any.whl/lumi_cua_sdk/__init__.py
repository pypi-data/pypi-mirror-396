"""Lumi Computer Use Agent SDK"""

import logging

from .config import config
from .cua_client import LumiCuaClient, create_computer_use_agent
from .sandbox_client import Sandbox
from .models.common_models import (
    Action,
    ScreenshotResult,
    ComputerActionArgs,
    SandboxDetails,
    SandboxStatus,
    SandboxOsType,
    SandboxStreamDisplayType,
)
from .models.agent_planner_models import (
    THINKING_DISABLED,
    THINKING_ENABLED
)
from .services.sandbox_manager import SandboxManagerClient
from .services.sandbox_tool_server import ToolServerClient,AsyncToolServerClient

# Configure logging for the SDK
# Basic configuration, users can override this.
logger = logging.getLogger(__name__) # Use __name__ which will be 'lumi_cua_sdk'
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Set default logging level for the SDK. Can be configured by the user.
logger.setLevel(logging.INFO) 

__all__ = [
    "config",
    "LumiCuaClient",
    "Sandbox",
    "Action",
    "ScreenshotResult",
    "ComputerActionArgs",
    "SandboxDetails",
    "SandboxStatus",
    "SandboxManagerClient",
    "ToolServerClient",
    "AsyncToolServerClient",
    "THINKING_DISABLED",
    "THINKING_ENABLED",
    "SandboxOsType",
    "SandboxStreamDisplayType",
    "create_computer_use_agent",
    "logger"
]