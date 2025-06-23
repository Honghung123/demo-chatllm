# Hướng dẫn cài đặt thư viện cho dự án Chat AI Local LLM

Dựa trên requirement và plan của dự án, bạn cần cài đặt các thư viện sau để xây dựng hệ thống đầy đủ:

## 1. Thư viện xử lý Semantic Search

### sentence-transformers
- Tạo embedding vector từ văn bản, hỗ trợ nhiều mô hình pre-trained, chạy tốt offline.

```bash
pip install sentence-transformers
```

### faiss-cpu
- Thư viện lưu trữ và tìm kiếm vector hiệu quả, phù hợp cho ứng dụng offline, quy mô vừa và nhỏ.

```bash
pip install faiss-cpu
```

### (Tùy chọn) chromadb
- Vector database hiện đại, dễ dùng, có thể dùng thay thế faiss nếu cần tính năng phức tạp hơn.

```bash
pip install chromadb
```

## 2. Thư viện xử lý File

### PyPDF2
- Đọc và trích xuất nội dung từ file PDF.

```bash
pip install PyPDF2
```

### python-docx
- Đọc và trích xuất nội dung từ file Word (.docx).

```bash
pip install python-docx
```

### python-pptx
- Đọc và trích xuất nội dung từ file PowerPoint (.pptx).

```bash
pip install python-pptx
```

## 3. LLM Local

### Ollama
- Cài đặt Ollama từ trang chủ: https://ollama.com/download
- Sau khi cài đặt, cài thêm Python binding:

```bash
pip install ollama
```

### (Hoặc) llama-cpp-python
- Nếu dùng llama.cpp thay vì Ollama:

```bash
pip install llama-cpp-python
```

## 4. Thư viện hỗ trợ khác

### Giao diện người dùng
```bash
pip install PyQt6  # Giao diện desktop
# hoặc
pip install gradio  # Giao diện web đơn giản
```

### Xử lý dữ liệu và xuất file
```bash
pip install pandas openpyxl  # Để xuất metadata ra Excel
pip install pydantic  # Để định nghĩa schema cho MCP
pip install requests  # Để gửi HTTP request
```

---

## Cài đặt mô hình Embedding Offline

Để chạy hoàn toàn offline, bạn cần tải trước mô hình embedding:

```python
# Chạy một lần để tải mô hình về máy
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # Mô hình nhỏ, hiệu quả
# hoặc
# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Hỗ trợ tiếng Việt tốt hơn
```

Mô hình sẽ được lưu vào thư mục cache và có thể sử dụng offline sau đó.

## Ví dụ sử dụng Semantic Search

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 1. Khởi tạo mô hình embedding
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Tạo embedding từ các đoạn văn bản
texts = [
    "Kế hoạch marketing năm 2024",
    "Báo cáo tài chính quý 1/2024",
    "Chiến lược phát triển sản phẩm mới"
]
embeddings = model.encode(texts)

# 3. Tạo FAISS index để tìm kiếm
dimension = embeddings.shape[1]  # Số chiều của vector embedding
index = faiss.IndexFlatL2(dimension)  # Dùng L2 distance
index.add(np.array(embeddings).astype('float32'))

# 4. Tìm kiếm với câu query
query = "Kế hoạch marketing"
query_vector = model.encode([query])[0].reshape(1, -1).astype('float32')
distances, indices = index.search(query_vector, k=2)  # Tìm 2 kết quả gần nhất

# 5. Hiển thị kết quả
for i, idx in enumerate(indices[0]):
    print(f"Kết quả {i+1}: {texts[idx]} (độ tương đồng: {1-distances[0][i]:.2f})")
```

---

**Khuyến nghị:**
- Để tối ưu cho pipeline tìm kiếm semantic offline, chỉ cần `sentence-transformers` và `faiss-cpu` là đủ.
- Nên sử dụng mô hình embedding nhỏ như `all-MiniLM-L6-v2` để chạy tốt trên máy tính phổ thông.
- Đảm bảo tải mô hình embedding trước khi chạy offline. 