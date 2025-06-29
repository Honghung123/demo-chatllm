# Ứng dụng Chat AI chạy Local LLM tích hợp MCP

Ứng dụng Chat AI chạy Local LLM tích hợp Model Context Protocol (MCP) để tìm kiếm và phân loại nội dung file văn bản.

## Tính năng

- 🤖 **Chat offline AI** sử dụng Ollama (không cần internet)
- 🔍 **Tìm kiếm thông minh** trong thư mục file (PDF, Word, PPT)
- 🏷️ **Phân loại tự động** file dựa trên nội dung
- 📊 **Gửi metadata** file qua MCP Cloud
- 📝 **Chain of Thought (CoT)** - giải thích quá trình xử lý
- 🔄 **RLHF** - Học từ phản hồi người dùng

## Cài đặt

### Yêu cầu

- Python 3.9+
- Ollama (đã cài đặt)
- Model Mistral (hoặc model tương đương)

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Cài đặt Ollama

1. Tải và cài đặt Ollama từ [https://ollama.ai/download](https://ollama.ai/download)
2. Tải model Mistral:
```bash
ollama pull mistral
```
- Có thể tải model khác từ [https://ollama.com/models](https://ollama.com/models)
3. Config .env file
```env
OLLAMA_MODEL=mistral
```
- Update OLLAMA_MODEL if you want to use other model

## Sử dụng

### Khởi chạy ứng dụng
- Tại root folder, chạy lệnh:
```bash
python app/main.py
```

### Chức năng hiện tại
- Tìm kiếm file và đọc nội dung file
- Tạo file mới và ghi nội dung vào file

## Tính năng nâng cao

### Agentic AI
Tự động thực hiện chuỗi hành động: tìm file → index nội dung → phân loại → xuất metadata

### Chain of Thought (CoT)
Mỗi kết quả tìm kiếm sẽ đi kèm với giải thích quy trình xử lý để người dùng hiểu cách AI đưa ra kết quả.

### RLHF (Reinforcement Learning from Human Feedback)
Học từ phản hồi người dùng để cải thiện phân loại file trong những lần tìm kiếm tiếp theo.


## 📁 **Cấu trúc thư mục**

```plaintext
chat-ai-app/
│
├── app/                        # Mã nguồn chính của ứng dụng
│   ├── __init__.py
│   ├── main.py                 # Điểm khởi động ứng dụng (FastAPI / Flask / Tkinter)
│   │
│   ├── llm/                    # Xử lý tương tác với LLM local
│   │   ├── __init__.py
│   │   ├── chat_engine.py      # Tạo câu trả lời từ LLM
│   │   └── prompt_templates.py # Template prompt cho phân loại / tìm kiếm
│   │
│   ├── files/                  # Xử lý và trích xuất nội dung file
│   │   ├── __init__.py
│   │   ├── file_loader.py      # Load & đọc PDF, DOCX, PPTX
│   │   ├── file_parser.py      # Tách nội dung, chia đoạn (chunking)
│   │   └── file_classifier.py  # Phân loại nội dung văn bản
│   │
│   ├── search/                 # Hệ thống tìm kiếm vector
│   │   ├── __init__.py
│   │   ├── embedder.py         # Tạo embedding từ văn bản
│   │   ├── vector_store.py     # FAISS hoặc ChromaDB
│   │   └── retriever.py        # Tìm kiếm file liên quan theo câu hỏi
│   │
│   ├── mcp/                    # Gửi metadata tới MCP Cloud
│   │   ├── __init__.py
│   │   ├── sender.py           # Gửi metadata qua HTTP
│   │   └── schema.py           # Cấu trúc dữ liệu gửi đi
│   │
│   ├── ui/                     # Giao diện người dùng
│   │   └── desktop/            # Giao diện desktop thiết kế bằng PyQt6
│   │       └── ui.py
│
├── data/                       # Thư mục chứa file người dùng
│   ├── documents/              # File đầu vào để tìm kiếm
│   └── embeddings/             # Lưu trữ vector embeddings
│
├── tests/                      # Thư mục chứa test
│   ├── test_file_loader.py
│   ├── test_chat_engine.py
│   └── test_retriever.py
│
├── models/                     # Mô hình LLM local (.gguf, .bin...)
│   └── mistral-7b-q4.gguf
│
├── requirements.txt            # Danh sách thư viện
├── README.md                   # Mô tả dự án
└── .env                        # Biến môi trường (nếu cần)
```

---

## 📌 **Giải thích chính**

| Thư mục / File | Vai trò |
|----------------|---------|
| `app/` | Phần lõi của ứng dụng |
| `llm/` | Tương tác với LLM offline (gọi mô hình, tạo câu trả lời) |
| `files/` | Đọc, phân tích và phân loại file tài liệu |
| `search/` | Tạo vector embedding, tìm kiếm văn bản |
| `mcp/` | Gửi metadata lên dịch vụ MCP |
| `ui/` | Giao diện người dùng (web hoặc desktop) |
| `data/` | Chứa file đầu vào, dữ liệu embedding, cache |
| `models/` | Mô hình LLM tải sẵn (GGUF hoặc binary) |
| `tests/` | Các unit test để kiểm thử logic chương trình |

---

# Công nghệ sử dụng

## 🧰 **1. Ngôn ngữ & Môi trường phát triển**

| Công nghệ | Mô tả |
|----------|-------|
| **Python** | Ngôn ngữ chính để xây dựng backend, xử lý văn bản, tích hợp LLM và vector search. | 

---
 
## 🔍 **4. Semantic Search & Vector Store**

| Công nghệ | Mô tả |
|-----------|------|
| **Sentence-Transformers** | Tạo embedding từ văn bản (dùng mô hình như `all-MiniLM-L6-v2`, `bge-small-en`). |
| **Faiss** | Vector store để lưu và tìm kiếm embedding, hiệu quả, chạy offline. |
| **ChromaDB** | Vector database nhẹ, dễ dùng, tích hợp tốt với LLM pipelines. |
| **LangChain (tuỳ chọn)** | Hỗ trợ tích hợp LLM, vector search, embedding pipeline. |

---

## 🧾 **5. Phân loại nội dung văn bản**

| Công nghệ | Mô tả |
|-----------|------|
| **Zero-shot classification bằng LLM** | Dùng prompt để LLM phân loại văn bản theo yêu cầu. |
| **Scikit-learn (tuỳ chọn)** | Nếu bạn muốn huấn luyện model phân loại riêng (SVM, Naive Bayes). |
| **spaCy / NLTK** | Xử lý ngôn ngữ tự nhiên cơ bản (tokenize, POS tagging, stopword). |

---  