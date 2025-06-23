# KẾ HOẠCH PHÁT TRIỂN ĐỒ ÁN CHAT AI LOCAL LLM + MCP

## 1. PHÂN TÍCH YÊU CẦU & CHUẨN BỊ
- **Đọc kỹ yêu cầu đồ án**, xác định các chức năng chính và nâng cao.
- **Xác định công nghệ, thư viện, mô hình LLM** sẽ sử dụng (`llama.cpp`, `Ollama`, `sentence-transformers`, `FAISS`, `FastAPI`, `Tkinter`, ...).
- **Chuẩn bị môi trường phát triển** (Python, cài đặt các thư viện cần thiết).
- **Tạo cấu trúc thư mục dự án** chuẩn như `README.md`.

## 2. XÂY DỰNG CHỨC NĂNG XỬ LÝ FILE
- Cài đặt và kiểm thử các thư viện đọc file: `PyPDF2`, `python-docx`, `python-pptx`.
- Phát triển module `file_loader.py` để load nội dung từ PDF, DOCX, PPTX.
- Phát triển module `file_parser.py` để tách nội dung, chia đoạn (chunking).
- Viết unit test cho các chức năng đọc và phân tích file.

## 3. TÍCH HỢP LLM LOCAL
- Cài đặt `Ollama` hoặc `llama.cpp` + tải mô hình GGUF phù hợp.
- Phát triển module `chat_engine.py` để nhận prompt và sinh câu trả lời từ LLM.
- Xây dựng các template prompt cho phân loại, tìm kiếm (`prompt_templates.py`).
- Kiểm thử khả năng sinh câu trả lời offline.

## 4. XÂY DỰNG HỆ THỐNG TÌM KIẾM SEMANTIC
- Cài đặt `sentence-transformers`, `FAISS` hoặc `ChromaDB`.
- Phát triển module `embedder.py` để tạo embedding từ văn bản.
- Phát triển module `vector_store.py` để lưu trữ và tìm kiếm embedding.
- Phát triển module `retriever.py` để tìm file liên quan theo câu hỏi.
- Viết test cho pipeline tìm kiếm.

## 5. PHÂN LOẠI NỘI DUNG FILE
- Thiết kế prompt phân loại file (zero-shot hoặc rule-based).
- Phát triển module `file_classifier.py` để phân loại nội dung văn bản.
- Kiểm thử phân loại với các file mẫu.

## 6. TÍCH HỢP MCP (MODEL CONTEXT PROTOCOL)
- Phát triển module `mcp/schema.py` để định nghĩa cấu trúc metadata gửi đi.
- Phát triển module `mcp/sender.py` để gửi metadata qua HTTP tới MCP Cloud (mock API nếu cần).
- Kiểm thử gửi metadata với dữ liệu mẫu.

## 7. XÂY DỰNG GIAO DIỆN NGƯỜI DÙNG
- Chọn giao diện desktop (`Tkinter`) hoặc web (`React`, `Gradio`, ...).
- Phát triển UI cơ bản: khung chat, hiển thị kết quả tìm kiếm, phân loại.
- Kết nối UI với backend (qua API hoặc trực tiếp gọi hàm Python).
- Kiểm thử luồng chat và hiển thị kết quả.

## 8. TÍCH HỢP TOÀN BỘ HỆ THỐNG
- Kết nối các module: **UI ↔ Chat Engine ↔ File Search ↔ Classifier ↔ MCP**.
- Đảm bảo luồng xử lý: *User nhập câu hỏi → AI tìm kiếm → phân loại → gửi metadata → trả kết quả*.
- Kiểm thử end-to-end với nhiều loại file và câu hỏi khác nhau.

## 9. PHÁT TRIỂN TÍNH NĂNG NÂNG CAO *(nếu có thời gian)*
- **Agentic AI:** tự động lên kế hoạch hành động theo yêu cầu phức tạp.
- **Chain of Thought:** AI giải thích quy trình xử lý từng bước.
- **RLHF:** Ghi nhận phản hồi người dùng, cập nhật phân loại cho lần sau.
- **Xuất metadata ra file Excel** (`pandas`, `openpyxl`).

## 10. HOÀN THIỆN, ĐÓNG GÓI, VIẾT TÀI LIỆU
- Viết `README`, hướng dẫn cài đặt, sử dụng, demo video.
- Đóng gói mã nguồn, kiểm tra lại toàn bộ chức năng.
- Chuẩn bị báo cáo, slide thuyết trình.

---

# LỘ TRÌNH CÔNG VIỆC *(Gợi ý theo tuần)*

| Tuần    | Công việc chính                                                      |
|---------|---------------------------------------------------------------------|
| **1**   | Phân tích yêu cầu, chuẩn bị môi trường, dựng skeleton dự án         |
| **2**   | Xử lý file (load, parse, test)                                      |
| **3**   | Tích hợp LLM local, xây dựng chat engine                            |
| **4**   | Xây dựng hệ thống tìm kiếm semantic, vector store                   |
| **5**   | Phân loại nội dung, tích hợp MCP                                    |
| **6**   | Xây dựng giao diện người dùng, kết nối backend                      |
| **7**   | Tích hợp toàn bộ, kiểm thử end-to-end                               |
| **8**   | Phát triển tính năng nâng cao, hoàn thiện tài liệu, demo            |

---

## LƯU Ý
- **Luôn viết test cho từng module nhỏ.**
- **Ghi log quá trình phát triển, lỗi phát sinh.**
- **Ưu tiên chức năng cơ bản trước, nâng cao sau.** 