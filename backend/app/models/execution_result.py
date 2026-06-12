from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class ExecutionResult(TimestampMixin, Base):
    __tablename__ = "execution_result"
    __table_args__ = (
        Index("idx_execution_result_task_id", "execution_task_id"),
        Index("idx_execution_result_test_case_id", "test_case_id"),
        Index("idx_execution_result_status", "status"),
        {"comment": "执行结果表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    execution_task_id: Mapped[int] = mapped_column(ForeignKey("execution_task.id"), nullable=False, comment="执行任务ID")
    test_case_id: Mapped[int | None] = mapped_column(ForeignKey("test_case.id"), comment="测试用例ID")
    api_endpoint_id: Mapped[int | None] = mapped_column(ForeignKey("api_endpoint.id"), comment="接口ID")
    status: Mapped[str] = mapped_column(String(32), nullable=False, comment="执行状态")
    status_code: Mapped[int | None] = mapped_column(Integer, comment="HTTP状态码")
    response_time_ms: Mapped[int | None] = mapped_column(Integer, comment="响应耗时毫秒")
    request_data: Mapped[dict | None] = mapped_column(JSON, comment="请求数据")
    response_data: Mapped[dict | None] = mapped_column(JSON, comment="响应数据")
    assertion_result: Mapped[dict | None] = mapped_column(JSON, comment="断言结果")
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")

    execution_task: Mapped["ExecutionTask"] = relationship(back_populates="execution_results")
    test_case: Mapped["TestCase | None"] = relationship(back_populates="execution_results")
    api_endpoint: Mapped["ApiEndpoint | None"] = relationship(back_populates="execution_results")
