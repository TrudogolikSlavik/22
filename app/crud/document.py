from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class CRUDDocument:
    """CRUD operations for documents"""

    def get_by_id(
        self,
        db: Session,
        doc_id: int,
        owner_id: int
    ) -> Optional[Document]:
        """Get document by ID for specific owner"""
        return db.query(Document).filter(
            Document.id == doc_id,
            Document.owner_id == owner_id
        ).first()

    def get_all_by_owner(
        self,
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get all documents for owner with pagination"""
        return db.query(Document).filter(
            Document.owner_id == owner_id
        ).offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        doc_data: DocumentCreate,
        owner_id: int
    ) -> Document:
        """Create new document"""
        doc = Document(**doc_data.model_dump(), owner_id=owner_id)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def create_with_file(
        self,
        db: Session,
        doc_data: DocumentCreate,
        owner_id: int,
        file_meta: Dict
    ) -> Document:
        """Create document with file metadata"""
        doc = Document(
            **doc_data.model_dump(),
            owner_id=owner_id,
            file_path=file_meta["file_path"],
            file_name=file_meta["file_name"],
            file_size=file_meta["file_size"],
            file_type=file_meta["file_type"]
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def update(
        self,
        db: Session,
        doc_id: int,
        doc_data: DocumentUpdate,
        owner_id: int
    ) -> Optional[Document]:
        """Update document"""
        doc = self.get_by_id(db, doc_id, owner_id)
        if doc:
            update_data = doc_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(doc, field, value)

            db.commit()
            db.refresh(doc)
        return doc

    def delete(
        self,
        db: Session,
        doc_id: int,
        owner_id: int
    ) -> bool:
        """Delete document"""
        doc = self.get_by_id(db, doc_id, owner_id)
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False


crud_document = CRUDDocument()
