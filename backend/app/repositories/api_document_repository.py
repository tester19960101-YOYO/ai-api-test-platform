from sqlalchemy.orm import Session

from app.models.api_document import ApiDocument


def create_api_document(db: Session, data: dict) -> ApiDocument:
    document = ApiDocument(**data)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
