from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class TestReport(TimestampMixin, Base):
    __tablename__ = "test_report"
    __table_args__ = (
        Index("idx_test_report_project_id", "project_id"),
        Index("idx_test_report_execution_task_id", "execution_task_id"),
        {"comment": "测试报告表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    execution_task_id: Mapped[int] = mapped_column(ForeignKey("execution_task.id"), nullable=False, comment="执行任务ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="报告标题")
    summary: Mapped[dict | None] = mapped_column(JSON, comment="报告摘要")
    report_path: Mapped[str | None] = mapped_column(String(512), comment="报告文件路径")
    status: Mapped[str] = mapped_column(String(32), default="created", nullable=False, comment="报告状态")

    execution_task: Mapped["ExecutionTask"] = relationship(back_populates="test_reports")
    project: Mapped["Project"] = relationship(back_populates="test_reports")
