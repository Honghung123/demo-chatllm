# Tách nội dung, chia đoạn (chunking) 

from typing import List

"""
Overlap giúp các đoạn văn bản sau khi chia nhỏ vẫn giữ được ngữ cảnh liền mạch, tăng chất lượng cho các tác vụ NLP, tìm kiếm, phân loại, tóm tắt, v.v.
"""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]: 
    if not text:
        return []
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == text_length:
            break
        start += chunk_size - overlap
    return chunks
