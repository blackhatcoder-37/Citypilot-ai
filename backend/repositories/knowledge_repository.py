"""
Knowledge document repository — all database queries for knowledge documents.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import KnowledgeDocument


class KnowledgeRepository:
    """Data-access layer for the knowledge_documents table."""

    @staticmethod
    def create(db: Session, doc: KnowledgeDocument) -> KnowledgeDocument:
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_all(db: Session) -> list[KnowledgeDocument]:
        return (
            db.query(KnowledgeDocument)
            .order_by(KnowledgeDocument.upload_date.desc())
            .all()
        )

    @staticmethod
    def get_count(db: Session) -> int:
        return db.query(func.count(KnowledgeDocument.id)).scalar() or 0

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> list[KnowledgeDocument]:
        return (
            db.query(KnowledgeDocument)
            .order_by(KnowledgeDocument.upload_date.desc())
            .limit(limit)
            .all()
        )
