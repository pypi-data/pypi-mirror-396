from typing import Sequence
from google.generativeai import configure, GenerativeModel
from chain_nhem_nhem.llm.llm_driver import LLMDriver, ToolType
from chain_nhem_nhem.llm.registry import llm_driver_registry
from chain_nhem_nhem.core.messages import Message, LLMResponse
from chain_nhem_nhem.config import settings

class GeminiDriver(LLMDriver):
    def __init__(self, model_name: str | None = None):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not found. Please set it in the environment variables.")

        configure(api_key=api_key)

        self.model = GenerativeModel(
            model_name=model_name or settings.MODEL
        )

    # ----------------------------
    # Gemini message converter
    # ----------------------------
    def _convert_messages(self, messages: Sequence[Message]):
        return [
            {
                "role": msg.role,
                "parts": [{"text": msg.content}],
            }
            for msg in messages
        ]

    # ----------------------------
    # Main generate method
    # ----------------------------
    def generate(
        self,
        messages: Sequence[Message],
        tools: Sequence[ToolType] | None = None
    ) -> LLMResponse:

        gemini_messages = self._convert_messages(messages)

        response = self.model.generate_content(
            gemini_messages,
            tools=tools,
        )

        usage = response.usage_metadata
        tokens_used = usage.total_token_count if usage else None

        # Gemini always returns an array of candidates → content → parts
        part = response.candidates[0].content.parts[0]

        if getattr(part, "function_call", None):
            fc = part.function_call

            return LLMResponse(
                type="tool_call",
                tool_name=fc.name,
                tool_args=dict(fc.args),
                tokens_used=tokens_used
            )

        # If it's normal text
        return LLMResponse(
            type="message",
            content=part.text,
            tokens_used=tokens_used
        )

    # ----------------------------
    # Streaming (optional)
    # ----------------------------
    def stream(
        self,
        messages: Sequence[Message],
        tools: Sequence[ToolType] | None = None
    ):
        raise NotImplementedError("Gemini streaming not implemented.")

llm_driver_registry.register("gemini", GeminiDriver)