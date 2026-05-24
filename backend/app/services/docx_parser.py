from io import BytesIO
from typing import Dict, List

from docx import Document


def extract_text_from_docx(file_bytes: bytes) -> List[Dict]:
    """
    Extract text from DOCX bytes.

    Returns:
        [
            {
                "page": None,
                "text": "..."
            }
        ]

    DOCX does not have reliable page numbers like PDF, so page is set to None.
    """
    document = Document(BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)

    if not full_text.strip():
        return []

    return [
        {
            "page": None,
            "text": full_text,
        }
    ]