import json
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, BadRequestError, OpenAI

from app.core.config import settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


class OpenAIClient:
    """OpenAI Chat Completions client that returns validated JSON objects."""

    provider = "openai"

    def __init__(
        self,
        api_base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_base_url = (
            api_base_url if api_base_url is not None else settings.ai_api_base_url
        ).strip() or "https://api.openai.com/v1"
        self.api_key = (api_key if api_key is not None else settings.ai_api_key).strip()
        self.model_name = (model_name if model_name is not None else settings.ai_model_name).strip()
        self.timeout = timeout or settings.ai_request_timeout

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise LLMConfigurationError("AI_API_KEY 未配置，无法调用真实 OpenAI")
        if not self.model_name:
            raise LLMConfigurationError("AI_MODEL_NAME 未配置，无法调用真实 OpenAI")

        client = OpenAI(api_key=self.api_key, base_url=self.api_base_url, timeout=self.timeout)
        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
        except AuthenticationError as exc:
            raise LLMResponseError("OpenAI 认证失败，请检查 AI_API_KEY 是否正确或已过期") from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise LLMResponseError("OpenAI 调用失败，请检查网络、代理或 AI_API_BASE_URL") from exc
        except BadRequestError as exc:
            raise LLMResponseError(f"OpenAI 请求参数不合法: {exc}") from exc
        except APIError as exc:
            raise LLMResponseError(f"OpenAI API 返回错误: {exc}") from exc
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMResponseError("OpenAI 返回结构不合法，无法读取 message.content") from exc

        if not content or not isinstance(content, str):
            raise LLMResponseError("OpenAI 返回内容为空")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError("模型返回格式不合法：不是有效 JSON，未保存测试用例") from exc
        if not isinstance(parsed, dict):
            raise LLMResponseError("模型返回格式不合法：JSON 根节点必须是对象，未保存测试用例")
        return parsed
