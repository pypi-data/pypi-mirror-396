from abc import ABC, abstractmethod
from pydantic import BaseModel
from chain_nhem_nhem.helpers.gemini_helper import GeminiHelper

class Tool(ABC):
    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    def __call__(self, args: BaseModel) -> dict:
        pass

    def to_gemini_tool(self):
        return {
            "function_declarations": [
                {
                    "name": self.name,
                    "description": self.description,
                    "parameters": GeminiHelper.strip_schema(self.args_schema.model_json_schema())
                }
            ]
        }
