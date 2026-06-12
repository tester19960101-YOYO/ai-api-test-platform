from sqlalchemy.orm import Session

from app.models.test_report import TestReport


def create_test_report(db: Session, data: dict) -> TestReport:
    report = TestReport(**data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
