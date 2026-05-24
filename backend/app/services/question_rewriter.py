from typing import Dict, List, Optional

from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


def build_history_text(chat_history: Optional[List[Dict]]) -> str:
    if not chat_history:
        return ""

    lines = []

    for message in chat_history:
        role = message.get("role", "")
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def rewrite_question(
    question: str,
    chat_history: Optional[List[Dict]] = None,
) -> str:
    """
    Rewrite a follow-up question into a standalone QUESTION using chat history.
    The output must be a question, not an answer.
    """
    history_text = build_history_text(chat_history)

    if not history_text.strip():
        return question

    prompt = f"""
Bạn là một bộ phận viết lại câu hỏi cho hệ thống RAG.

Nhiệm vụ duy nhất:
Viết lại Current question thành MỘT CÂU HỎI độc lập, rõ nghĩa, để dùng cho bước retrieval/search.

Quy tắc bắt buộc:
- Chỉ trả về đúng một câu hỏi.
- Câu trả về phải là câu nghi vấn.
- Không trả lời câu hỏi.
- Không biến câu hỏi thành câu khẳng định.
- Không thêm lời dẫn như "Câu hỏi đã viết lại là:".
- Không giải thích.
- Không dùng thông tin trong Chat history để trả lời.
- Chỉ dùng Chat history để hiểu các đại từ hoặc cụm mơ hồ như "nó", "cái đó", "còn ... thì sao".
- Nếu Current question đã rõ nghĩa, hãy giữ nguyên dạng câu hỏi.

Ví dụ đúng:
Current question: Còn Pinecone thì sao?
Standalone question: Pinecone được dùng để làm gì trong hệ thống Smart Document Assistant RAG?

Ví dụ sai:
Current question: Còn Pinecone thì sao?
Standalone question: Pinecone được dùng để lưu vector embedding và semantic search.

Chat history:
{history_text}

Current question:
{question}

Standalone question:
""".strip()

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You rewrite follow-up questions into standalone questions for retrieval. "
                    "Return only one question. Never answer the question."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.0,
        max_tokens=120,
    )

    rewritten = response.choices[0].message.content.strip()

    rewritten = clean_rewritten_question(
        rewritten=rewritten,
        original_question=question,
    )

    return rewritten


def clean_rewritten_question(
    rewritten: str,
    original_question: str,
) -> str:
    """
    Clean model output and make sure rewritten output is still a question.
    """
    if not rewritten or not rewritten.strip():
        return original_question

    rewritten = rewritten.strip()

    prefixes_to_remove = [
        "Câu hỏi đã viết lại là:",
        "Câu hỏi đã được viết lại là:",
        "Standalone question:",
        "Rewritten question:",
        "Câu hỏi:",
    ]

    for prefix in prefixes_to_remove:
        if rewritten.lower().startswith(prefix.lower()):
            rewritten = rewritten[len(prefix):].strip()

    lines = [line.strip() for line in rewritten.splitlines() if line.strip()]
    if lines:
        rewritten = lines[-1]

    # Nếu output là câu khẳng định, nhiều khả năng model đã trả lời thay vì rewrite.
    question_markers = [
        "?",
        " gì",
        " nào",
        " sao",
        " như thế nào",
        " làm sao",
        " vì sao",
        " tại sao",
        " bao nhiêu",
        " khi nào",
        " ở đâu",
        " ai",
        " có phải",
        " hay không",
    ]

    lower_rewritten = rewritten.lower()

    is_question = any(marker in lower_rewritten for marker in question_markers)

    if not is_question:
        # fallback: giữ lại câu hỏi gốc nếu model trả lời sai nhiệm vụ
        return original_question

    if not rewritten.endswith("?"):
        rewritten = rewritten.rstrip(".") + "?"

    return rewritten