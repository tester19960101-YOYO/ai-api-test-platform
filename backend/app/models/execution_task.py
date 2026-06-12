from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class ExecutionTask(TimestampMixin, Base):
    __tablename__ = "execution_task"
    __table_args__ = (
        Index("idx_execution_task_project_id", "project_id"),
        Index("idx_execution_task_environment_id", "environment_id"),
        Index("idx_execution_task_status", "status"),
        {"comment": "执行任务表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    environment_id: Mapped[int | None] = mapped_column(ForeignKey("environment.id"), comment="环境ID")
    task_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="任务名称")
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, comment="任务状态")
    trigger_type: Mapped[str] = mapped_column(String(32), default="manual", nullable=False, comment="触发方式")
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="用例总数")
    passed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="通过用例数")
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="失败用例数")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="开始时间")
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="结束时间")
    config: Mapped[dict | None] = mapped_column(JSON, comment="执行配置")

    project: Mapped["Project"] = relationship(back_populates="execution_tasks")
    environment: Mapped["Environment | None"] = relationship(back_populates="execution_tasks")
    execution_results: Mapped[list["ExecutionResult"]] = relationship(back_populates="execution_task")
    test_reports: Mapped[list["TestReport"]] = relationship(back_populates="execution_task")
