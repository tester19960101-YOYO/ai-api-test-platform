from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects")


@router.post("")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> dict:
    project = project_service.create_project(db, payload)
    return success_response(ProjectRead.model_validate(project))


@router.get("")
def list_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    projects = project_service.list_projects(db, skip=skip, limit=limit)
    return success_response([ProjectRead.model_validate(project) for project in projects])


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)) -> dict:
    project = project_service.get_project(db, project_id)
    return success_response(ProjectRead.model_validate(project))


@router.put("/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)) -> dict:
    project = project_service.update_project(db, project_id, payload)
    return success_response(ProjectRead.model_validate(project))


@router.delete("/{project_id}")
def disable_project(project_id: int, db: Session = Depends(get_db)) -> dict:
    project = project_service.disable_project(db, project_id)
    return success_response(ProjectRead.model_validate(project))
