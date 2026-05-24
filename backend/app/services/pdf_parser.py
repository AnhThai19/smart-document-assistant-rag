from io import BytesIO
from typing import Dict, List

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> List[Dict]:
    """
    Extract text from PDF bytes page by page.

    Returns:
        [
            {
                "page": 1,
                "text": "..."
            }
        ]
    """
    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                {
                    "page": page_index,
                    "text": text.strip(),
                }
            )

    return pages