from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.test_case import TestCase


def create_test_case(db: Session, data: dict) -> TestCase:
    test_case = TestCase(**data)
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


def list_test_cases_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 20) -> list[TestCase]:
    statement = (
        select(TestCase)
        .options(selectinload(TestCase.api_endpoint))
        .where(TestCase.project_id == project_id)
        .order_by(TestCase.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_test_case(db: Session, test_case_id: int) -> TestCase | None:
    statement = select(TestCase).options(selectinload(TestCase.api_endpoint)).where(TestCase.id == test_case_id)
    return db.scalars(statement).first()


def list_test_cases_by_ids(db: Session, case_ids: list[int]) -> list[TestCase]:
    statement = (
        select(TestCase)
        .options(selectinload(TestCase.api_endpoint))
        .where(TestCase.id.in_(case_ids))
        .order_by(TestCase.id.asc())
    )
    return list(db.scalars(statement).all())


def update_test_case(db: Session, test_case: TestCase, data: dict) -> TestCase:
    for key, value in data.items():
        setattr(test_case, key, value)
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case
