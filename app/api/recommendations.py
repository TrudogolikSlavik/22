
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.services.ai_service import ai_service

router = APIRouter()


@router.get("/documents/{document_id}/similar")
def get_similar_documents(
    document_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get similar documents"""
    target_document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not target_document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get all user documents (except target)
    all_documents = db.query(Document).filter(
        Document.owner_id == current_user.id,
        Document.id != document_id
    ).all()

    # Convert to dicts for processing
    documents_data = [
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content or "",
            "file_type": doc.file_type
        }
        for doc in all_documents
    ]

    # Find similar documents using AI service
    target_text = target_document.content or target_document.title
    similar_docs = ai_service.find_similar_documents(
        target_text,
        documents_data,
        top_k
    )

    return {
        "target_document": {
            "id": target_document.id,
            "title": target_document.title
        },
        "similar_documents": similar_docs
    }


@router.get("/clusters")
def get_document_clusters(
    num_clusters: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cluster documents by topics"""
    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).all()

    if not documents:
        return {"clusters": []}

    # Convert to dicts for processing
    documents_data = [
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content or "",
            "file_type": doc.file_type,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]

    # Cluster documents
    clusters = ai_service.cluster_documents(documents_data, num_clusters)

    return {
        "total_documents": len(documents),
        "clusters": clusters
    }
