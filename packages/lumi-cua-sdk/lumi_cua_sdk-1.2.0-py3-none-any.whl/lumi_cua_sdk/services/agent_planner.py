import httpx
import asyncio
import json
from typing import AsyncGenerator, Optional, Dict, Any, List
from ..models.agent_planner_models import AgentStreamMessage, ModelInfo, THINKING_DISABLED


class AgentPlannerClient:
    def __init__(self, endpoint: str, auth_token: str):
        self.endpoint = endpoint.rstrip('/')
        self.auth_token = auth_token
        self.timeout = 900

    async def run_task_stream(
        self,
        user_prompt: str,
        sandbox_id: str,
        model_name: str,
        user_system_prompt: str="",
        thinking_type: str=THINKING_DISABLED,
    ) -> AsyncGenerator[AgentStreamMessage, None]:
        """
        Calls the /run/task endpoint and yields AgentStreamMessage objects as they arrive.
        """
        url = f"{self.endpoint}/run/task"
        headers = {
            "Authorization": self.auth_token,
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        print(headers)
        payload = {
            "user_prompt": user_prompt,
            "sandbox_id": sandbox_id,
            "model_name": model_name,
            "system_prompt": user_system_prompt,
            "thinking_type": thinking_type
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[len("data:"):].strip()
                    if not data_str:
                        continue
                    try:
                        data = json.loads(data_str)
                        # If the server sends a dict directly matching AgentStreamMessage
                        msg = AgentStreamMessage(**data)
                        yield msg
                    except Exception as e:
                        # Optionally log or handle parse errors
                        continue

    async def list_models(self) -> List[ModelInfo]:
        """
        Calls the /models endpoint and returns the list of models as a list of ModelInfo objects.
        """
        url = f"{self.endpoint}/models"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers={"Authorization": self.auth_token})
            response.raise_for_status()
            data = response.json()
            return [ModelInfo(**item) for item in data.get("models", [])]
