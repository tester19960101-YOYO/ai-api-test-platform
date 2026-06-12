from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.environment import EnvironmentCreate, EnvironmentRead, EnvironmentUpdate
from app.services import environment_service

router = APIRouter()


@router.post("/projects/{project_id}/environments")
def create_environment(project_id: int, payload: EnvironmentCreate, db: Session = Depends(get_db)) -> dict:
    environment = environment_service.create_environment(db, project_id, payload)
    return success_response(EnvironmentRead.model_validate(environment))


@router.get("/projects/{project_id}/environments")
def list_environments(
    project_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    environments = environment_service.list_environments(db, project_id, skip=skip, limit=limit)
    return success_response([EnvironmentRead.model_validate(environment) for environment in environments])


@router.get("/environments/{environment_id}")
def get_environment(environment_id: int, db: Session = Depends(get_db)) -> dict:
    environment = environment_service.get_environment(db, environment_id)
    return success_response(EnvironmentRead.model_validate(environment))


@router.put("/environments/{environment_id}")
def update_environment(environment_id: int, payload: EnvironmentUpdate, db: Session = Depends(get_db)) -> dict:
    environment = environment_service.update_environment(db, environment_id, payload)
    return success_response(EnvironmentRead.model_validate(environment))


@router.delete("/environments/{environment_id}")
def disable_environment(environment_id: int, db: Session = Depends(get_db)) -> dict:
    environment = environment_service.disable_environment(db, environment_id)
    return success_response(EnvironmentRead.model_validate(environment))
