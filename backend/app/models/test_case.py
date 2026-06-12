from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class TestCase(TimestampMixin, Base):
    __tablename__ = "test_case"
    __table_args__ = (
        Index("idx_test_case_project_id", "project_id"),
        Index("idx_test_case_api_endpoint_id", "api_endpoint_id"),
        Index("idx_test_case_status", "status"),
        {"comment": "测试用例表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    api_endpoint_id: Mapped[int | None] = mapped_column(ForeignKey("api_endpoint.id"), comment="接口ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="用例名称")
    description: Mapped[str | None] = mapped_column(Text, comment="用例描述")
    priority: Mapped[str] = mapped_column(String(32), default="medium", nullable=False, comment="优先级")
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, comment="用例状态")
    steps: Mapped[list | None] = mapped_column(JSON, comment="测试步骤")
    assertions: Mapped[list | None] = mapped_column(JSON, comment="断言配置")
    variables: Mapped[dict | None] = mapped_column(JSON, comment="用例变量")

    project: Mapped["Project"] = relationship(back_populates="test_cases")
    api_endpoint: Mapped["ApiEndpoint | None"] = relationship(back_populates="test_cases")
    execution_results: Mapped[list["ExecutionResult"]] = relationship(back_populates="test_case")
    ai_analysis_records: Mapped[list["AiAnalysisRecord"]] = relationship(back_populates="test_case")
