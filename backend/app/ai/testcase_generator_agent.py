from typing import Any

from app.ai.llm_factory import LLMClient, LLMFactory
from app.ai.prompt_builder import SYSTEM_PROMPT, build_testcase_generation_prompt
from app.ai.swagger_case_model import build_endpoint_model
from app.ai.testcase_standardizer import standardize_ai_testcases
from app.models.api_endpoint import ApiEndpoint
from app.services.coverage_engine import CoverageEngine


class TestcaseGeneratorAgent:
    """Real LLM-backed agent that generates executable API testcases."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMFactory.create()
        self.model_name = self.llm_client.model_name
        self.provider = self.llm_client.provider
        self.coverage_engine = CoverageEngine()

    def generate(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        endpoint_model = build_endpoint_model(endpoint)
        coverage_plan = self.coverage_engine.build_coverage_plan(endpoint_model)
        prompt = build_testcase_generation_prompt(endpoint_model, coverage_plan)
        raw_output = self.llm_client.generate_json(SYSTEM_PROMPT, prompt)
        standardized = standardize_ai_testcases(raw_output, endpoint, coverage_plan)
        standardized["model_name"] = self.model_name
        standardized["provider"] = self.provider
        standardized["raw_ai_output"] = raw_output
        standardized["endpoint_model"] = endpoint_model
        standardized["coverage_plan"] = coverage_plan
        return standardized
