from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.db.mongo import get_database


COLLECTION_NAME = "documents"


def create_document_metadata(
    document_id: str,
    title: str,
    user_id: str,
    chunk_count: int,
    source_type: str = "text",
) -> Dict:
    db = get_database()
    collection = db[COLLECTION_NAME]

    document = {
        "document_id": document_id,
        "title": title,
        "user_id": user_id,
        "chunk_count": chunk_count,
        "source_type": source_type,
        "status": "indexed",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    collection.insert_one(document)

    document.pop("_id", None)
    return document


def list_documents(
    user_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    db = get_database()
    collection = db[COLLECTION_NAME]

    query = {}

    if user_id:
        query["user_id"] = user_id

    cursor = (
        collection.find(query, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )

    return list(cursor)


def get_document_by_id(document_id: str) -> Optional[Dict]:
    db = get_database()
    collection = db[COLLECTION_NAME]

    return collection.find_one(
        {"document_id": document_id},
        {"_id": 0},
    )
    
    
def delete_document_by_id(
    document_id: str,
    user_id: Optional[str] = None,
) -> bool:
    db = get_database()
    collection = db[COLLECTION_NAME]

    query = {
        "document_id": document_id,
    }

    if user_id:
        query["user_id"] = user_id

    result = collection.delete_one(query)

    return result.deleted_count > 0