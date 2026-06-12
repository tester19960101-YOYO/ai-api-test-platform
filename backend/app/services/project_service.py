from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, payload: ProjectCreate):
    return project_repository.create_project(db, payload.model_dump())


def list_projects(db: Session, skip: int = 0, limit: int = 20):
    return project_repository.list_projects(db, skip=skip, limit=limit)


def get_project(db: Session, project_id: int):
    project = project_repository.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project


def update_project(db: Session, project_id: int, payload: ProjectUpdate):
    project = get_project(db, project_id)
    data = payload.model_dump(exclude_unset=True)
    return project_repository.update_project(db, project, data)


def disable_project(db: Session, project_id: int):
    project = get_project(db, project_id)
    return project_repository.update_project(db, project, {"status": "inactive"})
