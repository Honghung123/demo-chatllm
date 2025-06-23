from typing import List, Dict, Any, Optional
import os
from app.search.vector_store import get_vector_store, index_documents
from app.search.embedder import get_embedder

class Retriever:
    """
    Module tìm kiếm văn bản liên quan sử dụng vector store
    """
    
    def __init__(self, index_directory: str = "data/documents"):
        """
        Khởi tạo retriever
        
        Args:
            index_directory: Thư mục chứa file cần đánh chỉ mục
        """
        self.index_directory = index_directory
        self.vector_store = get_vector_store()
        
    def index_files(self, force_reindex: bool = False) -> bool:
        """
        Đánh chỉ mục các file trong thư mục
        
        Args:
            force_reindex: Đánh chỉ mục lại nếu đã tồn tại
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Lấy danh sách file trong thư mục
        file_paths = []
        for root, _, files in os.walk(self.index_directory):
            for file in files:
                if file.lower().endswith(('.pdf', '.docx', '.pptx', '.doc', '.ppt')) and not file.startswith('.'):
                    file_paths.append(os.path.join(root, file))
        
        if not file_paths:
            return False
         
        # Đánh chỉ mục các file
        return index_documents(file_paths, force_reindex)
            
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các đoạn văn bản liên quan đến query
        
        Args:
            query: Câu truy vấn
            top_k: Số lượng kết quả trả về
            
        Returns:
            Danh sách các kết quả phù hợp nhất
        """
        # Nếu chưa đánh chỉ mục, tiến hành đánh chỉ mục trước
        if not self.vector_store.index:
            self.index_files()
            
        # Tìm kiếm đoạn văn bản phù hợp
        return self.vector_store.search(query, top_k)
    
    def get_relevant_files(self, query: str) -> List[str]:
        """
        Tìm kiếm các file liên quan đến query
        
        Args:
            query: Câu truy vấn
            
        Returns:
            Danh sách đường dẫn các file phù hợp nhất (đã loại bỏ trùng lặp)
        """
        results = self.search(query, top_k=10)
        
        # Lấy danh sách các file độc nhất
        file_paths = []
        for result in results:
            file_path = result.get("file_path")
            if file_path and file_path not in file_paths:
                file_paths.append(file_path)
        
        return file_paths

# Khởi tạo singleton
_retriever_instance = None

def get_retriever(index_directory: Optional[str] = None) -> Retriever:
    """
    Lấy instance của Retriever
    
    Args:
        index_directory: Thư mục chứa file cần đánh chỉ mục
        
    Returns:
        Instance của Retriever
    """
    global _retriever_instance
    if _retriever_instance is None or index_directory:
        _retriever_instance = Retriever(index_directory or "data/documents")
    return _retriever_instance