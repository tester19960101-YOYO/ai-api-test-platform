from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.testcase_generator_agent import TestcaseGeneratorAgent
from app.repositories import ai_analysis_record_repository, test_case_repository
from app.schemas.ai_generation import GeneratedTestcaseOutput
from app.services.api_endpoint_service import get_api_endpoint


def generate_test_cases_for_endpoint(db: Session, endpoint_id: int) -> dict:
    endpoint = get_api_endpoint(db, endpoint_id)
    agent = TestcaseGeneratorAgent()
    raw_output = agent.generate(endpoint)

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
                "prompt_data": _build_prompt_data(endpoint),
                "result_data": raw_output,
                "model_name": agent.model_name,
                "status": "failed",
                "error_message": str(exc),
            },
        )
        raise HTTPException(status_code=500, detail="mock AI output validation failed") from exc

    test_cases = [
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
                "assertions": [assertion.model_dump() for assertion in generated_case.assertions],
                "variables": generated_case.variables,
            },
        )
        for generated_case in generated_output.cases
    ]

    record = ai_analysis_record_repository.create_ai_analysis_record(
        db,
        {
            "project_id": endpoint.project_id,
            "api_document_id": endpoint.api_document_id,
            "api_endpoint_id": endpoint.id,
            "analysis_type": "testcase_generation",
            "prompt_data": _build_prompt_data(endpoint),
            "result_data": generated_output.model_dump(),
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
        "mode": "mock",
    }
