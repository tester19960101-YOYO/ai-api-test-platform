from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class ApiDocument(TimestampMixin, Base):
    __tablename__ = "api_document"
    __table_args__ = (
        Index("idx_api_document_project_id", "project_id"),
        Index("idx_api_document_status", "status"),
        {"comment": "接口文档表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="文档名称")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="文档来源类型")
    file_path: Mapped[str | None] = mapped_column(String(512), comment="上传文件路径")
    raw_content: Mapped[str | None] = mapped_column(Text, comment="原始文档内容")
    parsed_data: Mapped[dict | None] = mapped_column(JSON, comment="解析后的文档数据")
    status: Mapped[str] = mapped_column(String(32), default="uploaded", nullable=False, comment="文档状态")

    project: Mapped["Project"] = relationship(back_populates="api_documents")
    api_endpoints: Mapped[list["ApiEndpoint"]] = relationship(back_populates="api_document")
    ai_analysis_records: Mapped[list["AiAnalysisRecord"]] = relationship(back_populates="api_document")
