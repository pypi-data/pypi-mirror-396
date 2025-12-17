from typing import Optional
from pydantic import BaseModel, Field

THINKING_ENABLED = 'enabled'
THINKING_DISABLED = 'disabled'

class AgentRunRequest(BaseModel):
    """Request model for agent runnint a task prompt"""
    query: str = Field("", description="task prompt")
    sandbox_id: str = Field("0", description="sandbox id")
    sandbox_endpoint: str = Field("0", description="sandbox tool server endpoint")


class AgentStreamMessage(BaseModel):
    """Represents a single message/event streamed from the agent's run method."""
    summary: Optional[str] = Field("", description="A summary of the current step or observation.")
    action: Optional[str] = Field("", description="The specific action taken or proposed by the agent.")
    screenshot: Optional[str] = Field(None, description="A base64 encoded screenshot relevant to the current step, if available.")
    task_id: Optional[str] = Field(None, description="Task ID")
    total_tokens: Optional[int] = Field(None, description="Number of tokens consumed")


class AgentStreamResponse(BaseModel):
    data: AgentStreamMessage = Field(None, description="The response from the agent.")


class ModelInfo(BaseModel):
    name: str = Field("", description="Model name, e.g doubao-1.5-ui-tars-250328, used in run_task method")
    display_name: str = Field("", description="Model display name, e.g Doubao 1.5 UI Tars")
    is_thinking: bool = Field(False, description="Whether the model supports thinking")
