from typing import Protocol

from app.ai.clients.openai_client import LLMConfigurationError, OpenAIClient
from app.ai.clients.qwen_client import QwenClient
from app.core.config import settings


class LLMClient(Protocol):
    provider: str
    model_name: str

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        ...


class LLMFactory:
    """Create the configured LLM client without leaking provider logic into services."""

    @staticmethod
    def create(provider: str | None = None) -> LLMClient:
        selected_provider = (provider or settings.ai_provider or "openai").strip().lower()
        if selected_provider == "openai":
            return OpenAIClient()
        if selected_provider == "qwen":
            return QwenClient()
        raise LLMConfigurationError(
            f"Unsupported AI_PROVIDER: {selected_provider}. Supported providers: openai, qwen"
        )
