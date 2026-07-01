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
        Index("idx_test_case_type", "type"),
        Index("idx_test_case_priority", "priority"),
        {"comment": "测试用例表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    api_endpoint_id: Mapped[int | None] = mapped_column(ForeignKey("api_endpoint.id"), comment="接口ID")
    endpoint_name: Mapped[str | None] = mapped_column(String(128), comment="接口名称快照")
    endpoint_path: Mapped[str | None] = mapped_column(String(512), comment="接口路径快照")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="用例名称")
    description: Mapped[str | None] = mapped_column(Text, comment="用例描述")
    type: Mapped[str] = mapped_column(String(32), default="functional", nullable=False, comment="统一用例类型")
    priority: Mapped[str] = mapped_column(String(32), default="P1", nullable=False, comment="优先级")
    status: Mapped[str] = mapped_column(String(32), default="generated", nullable=False, comment="用例状态")
    request_data: Mapped[dict | None] = mapped_column(JSON, comment="统一请求数据")
    assertions: Mapped[list | None] = mapped_column(JSON, comment="结构化断言")
    dsl_assertions: Mapped[list | None] = mapped_column(JSON, comment="DSL断言列表")
    coverage_tag: Mapped[list | None] = mapped_column(JSON, comment="覆盖标签")
    risk_level: Mapped[str | None] = mapped_column(String(32), comment="风险等级")
    data_dependency: Mapped[dict | None] = mapped_column(JSON, comment="数据依赖")
    ai_metadata: Mapped[dict | None] = mapped_column(JSON, comment="AI生成元数据")

    # Legacy compatibility fields. They are kept for migration and old data reads only.
    steps: Mapped[list | None] = mapped_column(JSON, comment="历史测试步骤")
    variables: Mapped[dict | None] = mapped_column(JSON, comment="历史用例变量")

    project: Mapped["Project"] = relationship(back_populates="test_cases")
    api_endpoint: Mapped["ApiEndpoint | None"] = relationship(back_populates="test_cases")
    execution_results: Mapped[list["ExecutionResult"]] = relationship(back_populates="test_case")
    ai_analysis_records: Mapped[list["AiAnalysisRecord"]] = relationship(back_populates="test_case")
