import sys
import os  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ui.desktop.ui import start_desktop_ui
from app.search.retriever import get_retriever 

def print_colored(text, color=None):
    """In màu text trên terminal"""
    colors = {
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'end': '\033[0m'
    }
    
    if color and color in colors:
        print(f"{colors[color]}{text}{colors['end']}")
    else:
        print(text)

def setup_environment():
    """Thiết lập môi trường""" 
    
    # Xác minh thư mục documents đã tồn tại
    docs_dir = "data/documents"
    if not os.path.exists(docs_dir):
        print_colored(f"❌ Không tìm thấy thư mục {docs_dir}!", "red")
        print_colored(f"Tạo thư mục {docs_dir} và thêm các file PDF, DOCX, PPTX để tìm kiếm và phân loại.", "yellow")
        os.makedirs(docs_dir, exist_ok=True)
    
    # Kiểm tra thư mục vector store
    vector_store_dir = "data/vector_store"
    if not os.path.exists(vector_store_dir):
        os.makedirs(vector_store_dir, exist_ok=True)
    
    # Index các file - force reindex để đảm bảo dùng model mới
    print_colored("Đang đánh chỉ mục các file văn bản...", "blue")
    retriever = get_retriever()
    
    # Liệt kê file để kiểm tra
    file_count = 0
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.pptx', '.doc', '.ppt')) and not file.startswith('.'):
                file_count += 1
                print_colored(f"  - {file}", "blue")
    
    if file_count == 0:
        print_colored("⚠️ Không tìm thấy file nào trong thư mục documents!", "yellow")
        return True
        
    # Force reindex với model mới
    if retriever.index_files(force_reindex=True):
        print_colored(f"✓ Đã đánh chỉ mục xong {file_count} file!", "green")
    else:
        print_colored("⚠️ Không có file nào được đánh chỉ mục", "yellow")
    
    return True

def main(): 
    """Hàm chính"""
    # Thiết lập môi trường
    # setup_environment()
    
    # Khởi chạy giao diện desktop
    print_colored("Starting desktop UI...", "blue")
    start_desktop_ui()

if __name__ == "__main__":
    main()
    
