from typing import Dict, List, Optional
from uuid import uuid4

from app.db.repositories.document_repo import create_document_metadata
from app.services.chunker import chunk_pages, chunk_text
from app.services.embedder import embed_texts
from app.services.vector_store import upsert_chunks


def ingest_text_document(
    text: str,
    title: str,
    user_id: str,
    source_type: str = "text",
    chunk_size: int = 120,
    chunk_overlap: int = 30,
) -> Dict:
    """
    Ingest a raw text document into the RAG system.

    Flow:
    text -> chunks -> embeddings -> Pinecone -> MongoDB metadata
    """
    if not text or not text.strip():
        raise ValueError("Text content cannot be empty.")

    document_id = f"doc_{uuid4()}"

    chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        raise ValueError("No chunks were created from the provided text.")

    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(chunk_texts)

    upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        user_id=user_id,
    )

    create_document_metadata(
        document_id=document_id,
        title=title,
        user_id=user_id,
        chunk_count=len(chunks),
        source_type=source_type,
    )

    return {
        "document_id": document_id,
        "title": title,
        "user_id": user_id,
        "chunk_count": len(chunks),
        "source_type": source_type,
    }


def ingest_pages_document(
    pages: List[Dict],
    title: str,
    user_id: str,
    source_type: str,
    chunk_size: int = 120,
    chunk_overlap: int = 30,
    extra_metadata: Optional[Dict] = None,
) -> Dict:
    """
    Ingest a document represented as pages into the RAG system.

    Used for PDF and DOCX.

    Flow:
    pages -> chunks with page metadata -> embeddings -> Pinecone -> MongoDB metadata
    """
    if not pages:
        raise ValueError("No readable text was found in the uploaded document.")

    document_id = f"doc_{uuid4()}"

    chunks = chunk_pages(
        pages=pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        raise ValueError("No chunks were created from the uploaded document.")

    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(chunk_texts)

    upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        user_id=user_id,
    )

    create_document_metadata(
        document_id=document_id,
        title=title,
        user_id=user_id,
        chunk_count=len(chunks),
        source_type=source_type,
    )

    result = {
        "document_id": document_id,
        "title": title,
        "user_id": user_id,
        "chunk_count": len(chunks),
        "source_type": source_type,
    }

    if extra_metadata:
        result.update(extra_metadata)

    return result