from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class IngestTextRequest(BaseModel):
    title: Optional[str] = "Untitled Document"
    text: str
    user_id: Optional[str] = "demo_user"
    chunk_size: Optional[int] = 120
    chunk_overlap: Optional[int] = 30


class IngestTextResponse(BaseModel):
    document_id: str
    title: str
    user_id: str
    chunk_count: int
    message: str


class UploadTextFileResponse(BaseModel):
    document_id: str
    title: str
    file_name: str
    user_id: str
    chunk_count: int
    message: str


class UploadDocxFileResponse(BaseModel):
    document_id: str
    title: str
    file_name: str
    user_id: str
    chunk_count: int
    message: str


class UploadPdfFileResponse(BaseModel):
    document_id: str
    title: str
    file_name: str
    user_id: str
    page_count: int
    chunk_count: int
    message: str


class DocumentItem(BaseModel):
    document_id: str
    title: str
    user_id: str
    chunk_count: int
    source_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class ListDocumentsResponse(BaseModel):
    documents: List[DocumentItem]
    count: int
    

class DeleteDocumentResponse(BaseModel):
    document_id: str
    user_id: str
    deleted: bool
    message: str
    
    
