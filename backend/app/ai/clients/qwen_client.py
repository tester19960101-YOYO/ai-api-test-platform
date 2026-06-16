import json
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, BadRequestError, OpenAI

from app.ai.clients.openai_client import LLMConfigurationError, LLMResponseError
from app.core.config import settings


OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
QWEN_DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_DEFAULT_MODEL = "qwen-max-latest"


class QwenClient:
    """DashScope compatible-mode client with strict JSON post-validation."""

    provider = "qwen"

    def __init__(
        self,
        api_base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout: int | None = None,
    ) -> None:
        configured_base_url = (api_base_url if api_base_url is not None else settings.ai_api_base_url).strip()
        if not configured_base_url or configured_base_url == OPENAI_DEFAULT_BASE_URL:
            configured_base_url = QWEN_DEFAULT_BASE_URL
        self.api_base_url = configured_base_url
        self.api_key = (api_key if api_key is not None else settings.ai_api_key).strip()
        configured_model = (model_name if model_name is not None else settings.ai_model_name).strip()
        if not configured_model or configured_model == OPENAI_DEFAULT_MODEL:
            configured_model = QWEN_DEFAULT_MODEL
        self.model_name = configured_model
        self.timeout = timeout or settings.ai_request_timeout

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise LLMConfigurationError("AI_API_KEY is not configured; cannot call Qwen/DashScope")
        if not self.model_name:
            raise LLMConfigurationError("AI_MODEL_NAME is not configured; cannot call Qwen/DashScope")

        client = OpenAI(api_key=self.api_key, base_url=self.api_base_url, timeout=self.timeout)
        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content = completion.choices[0].message.content
        except AuthenticationError as exc:
            raise LLMResponseError("Qwen/DashScope authentication failed; check AI_API_KEY") from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise LLMResponseError("Qwen/DashScope request failed; check network or AI_API_BASE_URL") from exc
        except BadRequestError as exc:
            raise LLMResponseError(f"Qwen/DashScope request is invalid: {exc}") from exc
        except APIError as exc:
            raise LLMResponseError(f"Qwen/DashScope API returned an error: {exc}") from exc
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMResponseError("Qwen/DashScope response structure is invalid") from exc

        if not content or not isinstance(content, str):
            raise LLMResponseError("Qwen/DashScope returned empty content")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError("Model response is not valid JSON; no test cases were saved") from exc
        if not isinstance(parsed, dict):
            raise LLMResponseError("Model JSON root must be an object; no test cases were saved")
        return parsed
