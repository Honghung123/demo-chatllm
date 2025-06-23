# FAISS hoặc ChromaDB 

import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Any, Tuple, Optional
from app.search.embedder import get_embedder
from app.files.file_loader import load_file

class VectorStore:
    """
    Lưu trữ và tìm kiếm vector embedding sử dụng FAISS
    """
    
    def __init__(self, index_path: str = "data/vector_store/faiss_index"):
        self.index_path = index_path
        self.index = None
        self.metadata = []  # Lưu thông tin đi kèm với mỗi embedding
        self.embedder = get_embedder()
        self._ensure_directory()
        
    def _ensure_directory(self):
        """Đảm bảo thư mục lưu trữ index tồn tại"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
    
    def _init_index(self, dimension: int):
        """Khởi tạo FAISS index với kích thước xác định"""
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]] = None):
        """
        Thêm các đoạn văn bản vào index
        
        Args:
            documents: Danh sách các đoạn văn bản
            metadatas: Thông tin đi kèm với mỗi đoạn văn bản
        """
        if not documents:
            return
            
        embeddings = self.embedder.embed_texts(documents)
        
        # Khởi tạo index nếu chưa có
        if self.index is None:
            self._init_index(self.embedder.get_vector_size())
        
        # Thêm embeddings vào index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Lưu metadata
        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{"text": doc} for doc in documents])
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các đoạn văn bản tương tự với câu query
        
        Args:
            query: Câu truy vấn
            top_k: Số lượng kết quả trả về
            
        Returns:
            Danh sách các kết quả phù hợp nhất
        """
        if self.index is None or self.index.ntotal == 0:
            print(f"❌ Vector store không có dữ liệu. Index là None: {self.index is None}")
            return []
            
        print(f"🔍 Tìm kiếm trong vector store với query: '{query}'")
        print(f"📊 Vector store có {self.index.ntotal} embedding vectors")
            
        # Tạo embedding cho câu query
        query_embedding = self.embedder.embed_text(query)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Tìm kiếm top_k kết quả gần nhất
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        print(f"🔢 Kết quả indices: {indices[0]}")
        print(f"📏 Kết quả distances: {distances[0]}")
        
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                result = dict(self.metadata[idx])
                result["distance"] = float(distances[0][i])
                result["score"] = 1.0 / (1.0 + float(distances[0][i]))  # Convert khoảng cách thành điểm số
                print(f"📄 Tìm thấy: {result.get('file_name')} (score: {result['score']:.4f})")
                results.append(result)
        
        if not results:
            print("⚠️ Không tìm thấy kết quả phù hợp trong vector store")
            
        return results
    
    def save(self):
        """Lưu index và metadata vào file"""
        if self.index is None:
            return False
            
        try:
            # Lưu FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Lưu metadata
            with open(f"{self.index_path}.metadata", "wb") as f:
                pickle.dump(self.metadata, f)
                
            return True
        except Exception as e:
            print(f"Lỗi khi lưu vector store: {str(e)}")
            return False
    
    def load(self) -> bool:
        """Tải index và metadata từ file"""
        if not os.path.exists(f"{self.index_path}.faiss") or not os.path.exists(f"{self.index_path}.metadata"):
            return False
            
        try:
            # Tải FAISS index
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Tải metadata
            with open(f"{self.index_path}.metadata", "rb") as f:
                self.metadata = pickle.load(f)
                
            return True
        except Exception as e:
            print(f"Lỗi khi tải vector store: {str(e)}")
            self.index = None
            self.metadata = []
            return False

# Khởi tạo singleton
_vector_store = None

def get_vector_store() -> VectorStore:
    """Hàm tiện ích để lấy instance của VectorStore"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.load()  # Cố gắng tải index nếu có
    return _vector_store

def index_documents(file_paths: List[str], force_reindex: bool = False) -> bool:
    """
    Đánh chỉ mục (index) cho các file văn bản
    
    Args:
        file_paths: Danh sách đường dẫn các file
        force_reindex: Đánh chỉ mục lại nếu đã tồn tại
        
    Returns:
        True nếu thành công, False nếu thất bại
    """
    from app.files.file_parser import chunk_text
    
    vector_store = get_vector_store()
    if vector_store.index is not None and not force_reindex:
        return True
        
    texts = []
    metadata = []
    
    for file_path in file_paths:
        try:
            content = load_file(file_path)
            if not content:
                continue
                
            # Chia nội dung thành các đoạn nhỏ hơn
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadata.append({
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
                
        except Exception as e:
            print(f"Lỗi khi đánh chỉ mục file {file_path}: {str(e)}")
    
    if texts:
        vector_store.add_documents(texts, metadata)
        vector_store.save()
        return True
    
    return False