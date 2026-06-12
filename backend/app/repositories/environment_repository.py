from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.environment import Environment


def create_environment(db: Session, data: dict) -> Environment:
    environment = Environment(**data)
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment


def list_environments_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 20) -> list[Environment]:
    statement = (
        select(Environment)
        .where(Environment.project_id == project_id)
        .order_by(Environment.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_environment(db: Session, environment_id: int) -> Environment | None:
    return db.get(Environment, environment_id)


def get_default_environment(db: Session, project_id: int) -> Environment | None:
    statement = (
        select(Environment)
        .where(Environment.project_id == project_id, Environment.is_default.is_(True), Environment.status == "active")
        .order_by(Environment.id.asc())
        .limit(1)
    )
    return db.scalars(statement).first()


def update_environment(db: Session, environment: Environment, data: dict) -> Environment:
    for key, value in data.items():
        setattr(environment, key, value)
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment
