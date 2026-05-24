import time
from typing import Dict, List, Optional

from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings


EMBEDDING_DIMENSION = 3072


pc = Pinecone(api_key=settings.pinecone_api_key)


def get_or_create_index():
    index_name = settings.pinecone_index_name
    existing_indexes = [index["name"] for index in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
        )

        while True:
            description = pc.describe_index(index_name)
            if description.status["ready"]:
                break
            time.sleep(2)
    else:
        description = pc.describe_index(index_name)
        if description.dimension != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Pinecone index dimension mismatch. "
                f"Index '{index_name}' has dimension {description.dimension}, "
                f"but current embedding dimension is {EMBEDDING_DIMENSION}. "
                f"Use a new index name or delete the old index."
            )

    return pc.Index(index_name)


index = get_or_create_index()


def upsert_chunks(
    chunks: List[Dict],
    embeddings: List[List[float]],
    document_id: str,
    user_id: str = "demo_user",
) -> None:
    vectors = []

    for chunk, embedding in zip(chunks, embeddings):
        metadata = {
            "text": chunk["text"],
            "document_id": document_id,
            "user_id": user_id,
            "chunk_index": chunk.get("chunk_index", 0),
        }

        page = chunk.get("page")

        if page is not None:
            metadata["page"] = page

        vectors.append(
            {
                "id": chunk["chunk_id"],
                "values": embedding,
                "metadata": metadata,
            }
        )

    if vectors:
        index.upsert(vectors=vectors)


def search_similar_chunks(
    query_embedding: List[float],
    top_k: int = 5,
    document_id: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
    user_id: str = "demo_user",
) -> List[Dict]:
    metadata_filter = {
        "user_id": {"$eq": user_id}
    }

    if document_ids:
        metadata_filter["document_id"] = {"$in": document_ids}
    elif document_id:
        metadata_filter["document_id"] = {"$eq": document_id}

    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=metadata_filter,
    )

    matches = []

    for match in result.get("matches", []):
        metadata = match.get("metadata", {})

        matches.append(
            {
                "id": match.get("id"),
                "score": match.get("score"),
                "text": metadata.get("text"),
                "document_id": metadata.get("document_id"),
                "chunk_index": metadata.get("chunk_index"),
                "page": metadata.get("page"),
            }
        )

    return matches


def delete_document_vectors(
    document_id: str,
    user_id: str = "demo_user",
) -> None:
    """
    Delete all vectors belonging to a specific document.
    """
    index.delete(
        filter={
            "document_id": {"$eq": document_id},
            "user_id": {"$eq": user_id},
        }
    )