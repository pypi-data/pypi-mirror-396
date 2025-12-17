from pydantic import BaseModel
from typing import Literal, Optional, Any


class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    name: Optional[str] = None  # útil para tool responses

class LLMResponse(BaseModel):
    type: Literal["message", "tool_call"]
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tokens_used: Optional[int] = None