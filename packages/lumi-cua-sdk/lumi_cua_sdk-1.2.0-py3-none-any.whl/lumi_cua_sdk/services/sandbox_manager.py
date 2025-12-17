import asyncio
import httpx
import time
import logging

from typing import List, Optional, Dict, Any, AsyncGenerator

from ..models.common_models import SandboxDetails, SandboxStatus

logger = logging.getLogger(__name__)


class SandboxManagerClient:
    def __init__(self, endpoint: str, auth_token: str):
        self.base_url = endpoint.rstrip("/")
        self.headers = {"Authorization": auth_token}
        self.timeout = 30  # seconds

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f'{self.base_url}{path}'
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                return response
            except httpx.HTTPStatusError as e:
                logger.error(f'HTTP error occurred: {e.response.status_code} - {e.response.text} for {method} {url}')
                raise
            except httpx.RequestError as e:
                logger.error(f'Request error occurred: {e} for {method} {url}')
                raise

    async def describe_sandboxes(self, sandbox_id: str = None) -> List[SandboxDetails]:
        """列出所有实例，最多返回指定数量的记录。"""
        params={"Action": "DescribeSandboxes", "Version": "2020-04-01"}
        response = await self._request('GET', '/', params={**params,"SandboxId": sandbox_id})
        sandboxes_data = response.json().get('Result', [])
        detailed_sandboxes = [SandboxDetails(**sandbox) for sandbox in sandboxes_data]
        return detailed_sandboxes

    async def create_sandbox(self, os_type: str = 'Linux', wait_for_ip: bool = True, wait_timeout: int = 300) -> SandboxDetails:
        """
        启动一个新实例 (默认为 Linux)。
        如果 wait_for_ip 为 True，则会等待直到实例分配了私网 IP。
        """
        payload = {"Action": "CreateSandbox", "Version": "2020-04-01", "OsType": os_type}
        response = await self._request('GET', '/', params={**payload})
        sandbox_data = response.json()
        sandbox_id = sandbox_data.get('Result', {}).get('SandboxId')

        if not sandbox_id:
            raise ValueError("Failed to start sandbox or get sandbox ID.")

        if wait_for_ip:
            logger.info(f"Sandbox {sandbox_id} started. Waiting for private IP...")
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    sandbox_details = await self.get_sandbox_details(sandbox_id)
                    if not sandbox_details.primary_ip or sandbox_details.status != SandboxStatus.RUNNING.value:
                        time.sleep(1) # Wait for 1 second
                        continue
                    return sandbox_details
                except Exception as e: 
                    logger.warning(f"Error getting sandbox details: {e}")
                if asyncio.get_event_loop().time() - start_time > wait_timeout:
                    raise TimeoutError(f"Timeout waiting for private IP for sandbox {sandbox_id}")
                await asyncio.sleep(5)  # Poll every 5 seconds
        else:
            return SandboxDetails(**sandbox_data)

    async def get_sandbox_details(self, sandbox_id: str) -> SandboxDetails:
        """获取特定实例的详细信息。"""
        response = await self.describe_sandboxes(sandbox_id)
        if len(response) == 0:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        return response[0]

    async def stop_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """停止一个实例。"""
        payload = {"Action": "StopSandbox", "Version": "2020-04-01", "SandboxId": sandbox_id}
        response = await self._request('GET', '/', params={**payload})
        return response.json()

    async def delete_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """删除一个实例。"""
        payload = {"Action": "DeleteSandbox", "Version": "2020-04-01", "SandboxId": sandbox_id}
        response = await self._request('GET', '/', params={**payload})
        return response.json()

    async def describe_sandbox_terminal_url(self, sandbox_id: str,) -> Dict[str, Any]:
        payload = {"Action": "DescribeSandboxTerminalUrl", "Version": "2020-04-01", "SandboxId": sandbox_id}
        response = await self._request('GET', '/', params={**payload})
        return response.json()
