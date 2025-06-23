from typing import List, Union, Optional
import os
import numpy as np
from sentence_transformers import SentenceTransformer

class TextEmbedder:
    """
    Module tạo embedding từ văn bản sử dụng sentence-transformers.
    Hỗ trợ chạy offline sau khi đã tải mô hình.
    """
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        cache_folder: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Khởi tạo mô hình embedding.
        
        Args:
            model_name: Tên mô hình sentence-transformers (mặc định: all-MiniLM-L6-v2). Có thể dùng "paraphrase-multilingual-MiniLM-L12-v2" để hỗ trợ tiếng Việt tốt hơn
            cache_folder: Thư mục lưu cache mô hình (để chạy offline)
            device: Thiết bị tính toán ("cpu" hoặc "cuda" nếu có GPU)
        """
        try:
            self.model = SentenceTransformer(
                model_name_or_path=model_name,
                cache_folder=cache_folder,
                device=device
            )
            self.vector_size = self.model.get_sentence_embedding_dimension()
            print(f"✓ Đã tải mô hình embedding: {model_name} (kích thước vector: {self.vector_size})")
        except Exception as e:
            print(f"❌ Lỗi khi tải mô hình embedding: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Tạo embedding cho một đoạn văn bản.
        
        Args:
            text: Đoạn văn bản cần tạo embedding
            
        Returns:
            Vector embedding dạng numpy array
        """
        if not text or not text.strip():
            # Trả về vector 0 nếu text rỗng
            return np.zeros(self.vector_size)
        
        try:
            return self.model.encode(text, show_progress_bar=False)
        except Exception as e:
            print(f"❌ Lỗi khi tạo embedding: {str(e)}")
            return np.zeros(self.vector_size)
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Tạo embedding cho nhiều đoạn văn bản.
        
        Args:
            texts: Danh sách các đoạn văn bản
            batch_size: Số lượng văn bản xử lý trong mỗi batch
            
        Returns:
            Ma trận các vector embedding
        """
        if not texts:
            return np.array([])
        
        # Lọc bỏ các text rỗng
        texts = [t for t in texts if t and t.strip()]
        
        if not texts:
            return np.array([])
        
        try:
            return self.model.encode(
                texts, 
                batch_size=batch_size,
                show_progress_bar=len(texts) > 10
            )
        except Exception as e:
            print(f"❌ Lỗi khi tạo embedding batch: {str(e)}")
            return np.zeros((len(texts), self.vector_size))
    
    def get_vector_size(self) -> int:
        """Trả về kích thước của vector embedding"""
        return self.vector_size
    
    def is_ready(self) -> bool:
        """Kiểm tra xem mô hình đã sẵn sàng chưa"""
        return self.model is not None


# Hàm tiện ích để tạo embedder singleton
_embedder_instance = None

def get_embedder(
    model_name: str = "all-MiniLM-L6-v2", 
    cache_folder: Optional[str] = None,
    force_new: bool = False
) -> TextEmbedder:
    """
    Trả về instance của TextEmbedder (singleton pattern).
    
    Args:
        model_name: Tên mô hình sentence-transformers
        cache_folder: Thư mục lưu cache mô hình
        force_new: Tạo mới instance ngay cả khi đã có
        
    Returns:
        Instance của TextEmbedder
    """
    global _embedder_instance
    
    if _embedder_instance is None or force_new:
        print(f"🔄 Khởi tạo embedder với model: {model_name}")
        _embedder_instance = TextEmbedder(
            model_name=model_name,
            cache_folder=cache_folder
        )
    
    return _embedder_instance
