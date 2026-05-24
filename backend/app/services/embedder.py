from typing import List

from google import genai

from app.core.config import settings


client = genai.Client(api_key=settings.gemini_api_key)


def embed_text(text: str) -> List[float]:
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
    )

    return result.embeddings[0].values


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
    )

    return [embedding.values for embedding in result.embeddings]