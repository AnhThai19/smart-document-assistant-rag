from fastapi import APIRouter, HTTPException, Query

from app.services.question_rewriter import rewrite_question
from app.db.repositories.chat_repo import (
    create_chat_message,
    create_chat_session,
    delete_chat_session,
    get_chat_session,
    get_recent_messages,
    list_chat_messages,
    list_chat_sessions,
)
from app.schemas.chat_schema import (
    ChatSessionDetailResponse,
    ChatTestRequest,
    ChatTestResponse,
    CreateChatSessionRequest,
    CreateChatSessionResponse,
    DeleteChatSessionResponse,
    ListChatSessionsResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.embedder import embed_text
from app.services.generator import generate_answer
from app.services.vector_store import search_similar_chunks


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/test", response_model=ChatTestResponse)
def chat_test(request: ChatTestRequest):
    """
    Test RAG chat flow without saving chat history.
    """
    try:
        query_embedding = embed_text(request.question)

        contexts = search_similar_chunks(
            query_embedding=query_embedding,
            top_k=request.top_k,
            document_id=request.document_id,
            user_id=request.user_id,
        )

        if not contexts:
            return ChatTestResponse(
                question=request.question,
                answer="Mình chưa tìm thấy thông tin liên quan trong tài liệu được cung cấp.",
                sources=[],
            )

        answer = generate_answer(
            question=request.question,
            contexts=contexts,
        )

        return ChatTestResponse(
            question=request.question,
            answer=answer,
            sources=contexts,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat test failed: {str(exc)}",
        )


@router.post("/sessions", response_model=CreateChatSessionResponse)
def create_session(request: CreateChatSessionRequest):
    """
    Create a new chat session.
    """
    try:
        session = create_chat_session(
            title=request.title,
            user_id=request.user_id,
            document_id=request.document_id,
            document_ids=request.document_ids,
        )

        return CreateChatSessionResponse(
            session_id=session["session_id"],
            title=session["title"],
            user_id=session["user_id"],
            document_id=session.get("document_id"),
            document_ids=session.get("document_ids"),
            message="Chat session created successfully.",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Create chat session failed: {str(exc)}",
        )


@router.get("/sessions", response_model=ListChatSessionsResponse)
def get_sessions(
    user_id: str = Query(default="demo_user"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    List chat sessions by user_id.
    """
    try:
        sessions = list_chat_sessions(
            user_id=user_id,
            limit=limit,
        )

        return ListChatSessionsResponse(
            sessions=sessions,
            count=len(sessions),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"List chat sessions failed: {str(exc)}",
        )


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_session_detail(
    session_id: str,
    user_id: str = Query(default="demo_user"),
):
    """
    Get chat session detail with messages.
    """
    try:
        session = get_chat_session(
            session_id=session_id,
            user_id=user_id,
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found.",
            )

        messages = list_chat_messages(session_id=session_id)

        return ChatSessionDetailResponse(
            session=session,
            messages=messages,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Get chat session detail failed: {str(exc)}",
        )


@router.delete("/sessions/{session_id}", response_model=DeleteChatSessionResponse)
def delete_session(
    session_id: str,
    user_id: str = Query(default="demo_user"),
):
    """
    Delete a chat session and all messages in that session.
    """
    try:
        deleted = delete_chat_session(
            session_id=session_id,
            user_id=user_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found.",
            )

        return DeleteChatSessionResponse(
            session_id=session_id,
            user_id=user_id,
            deleted=True,
            message="Chat session deleted successfully.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Delete chat session failed: {str(exc)}",
        )


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
    session_id: str,
    request: SendMessageRequest,
):
    """
    Send a message in a chat session:
    save user message -> retrieve context -> generate answer -> save assistant message.
    """
    try:
        session = get_chat_session(
            session_id=session_id,
            user_id=request.user_id,
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found.",
            )

        document_ids = request.document_ids or session.get("document_ids") or []

        if request.document_id and request.document_id not in document_ids:
            document_ids.append(request.document_id)

        if not document_ids and session.get("document_id"):
            document_ids = [session.get("document_id")]

        create_chat_message(
            session_id=session_id,
            role="user",
            content=request.question,
            sources=[],
        )

        recent_messages = get_recent_messages(
            session_id=session_id,
            limit=6,
        )

        rewritten_question = rewrite_question(
            question=request.question,
            chat_history=recent_messages,
        )

        query_embedding = embed_text(rewritten_question)

        contexts = search_similar_chunks(
            query_embedding=query_embedding,
            top_k=request.top_k,
            document_ids=document_ids,
            user_id=request.user_id,
        )

        if not contexts:
            answer = "Mình chưa tìm thấy thông tin liên quan trong tài liệu được cung cấp."
            sources = []
        else:
            answer = generate_answer(
                question=rewritten_question,
                contexts=contexts,
                chat_history=recent_messages,
            )
            sources = contexts

        create_chat_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=sources,
        )

        return SendMessageResponse(
            session_id=session_id,
            question=request.question,
            rewritten_question=rewritten_question,
            answer=answer,
            sources=sources,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Send message failed: {str(exc)}",
        )