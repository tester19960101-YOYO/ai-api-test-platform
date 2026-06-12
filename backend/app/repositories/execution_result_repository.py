from sqlalchemy.orm import Session

from app.models.execution_result import ExecutionResult


def create_execution_result(db: Session, data: dict) -> ExecutionResult:
    result = ExecutionResult(**data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def create_execution_results(db: Session, items: list[dict]) -> list[ExecutionResult]:
    results = [ExecutionResult(**item) for item in items]
    db.add_all(results)
    db.commit()
    for result in results:
        db.refresh(result)
    return results
