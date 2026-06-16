from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import LLMConfigurationError, LLMResponseError
from app.ai.testcase_standardizer import TestcaseStandardizationError
from app.ai.testcase_generator_agent import TestcaseGeneratorAgent
from app.repositories import ai_analysis_record_repository, test_case_repository
from app.schemas.ai_generation import GeneratedTestcaseOutput
from app.services.api_endpoint_service import get_api_endpoint


def generate_test_cases_for_endpoint(db: Session, endpoint_id: int) -> dict:
    endpoint = get_api_endpoint(db, endpoint_id)
    agent = TestcaseGeneratorAgent()
    prompt_data = _build_prompt_data(endpoint)
    try:
        raw_output = agent.generate(endpoint)
    except LLMConfigurationError as exc:
        ai_analysis_record_repository.create_ai_analysis_record(
            db,
            {
                "project_id": endpoint.project_id,
                "api_document_id": endpoint.api_document_id,
                "api_endpoint_id": endpoint.id,
                "analysis_type": "testcase_generation",
                "prompt_data": prompt_data,
                "result_data": {"error_type": "configuration"},
                "model_name": agent.model_name,
                "status": "failed",
                "error_message": str(exc),
            },
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (LLMResponseError, TestcaseStandardizationError) as exc:
        ai_analysis_record_repository.create_ai_analysis_record(
            db,
            {
                "project_id": endpoint.project_id,
                "api_document_id": endpoint.api_document_id,
                "api_endpoint_id": endpoint.id,
                "analysis_type": "testcase_generation",
                "prompt_data": prompt_data,
                "result_data": {"error_type": "model_output"},
                "model_name": agent.model_name,
                "status": "failed",
                "error_message": str(exc),
            },
        )
        raise HTTPException(status_code=502, detail=f"AI 用例生成失败，未保存测试用例：{exc}") from exc

    try:
        generated_output = GeneratedTestcaseOutput.model_validate(raw_output)
    except ValidationError as exc:
        ai_analysis_record_repository.create_ai_analysis_record(
            db,
            {
                "project_id": endpoint.project_id,
                "api_document_id": endpoint.api_document_id,
                "api_endpoint_id": endpoint.id,
                "analysis_type": "testcase_generation",
                "prompt_data": prompt_data,
                "result_data": raw_output,
                "model_name": agent.model_name,
                "status": "failed",
                "error_message": str(exc),
            },
        )
        raise HTTPException(status_code=502, detail="AI 输出结构校验失败，未保存测试用例") from exc

    test_cases = []
    provider = generated_output.provider or getattr(agent, "provider", "unknown")
    for generated_case in generated_output.cases:
        variables = dict(generated_case.variables or {})
        variables["ai_assertion_dsl"] = list(generated_case.assertions)
        variables["ai_generation_mode"] = "real_llm"
        variables["ai_provider"] = provider
        variables["source"] = f"ai_{provider}"
        test_cases.append(
            test_case_repository.create_test_case(
                db,
                {
                    "project_id": endpoint.project_id,
                    "api_endpoint_id": endpoint.id,
                    "name": generated_case.name,
                    "description": generated_case.description,
                    "priority": generated_case.priority,
                    "status": "generated",
                    "steps": [step.model_dump() for step in generated_case.steps],
                    "assertions": [],
                    "variables": variables,
                },
            )
        )

    record = ai_analysis_record_repository.create_ai_analysis_record(
        db,
        {
            "project_id": endpoint.project_id,
            "api_document_id": endpoint.api_document_id,
            "api_endpoint_id": endpoint.id,
            "analysis_type": "testcase_generation",
            "prompt_data": prompt_data,
            "result_data": {
                "standardized_output": generated_output.model_dump(),
                "raw_ai_output": raw_output.get("raw_ai_output"),
            },
            "model_name": generated_output.model_name,
            "status": "success",
        },
    )

    return {
        "endpoint_id": endpoint.id,
        "analysis_record_id": record.id,
        "case_count": len(test_cases),
        "test_cases": test_cases,
    }


def _build_prompt_data(endpoint) -> dict:
    return {
        "endpoint_id": endpoint.id,
        "name": endpoint.name,
        "method": endpoint.method,
        "path": endpoint.path,
        "headers": endpoint.headers,
        "request_params": endpoint.request_params,
        "request_body_schema": endpoint.request_body_schema,
        "response_schema": endpoint.response_schema,
        "auth_required": endpoint.auth_required,
        "mode": "real_llm",
    }
