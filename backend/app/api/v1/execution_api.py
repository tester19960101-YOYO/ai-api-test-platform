from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.execution import ExecutionRunRequest, ExecutionRunResponse
from app.services import execution_service

router = APIRouter()


@router.post("/executions/run")
def run_execution(payload: ExecutionRunRequest, db: Session = Depends(get_db)) -> dict:
    result = execution_service.run_execution(db, payload)
    return success_response(ExecutionRunResponse.model_validate(result))
