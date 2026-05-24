# from typing import Dict, List
# from uuid import uuid4


# def chunk_text(
#     text: str,
#     chunk_size: int = 800,
#     chunk_overlap: int = 120,
# ) -> List[Dict]:
#     if not text or not text.strip():
#         return []

#     cleaned_text = " ".join(text.split())

#     chunks = []
#     start = 0
#     text_length = len(cleaned_text)
#     chunk_index = 0

#     while start < text_length:
#         end = start + chunk_size
#         chunk = cleaned_text[start:end]

#         chunks.append(
#             {
#                 "chunk_id": str(uuid4()),
#                 "chunk_index": chunk_index,
#                 "text": chunk,
#             }
#         )

#         chunk_index += 1
#         start = end - chunk_overlap

#         if start <= 0:
#             start = end

#     return chunks

from typing import Dict, List
from uuid import uuid4


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> List[Dict]:
    if not text or not text.strip():
        return []

    words = text.split()

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words)

        chunks.append(
            {
                "chunk_id": str(uuid4()),
                "chunk_index": chunk_index,
                "text": chunk_text_value,
            }
        )

        chunk_index += 1
        start = end - chunk_overlap

        if start <= 0:
            start = end

    return chunks


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 120,
    chunk_overlap: int = 30,
) -> List[Dict]:
    """
    Chunk extracted PDF pages while keeping page number metadata.
    """
    all_chunks = []
    global_chunk_index = 0

    for page in pages:
        page_number = page["page"]
        page_text = page["text"]

        page_chunks = chunk_text(
            text=page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk in page_chunks:
            chunk["chunk_index"] = global_chunk_index
            chunk["page"] = page_number
            all_chunks.append(chunk)
            global_chunk_index += 1

    return all_chunks