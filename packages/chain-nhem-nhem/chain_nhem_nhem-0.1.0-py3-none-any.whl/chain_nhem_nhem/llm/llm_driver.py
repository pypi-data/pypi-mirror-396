from abc import ABC, abstractmethod
from typing import Sequence, Dict, Any
from chain_nhem_nhem.core.messages import Message, LLMResponse

ToolType = Dict[str, Any]

class LLMDriver(ABC):
    @abstractmethod
    def generate(self, messages: Sequence[Message], tools: Sequence[ToolType] | None = None) -> LLMResponse:
        raise NotImplementedError

    def stream(self, messages: Sequence[Message], tools: Sequence[ToolType] | None = None) -> Any:
        raise NotImplementedError