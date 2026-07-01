from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import test_case_repository
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate
from app.services.api_endpoint_service import get_api_endpoint
from app.services.project_service import get_project
from app.services.test_case_unified_model import normalize_test_case_data


def create_test_case(db: Session, payload: TestCaseCreate):
    get_project(db, payload.project_id)
    endpoint = None
    if payload.api_endpoint_id is not None:
        endpoint = get_api_endpoint(db, payload.api_endpoint_id)
        if endpoint.project_id != payload.project_id:
            raise HTTPException(status_code=400, detail="api endpoint does not belong to project")
    data = normalize_test_case_data(payload.model_dump(), endpoint)
    return test_case_repository.create_test_case(db, data)


def list_test_cases(db: Session, project_id: int, skip: int = 0, limit: int = 20):
    get_project(db, project_id)
    return test_case_repository.list_test_cases_by_project(db, project_id, skip=skip, limit=limit)


def get_test_case(db: Session, test_case_id: int):
    test_case = test_case_repository.get_test_case(db, test_case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="test case not found")
    return test_case


def update_test_case(db: Session, test_case_id: int, payload: TestCaseUpdate):
    test_case = get_test_case(db, test_case_id)
    data = payload.model_dump(exclude_unset=True)
    endpoint = test_case.api_endpoint
    if data.get("api_endpoint_id") is not None:
        endpoint = get_api_endpoint(db, data["api_endpoint_id"])
        if endpoint.project_id != test_case.project_id:
            raise HTTPException(status_code=400, detail="api endpoint does not belong to project")
    merged = {
        "project_id": test_case.project_id,
        "api_endpoint_id": test_case.api_endpoint_id,
        "endpoint_name": test_case.endpoint_name,
        "endpoint_path": test_case.endpoint_path,
        "name": test_case.name,
        "description": test_case.description,
        "type": test_case.type,
        "priority": test_case.priority,
        "status": test_case.status,
        "request_data": test_case.request_data,
        "assertions": test_case.assertions,
        "dsl_assertions": test_case.dsl_assertions,
        "coverage_tag": test_case.coverage_tag,
        "risk_level": test_case.risk_level,
        "data_dependency": test_case.data_dependency,
        "ai_metadata": test_case.ai_metadata,
        "steps": test_case.steps,
        "variables": test_case.variables,
        **data,
    }
    normalized = normalize_test_case_data(merged, endpoint)
    normalized.pop("project_id", None)
    return test_case_repository.update_test_case(db, test_case, normalized)


def disable_test_case(db: Session, test_case_id: int):
    test_case = get_test_case(db, test_case_id)
    return test_case_repository.update_test_case(db, test_case, {"status": "disabled"})
