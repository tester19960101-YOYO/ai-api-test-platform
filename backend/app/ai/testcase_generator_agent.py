from typing import Any

from app.ai.llm_factory import LLMClient, LLMFactory
from app.ai.prompt_builder import SYSTEM_PROMPT, build_testcase_generation_prompt
from app.ai.swagger_case_model import build_endpoint_model
from app.ai.testcase_standardizer import standardize_ai_testcases
from app.models.api_endpoint import ApiEndpoint


class TestcaseGeneratorAgent:
    """Real LLM-backed agent that generates executable API testcases."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMFactory.create()
        self.model_name = self.llm_client.model_name
        self.provider = self.llm_client.provider

    def generate(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        endpoint_model = build_endpoint_model(endpoint)
        prompt = build_testcase_generation_prompt(endpoint_model)
        raw_output = self.llm_client.generate_json(SYSTEM_PROMPT, prompt)
        standardized = standardize_ai_testcases(raw_output, endpoint)
        standardized["model_name"] = self.model_name
        standardized["provider"] = self.provider
        standardized["raw_ai_output"] = raw_output
        standardized["endpoint_model"] = endpoint_model
        return standardized
