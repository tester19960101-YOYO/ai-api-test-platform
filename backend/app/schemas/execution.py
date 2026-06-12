from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExecutionRunRequest(BaseModel):
    project_id: int = Field(..., gt=0)
    environment_id: int = Field(..., gt=0)
    case_ids: list[int] | None = Field(default=None, min_length=1)
    timeout: int = Field(default=10, ge=1, le=120)


class ExecutionResultRead(BaseModel):
    id: int
    execution_task_id: int
    test_case_id: int | None
    api_endpoint_id: int | None
    status: str
    status_code: int | None
    response_time_ms: int | None
    request_data: dict[str, Any] | None
    response_data: dict[str, Any] | None
    assertion_result: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestReportRead(BaseModel):
    id: int
    execution_task_id: int
    project_id: int
    title: str
    summary: dict[str, Any] | None
    report_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionTaskRead(BaseModel):
    id: int
    project_id: int
    environment_id: int | None
    task_name: str
    status: str
    trigger_type: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    started_at: datetime | None
    finished_at: datetime | None
    config: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionRunResponse(BaseModel):
    task: ExecutionTaskRead
    results: list[ExecutionResultRead]
    report: TestReportRead
    generated_project_path: str
    report_path: str
    log_path: str
    pytest_exit_code: int
    stdout: str
    stderr: str
