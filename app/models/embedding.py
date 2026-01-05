from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Embedding(Base):
    """Embedding model for vector storage"""
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    embedding_vector = Column(ARRAY(Float), nullable=False)
    model_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User")
    document = relationship("Document")

    def __repr__(self):
        return f"<Embedding(id={self.id}, document_id={self.document_id})>"
