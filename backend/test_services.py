import time
from uuid import uuid4

from google import genai
from pinecone import Pinecone, ServerlessSpec
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.core.config import settings


def test_mongodb_connection():
    print("\n[1] Testing MongoDB connection...")

    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
    )

    try:
        client.admin.command("ping")
        print("[OK] MongoDB connected successfully.")

        db = client[settings.mongodb_db_name]
        collection = db["connection_tests"]

        test_doc = {
            "message": "MongoDB test from Smart Document Assistant RAG",
            "created_at": time.time(),
        }

        result = collection.insert_one(test_doc)
        print(f"[OK] Inserted test document with _id: {result.inserted_id}")

        found_doc = collection.find_one({"_id": result.inserted_id})
        print(f"[OK] Read back document: {found_doc['message']}")

    except ServerSelectionTimeoutError as exc:
        print("[ERROR] MongoDB connection failed.")
        print(str(exc))
        raise

    finally:
        client.close()


def create_gemini_embedding(text: str):
    client = genai.Client(api_key=settings.gemini_api_key)

    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
    )

    embedding = result.embeddings[0].values
    return embedding


def test_gemini_embedding():
    print("\n[2] Testing Gemini embedding...")

    text = "Smart Document Assistant RAG dùng embedding để tìm kiếm semantic trong tài liệu."
    embedding = create_gemini_embedding(text)

    print("[OK] Gemini embedding created successfully.")
    print(f"[OK] Embedding dimension: {len(embedding)}")
    print(f"[OK] First 5 values: {embedding[:5]}")

    return embedding


def get_or_create_pinecone_index(dimension: int):
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index_name = settings.pinecone_index_name

    existing_indexes = [index["name"] for index in pc.list_indexes()]

    if index_name not in existing_indexes:
        print(f"[INFO] Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
        )

        print("[INFO] Waiting for Pinecone index to be ready...")
        while True:
            description = pc.describe_index(index_name)
            if description.status["ready"]:
                break
            time.sleep(2)

        print("[OK] Pinecone index created and ready.")
    else:
        description = pc.describe_index(index_name)
        existing_dimension = description.dimension

        if existing_dimension != dimension:
            raise ValueError(
                f"Pinecone index dimension mismatch. "
                f"Index '{index_name}' has dimension {existing_dimension}, "
                f"but Gemini embedding has dimension {dimension}. "
                f"Delete this index in Pinecone Console or use a new index name."
            )

        print(f"[OK] Pinecone index already exists: {index_name}")

    return pc.Index(index_name)


def test_pinecone_upsert_and_query(embedding):
    print("\n[3] Testing Pinecone upsert and query...")

    dimension = len(embedding)
    index = get_or_create_pinecone_index(dimension)

    vector_id = f"test-{uuid4()}"

    text = "MongoDB lưu metadata, chat history và memory. Pinecone lưu embedding để semantic search."

    index.upsert(
        vectors=[
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text": text,
                    "source": "test_services.py",
                    "user_id": "demo_user",
                },
            }
        ]
    )

    print(f"[OK] Upserted test vector: {vector_id}")

    query_text = "Pinecone dùng để làm gì trong dự án RAG?"
    query_embedding = create_gemini_embedding(query_text)

    result = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={
            "user_id": {"$eq": "demo_user"}
        },
    )

    matches = result.get("matches", [])

    if not matches:
        raise RuntimeError("Pinecone query succeeded but returned no matches.")

    print("[OK] Pinecone query returned matches.")

    for match in matches:
        print("-" * 50)
        print(f"ID: {match.get('id')}")
        print(f"Score: {match.get('score')}")
        print(f"Text: {match.get('metadata', {}).get('text')}")


def main():
    print("Starting service tests...")

    test_mongodb_connection()
    embedding = test_gemini_embedding()
    test_pinecone_upsert_and_query(embedding)

    print("\nAll service tests completed successfully.")


if __name__ == "__main__":
    main()