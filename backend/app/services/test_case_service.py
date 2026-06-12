from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import test_case_repository
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate
from app.services.api_endpoint_service import get_api_endpoint
from app.services.project_service import get_project


def create_test_case(db: Session, payload: TestCaseCreate):
    get_project(db, payload.project_id)
    if payload.api_endpoint_id is not None:
        endpoint = get_api_endpoint(db, payload.api_endpoint_id)
        if endpoint.project_id != payload.project_id:
            raise HTTPException(status_code=400, detail="api endpoint does not belong to project")
    return test_case_repository.create_test_case(db, payload.model_dump())


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
    if data.get("api_endpoint_id") is not None:
        endpoint = get_api_endpoint(db, data["api_endpoint_id"])
        if endpoint.project_id != test_case.project_id:
            raise HTTPException(status_code=400, detail="api endpoint does not belong to project")
    return test_case_repository.update_test_case(db, test_case, data)


def disable_test_case(db: Session, test_case_id: int):
    test_case = get_test_case(db, test_case_id)
    return test_case_repository.update_test_case(db, test_case, {"status": "inactive"})
