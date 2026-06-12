from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class AiAnalysisRecord(TimestampMixin, Base):
    __tablename__ = "ai_analysis_record"
    __table_args__ = (
        Index("idx_ai_analysis_record_project_id", "project_id"),
        Index("idx_ai_analysis_record_type", "analysis_type"),
        Index("idx_ai_analysis_record_status", "status"),
        {"comment": "AI分析记录表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    api_document_id: Mapped[int | None] = mapped_column(ForeignKey("api_document.id"), comment="接口文档ID")
    api_endpoint_id: Mapped[int | None] = mapped_column(ForeignKey("api_endpoint.id"), comment="接口ID")
    test_case_id: Mapped[int | None] = mapped_column(ForeignKey("test_case.id"), comment="测试用例ID")
    analysis_type: Mapped[str] = mapped_column(String(64), nullable=False, comment="分析类型")
    prompt_data: Mapped[dict | None] = mapped_column(JSON, comment="提示词数据")
    result_data: Mapped[dict | None] = mapped_column(JSON, comment="AI分析结果")
    model_name: Mapped[str | None] = mapped_column(String(128), comment="模型名称")
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, comment="分析状态")
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")

    project: Mapped["Project"] = relationship(back_populates="ai_analysis_records")
    api_document: Mapped["ApiDocument | None"] = relationship(back_populates="ai_analysis_records")
    api_endpoint: Mapped["ApiEndpoint | None"] = relationship(back_populates="ai_analysis_records")
    test_case: Mapped["TestCase | None"] = relationship(back_populates="ai_analysis_records")
