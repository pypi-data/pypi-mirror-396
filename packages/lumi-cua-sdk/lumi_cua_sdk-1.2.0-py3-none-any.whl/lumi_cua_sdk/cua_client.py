import json
import logging
import time

from typing import List, Optional, AsyncGenerator

from .sandbox_client import Sandbox
from .services.sandbox_manager import SandboxManagerClient
from .services.agent_planner import AgentPlannerClient

from .models.common_models import SandboxOsType
from .models.agent_planner_models import AgentStreamMessage, ModelInfo, THINKING_DISABLED

from .config import get_config

logger = logging.getLogger(__name__)


class LumiCuaClient:
    """Client for interacting with the Lumi Computer Use Agent services."""

    def __init__(self, sandbox_manager_url: str=None, agent_planner_url: str=None, auth_token: str=None):
        """
        Initializes the LumiCuaClient.

        Args:
            sandbox_manager_url: The endpoint for the Sandbox Manager service.
            agent_planner_url: The endpoint for the Agent Planner service.
            auth_token: Optional API key for authenticating with backend services.
        """
        _config = get_config()
        self.auth_token = auth_token or _config.auth_token
        self.sandbox_manager_url = sandbox_manager_url or _config.sandbox_manager_url
        self.agent_planner_url = agent_planner_url or _config.agent_planner_url

        self.sandbox_manager = SandboxManagerClient(endpoint=self.sandbox_manager_url, auth_token=self.auth_token)
        self.agent_planner = AgentPlannerClient(endpoint=self.agent_planner_url, auth_token=self.auth_token)
        logger.info(f"LumiCuaClient initialized. Sandbox Manager: {self.sandbox_manager_url}, Agent Planner: {self.agent_planner_url}")

    async def list_sandboxes(self) -> List[Sandbox]:
        """
        Lists available CUA sandboxes by calling the ECS manager.

        Returns:
            A list of Sandbox objects.
        """
        logger.info("Listing sandboxes via ECS manager.")
        sandboxes_detail_list = await self.sandbox_manager.describe_sandboxes()
        return [Sandbox(details=details, auth_token=self.auth_token, sandbox_manager_url=self.sandbox_manager_url)
                for details in sandboxes_detail_list]

    async def start_linux(self, wait_for_ip: bool = True, wait_timeout: int = 300) -> Sandbox:
        """
        Starts a new Linux CUA sandbox using the ECS manager.

        Args:
            wait_for_ip: If True, waits until the sandbox has a private IP.
            wait_timeout: Timeout in seconds for waiting for the IP.

        Returns:
            An Sandbox object representing the started Linux sandbox.
        """
        logger.info(f"Attempting to start a Linux sandbox (wait_for_ip={wait_for_ip}).")
        sandbox_details = await self.sandbox_manager.create_sandbox(
            os_type=SandboxOsType.LINUX.value,
            wait_for_ip=wait_for_ip,
            wait_timeout=wait_timeout
        )
        logger.info(f"Linux sandbox started via ECS manager: id={sandbox_details.id}, ip={sandbox_details.primary_ip}")
        return Sandbox(details=sandbox_details, auth_token=self.auth_token, sandbox_manager_url=self.sandbox_manager_url)

    async def start_windows(self, wait_for_ip: bool = True, wait_timeout: int = 300) -> Sandbox:
        """
        Starts a new Windows CUA sandbox using the ECS manager.

        Args:
            wait_for_ip: If True, waits until the sandbox has a private IP.
            wait_timeout: Timeout in seconds for waiting for the IP.

        Returns:
            An Sandbox object representing the started Windows sandbox.
        """
        logger.info(f"Attempting to start a Windows sandbox (wait_for_ip={wait_for_ip}).")
        sandbox_details = await self.sandbox_manager.create_sandbox(
            os_type=SandboxOsType.WINDOWS.value,
            wait_for_ip=wait_for_ip,
            wait_timeout=wait_timeout
        )
        # sleep 1min waiting for os became ready
        time.sleep(70)
        logger.info(f"Windows sandbox started via ECS manager: id={sandbox_details.id}, ip={sandbox_details.primary_ip}")
        return Sandbox(details=sandbox_details, auth_token=self.auth_token, sandbox_manager_url=self.sandbox_manager_url)

    async def list_models(self) -> List[ModelInfo]:
        result = await self.agent_planner.list_models()
        return result

    async def run_task(
        self,
        user_prompt: str,
        sandbox_id: str,
        model_name: str,
        user_system_prompt: str = "",
        thinking_type: str = THINKING_DISABLED
    ) -> AsyncGenerator[AgentStreamMessage, None]:
        """
        Run a task using the agent planner and yield AgentStreamMessage objects.
        """
        async for msg in self.agent_planner.run_task_stream(
            user_prompt=user_prompt,
            sandbox_id=sandbox_id,
            model_name=model_name,
            user_system_prompt=user_system_prompt,
            thinking_type=thinking_type
        ):
            yield msg


def create_computer_use_agent(
    sandbox_manager_url: str=None, agent_planner_url: str=None, auth_token: str=None
) -> LumiCuaClient:
    """
    Factory function to create and initialize a ComputerUseAgent instance.

    Args:
        sandbox_manager_url: URL for the ECS Manager.
        agent_planner_url:  URL for the Agent Planner
        auth_token: Authentication token for computer use environment's ECS Manager Server.

    Returns:
        An uninitialized ComputerUseAgent instance.
    """
    client = LumiCuaClient(sandbox_manager_url=sandbox_manager_url, agent_planner_url=agent_planner_url,
                           auth_token=auth_token)
    return client
