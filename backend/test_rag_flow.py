from app.services.chunker import chunk_text
from app.services.embedder import embed_text, embed_texts
from app.services.vector_store import upsert_chunks, search_similar_chunks
from app.services.generator import generate_answer


sample_text = """
Smart Document Assistant RAG là một hệ thống hỏi đáp tài liệu thông minh.
Người dùng có thể upload tài liệu như PDF, DOCX hoặc TXT, sau đó đặt câu hỏi
dựa trên nội dung tài liệu.

Hệ thống sử dụng kỹ thuật chunking để chia tài liệu thành các đoạn nhỏ.
Mỗi đoạn nhỏ được gọi là một chunk. Sau đó, hệ thống dùng embedding model
để biến từng chunk thành vector số.

Các vector embedding được lưu vào Pinecone. Pinecone đóng vai trò là vector
database, giúp hệ thống tìm kiếm các đoạn tài liệu có ý nghĩa gần nhất với
câu hỏi của người dùng. Kiểu tìm kiếm này gọi là semantic search.

MongoDB được dùng để lưu dữ liệu ứng dụng như thông tin tài liệu, metadata,
lịch sử chat, phiên hội thoại và memory của chatbot.

Khi người dùng đặt câu hỏi, hệ thống tạo embedding cho câu hỏi đó, tìm các
chunk liên quan nhất trong Pinecone, rồi đưa các chunk này vào prompt cho LLM
để sinh câu trả lời dựa trên tài liệu.
"""


def main():
    document_id = "demo_doc_001"
    user_id = "demo_user"

    print("[1] Chunking sample text...")
    chunks = chunk_text(sample_text, chunk_size=60, chunk_overlap=15)
    print(f"[OK] Created {len(chunks)} chunks.")

    for chunk in chunks:
        print("-" * 50)
        print(f"Chunk index: {chunk['chunk_index']}")
        print(chunk["text"])

    print("\n[2] Creating embeddings for chunks with Gemini...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts)
    print(f"[OK] Created {len(embeddings)} embeddings.")
    print(f"[OK] Embedding dimension: {len(embeddings[0])}")

    print("\n[3] Upserting chunks into Pinecone...")
    upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        user_id=user_id,
    )
    print("[OK] Upsert completed.")

    print("\n[4] Searching similar chunks...")
    question = "MongoDB được dùng để làm gì trong hệ thống?"
    query_embedding = embed_text(question)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        top_k=3,
        document_id=document_id,
        user_id=user_id,
    )

    print(f"\nQuestion: {question}")
    print("\nSearch results:")

    for result in results:
        print("-" * 50)
        print(f"Score: {result['score']}")
        print(f"Chunk index: {result['chunk_index']}")
        print(f"Text: {result['text']}")

    print("\n[5] Generating final answer with Groq...")
    answer = generate_answer(
        question=question,
        contexts=results,
    )

    print("\nFinal answer:")
    print(answer)


if __name__ == "__main__":
    main()
    
    