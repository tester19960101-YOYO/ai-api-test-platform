from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.generator.project_generator import PytestProjectGenerator
from app.repositories import (
    environment_repository,
    execution_result_repository,
    execution_task_repository,
    test_case_repository,
    test_report_repository,
)
from app.runner.pytest_runner import PytestRunner
from app.schemas.execution import ExecutionRunRequest
from app.services.project_service import get_project


def run_execution(db: Session, payload: ExecutionRunRequest) -> dict:
    project = get_project(db, payload.project_id)
    environment = environment_repository.get_environment(db, payload.environment_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="environment not found")
    if environment.project_id != project.id:
        raise HTTPException(status_code=400, detail="environment does not belong to project")
    if environment.status != "active":
        raise HTTPException(status_code=400, detail="environment is inactive")

    test_cases = _load_test_cases(db, payload.project_id, payload.case_ids)
    if not test_cases:
        raise HTTPException(status_code=400, detail="no executable test cases found")

    task = execution_task_repository.create_execution_task(
        db,
        {
            "project_id": project.id,
            "environment_id": environment.id,
            "task_name": f"{project.name}-execution-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "running",
            "trigger_type": "manual",
            "total_cases": len(test_cases),
            "passed_cases": 0,
            "failed_cases": 0,
            "started_at": datetime.now(),
            "config": {
                "case_ids": [test_case.id for test_case in test_cases],
                "timeout": payload.timeout,
            },
        },
    )

    generator = PytestProjectGenerator()
    generated_project_path = generator.generate(project, environment, task, test_cases, payload.timeout)
    runner_result = PytestRunner().run(generated_project_path, task.id)

    result_rows = _save_execution_results(db, task.id, runner_result.results)
    passed_cases = sum(1 for item in result_rows if item.status == "passed")
    failed_cases = len(result_rows) - passed_cases
    task_status = "passed" if runner_result.exit_code == 0 and failed_cases == 0 else "failed"
    task = execution_task_repository.update_execution_task(
        db,
        task,
        {
            "status": task_status,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "finished_at": datetime.now(),
            "config": {
                **(task.config or {}),
                "generated_project_path": _to_project_path(generated_project_path),
                "report_path": _to_project_path(runner_result.report_path),
                "log_path": _to_project_path(runner_result.log_path),
                "pytest_exit_code": runner_result.exit_code,
            },
        },
    )
    report = test_report_repository.create_test_report(
        db,
        {
            "execution_task_id": task.id,
            "project_id": project.id,
            "title": f"{task.task_name} report",
            "summary": {
                "total_cases": len(test_cases),
                "passed_cases": passed_cases,
                "failed_cases": failed_cases,
                "pytest_exit_code": runner_result.exit_code,
            },
            "report_path": _to_project_path(runner_result.report_path),
            "status": "created" if runner_result.report_path.exists() else "failed",
        },
    )

    return {
        "task": task,
        "results": result_rows,
        "report": report,
        "generated_project_path": _to_project_path(generated_project_path),
        "report_path": _to_project_path(runner_result.report_path),
        "log_path": _to_project_path(runner_result.log_path),
        "pytest_exit_code": runner_result.exit_code,
        "stdout": runner_result.stdout[-4000:],
        "stderr": runner_result.stderr[-4000:],
    }


def _load_test_cases(db: Session, project_id: int, case_ids: list[int] | None):
    if case_ids:
        test_cases = test_case_repository.list_test_cases_by_ids(db, case_ids)
        found_ids = {test_case.id for test_case in test_cases}
        missing_ids = set(case_ids) - found_ids
        if missing_ids:
            raise HTTPException(status_code=404, detail=f"test cases not found: {sorted(missing_ids)}")
    else:
        test_cases = test_case_repository.list_test_cases_by_project(db, project_id, skip=0, limit=100)
    for test_case in test_cases:
        if test_case.project_id != project_id:
            raise HTTPException(status_code=400, detail="test case does not belong to project")
        if test_case.status not in {"active", "draft", "generated"}:
            raise HTTPException(status_code=400, detail=f"test case {test_case.id} is not executable")
    return test_cases


def _save_execution_results(db: Session, task_id: int, results: list[dict]):
    rows = [
        {
            "execution_task_id": task_id,
            "test_case_id": result.get("test_case_id"),
            "api_endpoint_id": result.get("api_endpoint_id"),
            "status": result.get("status") or "failed",
            "status_code": result.get("status_code"),
            "response_time_ms": result.get("response_time_ms"),
            "request_data": result.get("request_data"),
            "response_data": result.get("response_data"),
            "assertion_result": result.get("assertion_result"),
            "error_message": result.get("error_message"),
        }
        for result in results
    ]
    if not rows:
        rows = [
            {
                "execution_task_id": task_id,
                "status": "failed",
                "error_message": "pytest did not produce execution result data",
            }
        ]
    return execution_result_repository.create_execution_results(db, rows)


def _to_project_path(path: Path) -> str:
    root = Path(__file__).resolve().parents[3]
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
