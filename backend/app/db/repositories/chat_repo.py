from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from app.db.mongo import get_database


SESSIONS_COLLECTION = "chat_sessions"
MESSAGES_COLLECTION = "chat_messages"


def create_chat_session(
    title: str,
    user_id: str,
    document_id: Optional[str] = None,
    document_ids: Optional[List[str]] = None,
) -> Dict:
    db = get_database()
    collection = db[SESSIONS_COLLECTION]

    now = datetime.now(timezone.utc)

    session = {
        "session_id": f"session_{uuid4()}",
        "title": title,
        "user_id": user_id,
        "document_id": document_id,
        "document_ids": document_ids or ([document_id] if document_id else []),
        "created_at": now,
        "updated_at": now,
    }

    collection.insert_one(session)
    session.pop("_id", None)

    return session


def list_chat_sessions(
    user_id: str,
    limit: int = 20,
) -> List[Dict]:
    db = get_database()
    collection = db[SESSIONS_COLLECTION]

    cursor = (
        collection.find({"user_id": user_id}, {"_id": 0})
        .sort("updated_at", -1)
        .limit(limit)
    )

    return list(cursor)


def get_chat_session(
    session_id: str,
    user_id: Optional[str] = None,
) -> Optional[Dict]:
    db = get_database()
    collection = db[SESSIONS_COLLECTION]

    query = {"session_id": session_id}

    if user_id:
        query["user_id"] = user_id

    return collection.find_one(query, {"_id": 0})


def update_session_timestamp(session_id: str) -> None:
    db = get_database()
    collection = db[SESSIONS_COLLECTION]

    collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


def create_chat_message(
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict]] = None,
) -> Dict:
    db = get_database()
    collection = db[MESSAGES_COLLECTION]

    message = {
        "message_id": f"msg_{uuid4()}",
        "session_id": session_id,
        "role": role,
        "content": content,
        "sources": sources or [],
        "created_at": datetime.now(timezone.utc),
    }

    collection.insert_one(message)
    message.pop("_id", None)

    update_session_timestamp(session_id)

    return message


def list_chat_messages(
    session_id: str,
    limit: int = 50,
) -> List[Dict]:
    db = get_database()
    collection = db[MESSAGES_COLLECTION]

    cursor = (
        collection.find({"session_id": session_id}, {"_id": 0})
        .sort("created_at", 1)
        .limit(limit)
    )

    return list(cursor)


def get_recent_messages(
    session_id: str,
    limit: int = 6,
) -> List[Dict]:
    db = get_database()
    collection = db[MESSAGES_COLLECTION]

    cursor = (
        collection.find({"session_id": session_id}, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )

    messages = list(cursor)
    messages.reverse()

    return messages


def delete_chat_session(
    session_id: str,
    user_id: str,
) -> bool:
    db = get_database()
    sessions_collection = db[SESSIONS_COLLECTION]
    messages_collection = db[MESSAGES_COLLECTION]

    session = sessions_collection.find_one(
        {
            "session_id": session_id,
            "user_id": user_id,
        }
    )

    if not session:
        return False

    messages_collection.delete_many(
        {
            "session_id": session_id,
        }
    )

    result = sessions_collection.delete_one(
        {
            "session_id": session_id,
            "user_id": user_id,
        }
    )

    return result.deleted_count > 0