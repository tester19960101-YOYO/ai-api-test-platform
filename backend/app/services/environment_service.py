from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import environment_repository
from app.services.project_service import get_project
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate


def create_environment(db: Session, project_id: int, payload: EnvironmentCreate):
    get_project(db, project_id)
    data = payload.model_dump()
    data["project_id"] = project_id
    return environment_repository.create_environment(db, data)


def list_environments(db: Session, project_id: int, skip: int = 0, limit: int = 20):
    get_project(db, project_id)
    return environment_repository.list_environments_by_project(db, project_id, skip=skip, limit=limit)


def get_environment(db: Session, environment_id: int):
    environment = environment_repository.get_environment(db, environment_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="environment not found")
    return environment


def update_environment(db: Session, environment_id: int, payload: EnvironmentUpdate):
    environment = get_environment(db, environment_id)
    data = payload.model_dump(exclude_unset=True)
    return environment_repository.update_environment(db, environment, data)


def disable_environment(db: Session, environment_id: int):
    environment = get_environment(db, environment_id)
    return environment_repository.update_environment(db, environment, {"status": "inactive"})
