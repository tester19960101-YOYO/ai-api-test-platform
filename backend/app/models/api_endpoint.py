from sqlalchemy import Boolean, JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class ApiEndpoint(TimestampMixin, Base):
    __tablename__ = "api_endpoint"
    __table_args__ = (
        Index("idx_api_endpoint_project_id", "project_id"),
        Index("idx_api_endpoint_document_id", "api_document_id"),
        Index("idx_api_endpoint_method_path", "method", "path"),
        Index("idx_api_endpoint_status", "status"),
        {"comment": "接口定义表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    api_document_id: Mapped[int | None] = mapped_column(ForeignKey("api_document.id"), comment="接口文档ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="接口名称")
    group_name: Mapped[str | None] = mapped_column(String(128), comment="接口分组")
    method: Mapped[str] = mapped_column(String(16), nullable=False, comment="HTTP方法")
    path: Mapped[str] = mapped_column(String(512), nullable=False, comment="接口路径")
    description: Mapped[str | None] = mapped_column(Text, comment="接口描述")
    headers: Mapped[dict | None] = mapped_column(JSON, comment="请求头定义")
    request_params: Mapped[dict | None] = mapped_column(JSON, comment="请求参数定义")
    request_body_schema: Mapped[dict | None] = mapped_column(JSON, comment="请求体结构")
    response_schema: Mapped[dict | None] = mapped_column(JSON, comment="响应结构")
    example_request: Mapped[dict | None] = mapped_column(JSON, comment="示例请求")
    example_response: Mapped[dict | None] = mapped_column(JSON, comment="示例响应")
    auth_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否需要鉴权")
    tags: Mapped[list | None] = mapped_column(JSON, comment="接口标签")
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, comment="接口状态")

    project: Mapped["Project"] = relationship(back_populates="api_endpoints")
    api_document: Mapped["ApiDocument | None"] = relationship(back_populates="api_endpoints")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="api_endpoint")
    execution_results: Mapped[list["ExecutionResult"]] = relationship(back_populates="api_endpoint")
    ai_analysis_records: Mapped[list["AiAnalysisRecord"]] = relationship(back_populates="api_endpoint")
