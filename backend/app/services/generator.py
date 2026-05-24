from typing import Dict, List, Optional

from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


def build_context_text(contexts: List[Dict]) -> str:
    if not contexts:
        return ""

    context_parts = []

    for idx, item in enumerate(contexts, start=1):
        source_text = item.get("text", "")
        score = item.get("score", "")
        document_id = item.get("document_id", "")
        chunk_index = item.get("chunk_index", "")
        page = item.get("page", "")

        context_parts.append(
            f"""
[Source {idx}]
Document ID: {document_id}
Chunk index: {chunk_index}
Page: {page}
Similarity score: {score}
Content:
{source_text}
""".strip()
        )

    return "\n\n".join(context_parts)


def build_history_text(chat_history: Optional[List[Dict]]) -> str:
    if not chat_history:
        return ""

    lines = []

    for message in chat_history:
        role = message.get("role", "")
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def generate_answer(
    question: str,
    contexts: List[Dict],
    chat_history: Optional[List[Dict]] = None,
) -> str:
    context_text = build_context_text(contexts)
    history_text = build_history_text(chat_history)

    user_prompt = f"""
Bạn là trợ lý hỏi đáp tài liệu trong dự án Smart Document Assistant RAG.

Nhiệm vụ:
- Chỉ trả lời dựa trên phần Context được cung cấp.
- Có thể dùng Chat history để hiểu câu hỏi nối tiếp của người dùng.
- Nếu Context không có thông tin đủ để trả lời, hãy nói: "Mình chưa tìm thấy thông tin này trong tài liệu được cung cấp."
- Trả lời bằng tiếng Việt.
- Trả lời rõ ràng, ngắn gọn.
- Cuối câu trả lời, thêm mục "Nguồn tham khảo" và ghi rõ Source number, Document ID, Page, Chunk index nếu có.

Chat history:
{history_text}

Context:
{context_text}

Câu hỏi của người dùng:
{question}
""".strip()

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "You are a careful document question-answering assistant.",
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
        max_tokens=800,
    )

    return response.choices[0].message.content