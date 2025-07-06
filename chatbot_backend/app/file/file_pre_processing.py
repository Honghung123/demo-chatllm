import re
from typing import List


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Xử lý Unicode lỗi và khoảng trắng
    text = text.encode("utf-8", errors="ignore").decode("utf-8")
    text = re.sub(r'\s+', ' ', text).strip()

    # Loại bỏ một số ký tự nhiễu nhưng giữ lại từ, chữ hoa, số, dấu chấm, phẩy
    text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)

    return text


def chunk_text_by_words(text: str, chunk_size: int = 150, overlap: int = 30) -> List[str]:
    if not text:
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def preprocess_text(text: str) -> List[str]:
    cleaned = clean_text(text)
    chunks = chunk_text_by_words(cleaned)
    return chunks
