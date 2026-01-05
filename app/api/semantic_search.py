from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.embedding_service import embedding_service

router = APIRouter()


@router.get("/semantic", response_model=List[DocumentResponse])
def semantic_search(
    q: str = Query(..., description="Semantic search query"),
    k: int = Query(10, description="Number of results"),
    threshold: float = Query(0.3, description="Similarity threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Semantic search by meaning"""

    # Check and rebuild index if needed
    if not embedding_service.load_index(current_user.id):
        embedding_service.build_index_from_documents(db, current_user.id)

    # Perform semantic search
    results = embedding_service.semantic_search(q, k)

    # Filter by similarity threshold and get documents
    document_ids = [doc_id for doc_id, score in results if score >= threshold]

    if not document_ids:
        return []

    # Get documents from database
    documents = db.query(Document).filter(
        Document.id.in_(document_ids),
        Document.owner_id == current_user.id
    ).all()

    # Sort by relevance
    document_map = {doc.id: doc for doc in documents}
    sorted_documents = [
        document_map[doc_id] for doc_id in document_ids if doc_id in document_map
    ]

    return sorted_documents


@router.post("/rebuild-index")
def rebuild_semantic_index(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rebuild semantic index for user"""
    try:
        embedding_service.build_index_from_documents(db, current_user.id)
        return {"message": "Semantic index rebuilt successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rebuilding index: {str(e)}"
        )


@router.get("/hybrid-search", response_model=List[DocumentResponse])
def hybrid_search(
    q: str = Query(..., description="Search query"),
    semantic_weight: float = Query(0.7, description="Weight for semantic search"),
    keyword_weight: float = Query(0.3, description="Weight for keyword search"),
    limit: int = Query(20, description="Number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hybrid search: combination of semantic and keyword"""

    from sqlalchemy import or_

    # Semantic search
    semantic_results = []
    if semantic_weight > 0:
        if not embedding_service.load_index(current_user.id):
            embedding_service.build_index_from_documents(db, current_user.id)
        semantic_results = embedding_service.semantic_search(q, limit * 2)

    # Keyword search
    keyword_docs = []
    if keyword_weight > 0:
        search_filter = or_(
            Document.title.ilike(f"%{q}%"),
            Document.content.ilike(f"%{q}%")
        )
        keyword_docs = db.query(Document).filter(
            Document.owner_id == current_user.id,
            search_filter
        ).limit(limit * 2).all()

    # Combine results
    scored_docs = {}

    # Add semantic results
    for doc_id, score in semantic_results:
        scored_docs[doc_id] = scored_docs.get(doc_id, 0) + score * semantic_weight

    # Add keyword results
    for doc in keyword_docs:
        scored_docs[doc.id] = scored_docs.get(doc.id, 0) + keyword_weight

    # Sort by final score
    sorted_doc_ids = sorted(
        scored_docs.keys(),
        key=lambda x: scored_docs[x],
        reverse=True
    )[:limit]

    # Get documents
    documents = db.query(Document).filter(
        Document.id.in_(sorted_doc_ids),
        Document.owner_id == current_user.id
    ).all()

    # Maintain order
    document_map = {doc.id: doc for doc in documents}
    return [
        document_map[doc_id] for doc_id in sorted_doc_ids if doc_id in document_map
    ]
