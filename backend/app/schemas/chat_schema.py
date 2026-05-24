from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatTestRequest(BaseModel):
    question: str
    document_id: Optional[str] = "demo_doc_001"
    user_id: Optional[str] = "demo_user"
    top_k: Optional[int] = 3


class SourceItem(BaseModel):
    id: str
    score: float
    text: str
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None
    page: Optional[int] = None


class ChatTestResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceItem]


class CreateChatSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"
    user_id: Optional[str] = "demo_user"
    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None


class ChatSessionItem(BaseModel):
    session_id: str
    title: str
    user_id: str
    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class CreateChatSessionResponse(BaseModel):
    session_id: str
    title: str
    user_id: str
    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    message: str


class ListChatSessionsResponse(BaseModel):
    sessions: List[ChatSessionItem]
    count: int


class ChatMessageItem(BaseModel):
    message_id: str
    session_id: str
    role: str
    content: str
    sources: Optional[List[SourceItem]] = []
    created_at: datetime


class ChatSessionDetailResponse(BaseModel):
    session: ChatSessionItem
    messages: List[ChatMessageItem]


class SendMessageRequest(BaseModel):
    question: str
    user_id: Optional[str] = "demo_user"
    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    top_k: Optional[int] = 3


class SendMessageResponse(BaseModel):
    session_id: str
    question: str
    rewritten_question: Optional[str] = None
    answer: str
    sources: List[SourceItem]
    
    
class DeleteChatSessionResponse(BaseModel):
    session_id: str
    user_id: str
    deleted: bool
    message: str
    
    
