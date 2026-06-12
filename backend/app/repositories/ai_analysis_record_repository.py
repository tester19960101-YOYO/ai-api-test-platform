from sqlalchemy.orm import Session

from app.models.ai_analysis_record import AiAnalysisRecord


def create_ai_analysis_record(db: Session, data: dict) -> AiAnalysisRecord:
    record = AiAnalysisRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
