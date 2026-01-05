from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
def search_documents(
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search by title and content"""

    # Basic search with ILIKE for case-insensitive search
    search_filter = or_(
        Document.title.ilike(f"%{q}%"),
        Document.content.ilike(f"%{q}%")
    )

    documents = db.query(Document).filter(
        Document.owner_id == current_user.id,
        search_filter
    ).offset(skip).limit(limit).all()

    return documents


@router.get("/advanced", response_model=List[DocumentResponse])
def advanced_search(
    title: Optional[str] = Query(None, description="Search in title"),
    content: Optional[str] = Query(None, description="Search in content"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advanced search with filtering"""

    query = db.query(Document).filter(Document.owner_id == current_user.id)

    if title:
        query = query.filter(Document.title.ilike(f"%{title}%"))

    if content:
        query = query.filter(Document.content.ilike(f"%{content}%"))

    if file_type:
        query = query.filter(Document.file_type == file_type)

    documents = query.offset(skip).limit(limit).all()

    return documents
