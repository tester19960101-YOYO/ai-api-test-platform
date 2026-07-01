from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.test_case import TestCaseCreate, TestCaseRead, TestCaseUpdate
from app.services import test_case_service

router = APIRouter()


@router.post("/test-cases")
@router.post("/testcases")
def create_test_case(payload: TestCaseCreate, db: Session = Depends(get_db)) -> dict:
    test_case = test_case_service.create_test_case(db, payload)
    return success_response(TestCaseRead.model_validate(test_case))


@router.get("/projects/{project_id}/test-cases")
@router.get("/projects/{project_id}/testcases")
def list_test_cases(
    project_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    test_cases = test_case_service.list_test_cases(db, project_id, skip=skip, limit=limit)
    return success_response([TestCaseRead.model_validate(test_case) for test_case in test_cases])


@router.get("/testcases")
def list_testcases_by_query_project(
    project_id: int = Query(..., gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    test_cases = test_case_service.list_test_cases(db, project_id, skip=skip, limit=limit)
    return success_response([TestCaseRead.model_validate(test_case) for test_case in test_cases])


@router.get("/test-cases/{test_case_id}")
@router.get("/testcases/{test_case_id}")
def get_test_case(test_case_id: int, db: Session = Depends(get_db)) -> dict:
    test_case = test_case_service.get_test_case(db, test_case_id)
    return success_response(TestCaseRead.model_validate(test_case))


@router.put("/test-cases/{test_case_id}")
@router.put("/testcases/{test_case_id}")
def update_test_case(test_case_id: int, payload: TestCaseUpdate, db: Session = Depends(get_db)) -> dict:
    test_case = test_case_service.update_test_case(db, test_case_id, payload)
    return success_response(TestCaseRead.model_validate(test_case))


@router.delete("/test-cases/{test_case_id}")
@router.delete("/testcases/{test_case_id}")
def disable_test_case(test_case_id: int, db: Session = Depends(get_db)) -> dict:
    test_case = test_case_service.disable_test_case(db, test_case_id)
    return success_response(TestCaseRead.model_validate(test_case))
