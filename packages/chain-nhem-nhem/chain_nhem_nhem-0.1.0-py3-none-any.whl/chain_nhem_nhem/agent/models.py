from pydantic import BaseModel
from typing import List, Optional

class AgentResult(BaseModel):
    output: str
    steps: List[str]
    tools_used: List[str]
    tokens: Optional[int] = None
