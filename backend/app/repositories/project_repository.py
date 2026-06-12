from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


def create_project(db: Session, data: dict) -> Project:
    project = Project(**data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, skip: int = 0, limit: int = 20) -> list[Project]:
    statement = select(Project).order_by(Project.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def update_project(db: Session, project: Project, data: dict) -> Project:
    for key, value in data.items():
        setattr(project, key, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
