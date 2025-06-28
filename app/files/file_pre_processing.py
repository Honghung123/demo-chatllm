import re
import unicodedata
from typing import List
from unidecode import unidecode
import nltk

# Download stopwords (in English) if not already available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words('english'))

# chunk_text: function to split text into smaller chunks
# with a specified size and overlap (overlap helps maintain context between chunks)
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


def normalize_text(text: str) -> str:
    if not text:
        return ""
    
    # endcode to handle non-UTF-8 characters
    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    # Bỏ dấu (ví dụ: tiếng Việt → khong dau)
    text = unidecode(text)

    # Lowercase
    text = text.lower()

    # remove punctuation and special characters(except letters, numbers, and spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# clean_text: function to remove stop words from the text
def clean_text(text: str, language: str = "english") -> str:
    words = text.split()
    cleaned_words = [word for word in words if word not in STOP_WORDS]
    return " ".join(cleaned_words)


# preprocess_text: function to normalize, clean, and chunk the text
# combines to pipelines
def preprocess_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    normalized = normalize_text(text)
    cleaned = clean_text(normalized)
    chunks = chunk_text(cleaned, chunk_size, overlap)
    return chunks
