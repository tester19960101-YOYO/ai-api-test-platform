from sqlalchemy.orm import Session

from app.models.execution_task import ExecutionTask


def create_execution_task(db: Session, data: dict) -> ExecutionTask:
    task = ExecutionTask(**data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_execution_task(db: Session, task: ExecutionTask, data: dict) -> ExecutionTask:
    for key, value in data.items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_execution_task(db: Session, task_id: int) -> ExecutionTask | None:
    return db.get(ExecutionTask, task_id)
