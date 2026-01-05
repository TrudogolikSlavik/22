import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.file_utils import delete_file, save_upload_file
from app.crud.document import crud_document
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    NoteCreate,
)
from app.services.ai_service import ai_service
from app.services.text_extraction import text_extraction_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for current user"""
    return crud_document.get_all_by_owner(db, current_user.id, skip, limit)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific document by ID"""
    doc = crud_document.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return doc


@router.post("/", response_model=DocumentResponse)
def create_document_endpoint(
    doc_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document with automatic summarization"""
    document = crud_document.create(db, doc_data, current_user.id)

    # Auto summarize if content is long
    if document.content and len(document.content) > 500:
        try:
            ai_service.summarize_text(document.content)
            logger.info(f"Generated summary for document {document.id}")
        except Exception as e:
            logger.error(f"Error generating summary: {e}")

    return document


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    auto_summarize: bool = Form(True),
    extract_keywords_enabled: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload file with AI processing"""
    file_meta = None
    try:
        # Save uploaded file
        file_meta = await save_upload_file(file, current_user.id)

        # Extract text from file
        extracted_text = text_extraction_service.extract_text_from_file(
            file_meta["file_path"]
        )

        # Process with AI
        final_content = extracted_text or ""
        summary = None
        keywords = []

        if auto_summarize and final_content:
            summary = ai_service.summarize_text(final_content)

        if extract_keywords_enabled and final_content:
            keywords = ai_service.extract_keywords(final_content)

        # Use filename as title if not provided
        document_title = title or file.filename

        # Create database record
        doc_data = DocumentCreate(
            title=document_title,
            content=final_content
        )

        document = crud_document.create_with_file(
            db,
            doc_data,
            current_user.id,
            file_meta
        )

        # Log AI results
        if summary or keywords:
            logger.info(
                f"AI results for doc {document.id}: "
                f"summary={bool(summary)}, keywords={keywords}"
            )

        return document

    except Exception as e:
        if file_meta and "file_path" in file_meta:
            delete_file(file_meta["file_path"])
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/{doc_id}/analyze")
def analyze_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze document with AI"""
    document = crud_document.get_by_id(db, doc_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not document.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no content to analyze"
        )

    try:
        # Generate AI analysis
        summary = ai_service.summarize_text(document.content)
        keywords = ai_service.extract_keywords(document.content)
        categories = ai_service.categorize_document(document.content)

        return {
            "document_id": document.id,
            "summary": summary,
            "keywords": keywords,
            "categories": categories,
            "content_length": len(document.content)
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing document: {str(e)}"
        )


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int,
    doc_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document"""
    doc = crud_document.update(db, doc_id, doc_data, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return doc


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete document"""
    # Get document before deletion
    doc = crud_document.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete file from disk if exists
    if doc.file_path:
        delete_file(doc.file_path)

    # Delete from database
    success = crud_document.delete(db, doc_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"message": "Document deleted successfully"}


@router.post("/upload-web")
async def upload_document_web(
    request: Request,
    db: Session = Depends(get_db)
):
    """Simplified file upload for web interface"""
    try:
        # Get user from session
        from app.core.sessions import get_session

        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        user = db.query(User).filter(User.id == session["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Process form
        form = await request.form()
        file = form.get("file")
        title = form.get("title", "")

        if not file or not hasattr(file, "file"):
            raise HTTPException(status_code=400, detail="No file provided")

        # Save file
        file_meta = await save_upload_file(file, user.id)

        # Create database record
        doc_data = DocumentCreate(
            title=title or file.filename,
            content=f"Uploaded file: {file.filename}"
        )

        document = crud_document.create_with_file(
            db,
            doc_data,
            user.id,
            file_meta
        )

        return {
            "success": True,
            "document": {
                "id": document.id,
                "title": document.title,
                "file_type": document.file_type,
                "file_size": document.file_size
            }
        }

    except Exception as e:
        logger.error(f"Error in web upload: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/create-note", response_model=DocumentResponse)
async def create_note_endpoint(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a note with optional keyword extraction"""
    # Create basic document first
    doc_data = DocumentCreate(
        title=note_data.title,
        content=note_data.content
    )
    document = crud_document.create(db, doc_data, current_user.id)

    # Extract keywords if requested
    if note_data.extract_keywords and note_data.content:
        try:
            keywords = ai_service.extract_keywords(note_data.content)
            logger.info(f"Extracted keywords for note {document.id}: {keywords}")
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")

    return document
