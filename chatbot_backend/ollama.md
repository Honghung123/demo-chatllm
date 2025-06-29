# Hướng dẫn cài đặt Ollama cho dự án Chat AI Local LLM (Windows)

## 1. Cài đặt Ollama trên Windows

### a. Yêu cầu hệ thống
- Windows 10/11 (64-bit)
- Đã cài đặt Python (khuyên dùng Python latest  3.12+)

### b. Tải và cài đặt Ollama
1. Truy cập trang chủ Ollama: https://ollama.com/download
2. Tải file cài đặt cho Windows (`OllamaSetup.exe`).
3. Chạy file vừa tải và làm theo hướng dẫn để cài đặt Ollama.
4. Sau khi cài đặt xong, mở **Command Prompt** hoặc **PowerShell** và kiểm tra:
   ```sh
   ollama --version
   ```
   Nếu hiện phiên bản Ollama, bạn đã cài thành công.

## 2. Tải mô hình LLM phù hợp

Ollama hỗ trợ nhiều mô hình (Llama2, Mistral, Phi, Gemma, ...). Nhưng ở đây ta chọn Mistral. Để tải mô hình này, chạy lệnh:

```sh
ollama pull mistral
``` 
- Mô hình sẽ được lưu ở thư mục mặc định của Ollama.

## 3. Chạy thử mô hình với Ollama

Khởi động mô hình (tắt GPU, chỉ sử dụng CPU) và chat thử trực tiếp:

```sh
export OLLAMA_NO_CUDA=1 
ollama run mistral
``` 

- Gõ câu hỏi để kiểm tra mô hình hoạt động.
- Nhấn `Ctrl+C` để thoát.

## 4. Tích hợp Ollama vào Python backend

### Cách 1:
- Sử dụng thư viện ollama:
```
pip install ollama
```
=> Trong project này này đang dùng thư viện ollama :v. Nên ae nhớ chạy lệnh trên nhá XD

### Cách 2
- Ollama cung cấp REST API mặc định tại `http://localhost:11434`.
- Bạn có thể gọi từ Python bằng thư viện `requests`:

```python
import requests

url = 'http://localhost:11434/api/chat'
data = {
    'model': 'mistral',
    'prompt': 'Xin chào, bạn là ai?'
}
response = requests.post(url, json=data, stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode())
```

- Đảm bảo Ollama đang chạy (nếu chưa, chạy `ollama run mistral` hoặc để Ollama tự động khởi động khi có request). 

## 5. Một số lệnh hữu ích

- Liệt kê các mô hình đã tải:
  ```sh
  ollama list
  ```
- Xóa mô hình:
  ```sh
  ollama rm mistral
  ```
- Xem log server:
  ```sh
  ollama serve
  ```

## 6. Tài liệu tham khảo
- Trang chủ: https://ollama.com
- Thư viện mô hình: https://ollama.com/library
- REST API: https://github.com/ollama/ollama/blob/main/docs/api.md

---
**Ghi chú:**
- Ollama sẽ tự động tải mô hình nếu bạn gọi API với tên model chưa có.
- Có thể tích hợp trực tiếp vào FastAPI/Flask backend như một service sinh câu trả lời LLM. 

# Installed
`pip install fastapi uvicorn fastui python-multipart mistralai python-decouple
`
