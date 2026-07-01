from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import LLMConfigurationError, LLMResponseError
from app.ai.testcase_standardizer import TestcaseStandardizationError
from app.ai.testcase_generator_agent import TestcaseGeneratorAgent
from app.repositories import ai_analysis_record_repository, test_case_repository
from app.schemas.ai_generation import GeneratedTestcaseOutput
from app.services.coverage_engine import CoverageEngine
from app.services.api_endpoint_service import get_api_endpoint
from app.services.test_case_unified_model import normalize_test_case_data


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
        ai_metadata = {
            "generated_by": "ai_strategy_generator",
            "source": f"ai_{provider}",
            "ai_provider": provider,
            "ai_generation_mode": "real_llm",
            "model_name": generated_output.model_name,
            "purpose": variables.get("purpose"),
            "reason": variables.get("reason"),
            "coverage_source": variables.get("coverage_source") or "ai",
        }
        request = generated_case.steps[0].request if generated_case.steps else {}
        case_data = normalize_test_case_data(
            {
                "project_id": endpoint.project_id,
                "api_endpoint_id": endpoint.id,
                "endpoint_name": endpoint.name,
                "endpoint_path": endpoint.path,
                "name": generated_case.name,
                "description": generated_case.description,
                "type": variables.get("coverage_dimension") or generated_case.case_type,
                "priority": variables.get("risk_level") or generated_case.priority,
                "status": "generated",
                "request": request,
                "dsl_assertions": list(generated_case.assertions),
                "coverage_tag": [variables.get("coverage_dimension") or generated_case.case_type],
                "risk_level": variables.get("risk_level"),
                "data_dependency": variables.get("data_dependency") or {},
                "ai_metadata": ai_metadata,
                "variables": variables,
            },
            endpoint,
        )
        test_cases.append(
            test_case_repository.create_test_case(
                db,
                case_data,
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
                "coverage_plan": raw_output.get("coverage_plan"),
                "coverage_summary": generated_output.coverage_summary,
            },
            "model_name": generated_output.model_name,
            "status": "success",
        },
    )

    return {
        "endpoint_id": endpoint.id,
        "analysis_record_id": record.id,
        "case_count": len(test_cases),
        "coverage_matrix": generated_output.coverage_matrix,
        "coverage_summary": generated_output.coverage_summary,
        "test_cases": test_cases,
    }


def _build_prompt_data(endpoint) -> dict:
    api_schema = {
        "endpoint_id": endpoint.id,
        "name": endpoint.name,
        "method": endpoint.method,
        "path": endpoint.path,
        "headers": endpoint.headers,
        "request_params": endpoint.request_params,
        "request_body_schema": endpoint.request_body_schema,
        "response_schema": endpoint.response_schema,
        "auth_required": endpoint.auth_required,
    }
    return {
        **api_schema,
        "coverage_plan": CoverageEngine().build_coverage_plan(api_schema),
        "mode": "real_llm",
    }
