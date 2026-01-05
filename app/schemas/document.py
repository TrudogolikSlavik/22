from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema"""
    title: str
    content: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    owner_id: int
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NoteCreate(BaseModel):
    """Schema for creating a note"""
    title: str
    content: str
    extract_keywords: bool = False


class AIAnalysisResult(BaseModel):
    """Schema for AI analysis results"""
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class DocumentWithAnalysis(DocumentResponse):
    """Extended document schema with AI analysis"""
    ai_analysis: Optional[AIAnalysisResult] = None
