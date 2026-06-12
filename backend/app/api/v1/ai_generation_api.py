from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.ai_generation import AiGenerationResult
from app.services import ai_testcase_service

router = APIRouter()


@router.post("/endpoints/{endpoint_id}/testcases/generate")
def generate_test_cases(endpoint_id: int, db: Session = Depends(get_db)) -> dict:
    result = ai_testcase_service.generate_test_cases_for_endpoint(db, endpoint_id)
    return success_response(AiGenerationResult.model_validate(result))
