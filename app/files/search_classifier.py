from typing import List, Dict, Optional, Tuple
import os
import json
from pathlib import Path
from app.files.file_loader import load_file
from app.files.file_classifier import classify_file
from app.mcp.sender import send_classified_files
from app.llm.prompt_templates import SEARCH_PROMPT, COT_PROMPT, RLHF_CONFIRM_PROMPT
from app.search.retriever import get_retriever

# Thư mục lưu trữ phản hồi RLHF
RLHF_FEEDBACK_DIR = "data/rlhf_feedback"
RLHF_FEEDBACK_FILE = os.path.join(RLHF_FEEDBACK_DIR, "user_feedback.json")

# Tạo thư mục nếu chưa tồn tại
os.makedirs(RLHF_FEEDBACK_DIR, exist_ok=True)

def load_rlhf_feedback() -> Dict[str, Dict[str, str]]:
    """
    Tải dữ liệu phản hồi từ người dùng
    
    Returns:
        Dict với key là file_path và value là dict chứa label được người dùng xác nhận
    """
    if not os.path.exists(RLHF_FEEDBACK_FILE):
        return {}
    
    try:
        with open(RLHF_FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Lỗi khi tải dữ liệu RLHF: {str(e)}")
        return {}

def save_rlhf_feedback(feedback_data: Dict[str, Dict[str, str]]):
    """
    Lưu dữ liệu phản hồi từ người dùng
    
    Args:
        feedback_data: Dict với key là file_path và value là dict chứa label được người dùng xác nhận
    """
    try:
        with open(RLHF_FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Lỗi khi lưu dữ liệu RLHF: {str(e)}")

def search_files(query: str, directory: str = "data/documents") -> List[str]:
    """
    Tìm kiếm các file trong thư mục dựa trên câu query.
    
    Args:
        query: Câu truy vấn tìm kiếm
        directory: Thư mục chứa file cần tìm
        
    Returns:
        Danh sách đường dẫn các file tìm thấy
    """
    # Kiểm tra thư mục tồn tại
    if not os.path.exists(directory):
        print(f"❌ Thư mục {directory} không tồn tại")
        return []
        
    # Sử dụng vector store để tìm kiếm hiệu quả
    print(f"🔍 Đang tìm kiếm files với query: '{query}'")
    
    try:
        # Kiểm tra và xử lý tìm kiếm đơn giản trước
        # Nếu query trực tiếp là tên file hoặc từ khóa rõ ràng, tìm nhanh hơn
        # keyword_matches = []
        all_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                     if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
                     
        # Kiểm tra từ khóa trực tiếp trong tên file
        # for file_path in all_files:
        #     file_name = os.path.basename(file_path).lower()
        #     query_parts = query.lower().split()
            
        #     # Nếu có bất kỳ từ khóa nào trong tên file
        #     if any(part in file_name for part in query_parts if len(part) > 2):
        #         keyword_matches.append(file_path) 
        
        # Nếu tìm được qua từ khóa, ưu tiên trả về
        # if keyword_matches: 
        #     return keyword_matches
            
        # Nếu không tìm được qua từ khóa, sử dụng vector search
        print(f"🔍 Đang tìm kiếm vector với query: '{query}'")
        retriever = get_retriever(directory)
        
        # Đảm bảo files được index
        if not retriever.index_files():
            print(f"⚠️ Không thể đánh chỉ mục file trong thư mục {directory}")
        
        # Lấy danh sách file liên quan
        vector_results = retriever.get_relevant_files(query)
        
        if vector_results:
            print(f"✓ Vector search tìm thấy {len(vector_results)} file")
            return vector_results
            
        # Nếu vẫn không có kết quả, dùng fallback
        print("⚠️ Không tìm thấy kết quả từ vector search, sử dụng fallback")
            
        # Fallback: Sử dụng phương pháp tìm kiếm trực tiếp
        from app.llm.chat_engine import chat_llm  # Import here to avoid circular dependency
        
        file_paths = []
        file_summaries = []
        
        for file_path in all_files:
            content = load_file(file_path)
            if content and isinstance(content, str) and content.strip():
                # Giới hạn nội dung để tiết kiệm token
                file_summaries.append(f"File: {os.path.basename(file_path)}\nNội dung: {content[:2000]}...")
                file_paths.append(file_path)
        
        if not file_paths:
            return []
        
        # Dùng LLM để tìm các file liên quan đến câu hỏi
        prompt = SEARCH_PROMPT.format(query=query, file_summaries="\n\n".join(file_summaries))
        response = chat_llm(prompt, streaming=False)
        print(f"🤖 LLM response: {response}")
        
        # Xử lý kết quả trả về từ LLM để lấy danh sách file liên quan
        relevant_files = []
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Tìm file trong danh sách ban đầu
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                if file_name.lower() in line.lower():
                    relevant_files.append(file_path)
                    print(f"✓ Tìm thấy file qua LLM: {file_name}")
                    break
        
        return relevant_files
    except Exception as e:
        print(f"❌ Lỗi khi tìm kiếm files: {str(e)}")
        return []

def get_file_classification(file_path: str, labels: List[str], method: str = "llm") -> str:
    """
    Phân loại file với tích hợp RLHF - kiểm tra phản hồi người dùng trước khi phân loại
    
    Args:
        file_path: Đường dẫn file
        labels: Danh sách nhãn
        method: Phương pháp phân loại
        
    Returns:
        Nhãn phân loại
    """
    # Kiểm tra xem đã có phản hồi từ người dùng chưa
    rlhf_data = load_rlhf_feedback()
    if file_path in rlhf_data and "user_label" in rlhf_data[file_path]:
        user_label = rlhf_data[file_path]["user_label"]
        # Kiểm tra xem nhãn người dùng có trong danh sách nhãn không
        if user_label in labels:
            return user_label
    print(f"Chưa có phản hồi từ người dùng cho {file_path}. LLM sẽ thực hiện phân loại.")
    # Nếu không có phản hồi, thực hiện phân loại thông thường
    return classify_file(file_path, labels, method=method)

def format_search_results(results: List[Dict], explanation: str) -> str:
    """
    Format kết quả tìm kiếm để hiển thị cho người dùng
    
    Args:
        results: Danh sách kết quả tìm kiếm
        explanation: Giải thích CoT
        
    Returns:
        Chuỗi kết quả đã được format
    """
    if not results:
        return "❌ Không tìm thấy file nào phù hợp."
    
    # Khởi tạo output trước khi sử dụng
    output = "🔍 KẾT QUẢ TÌM KIẾM\n"
    output += "=" * 40 + "\n\n"
    
    # Phân loại theo nhóm
    group_a = [r for r in results if r.get("label") == "A"]
    group_b = [r for r in results if r.get("label") == "B"]
    others = [r for r in results if r.get("label") not in ["A", "B"]]
    
    if group_a:
        output += "✅ Đúng nội dung cần tìm (Nhóm A):\n"
        for item in group_a:
            output += f"  • {item['file_name']}\n"
        output += "\n"
    
    if group_b:
        output += "ℹ️ Có nội dung liên quan (Nhóm B):\n"
        for item in group_b:
            output += f"  • {item['file_name']}\n"
        output += "\n"
    
    if others:
        output += "⚠️ Các file khác:\n"
        for item in others:
            output += f"  • {item['file_name']} (Nhóm {item.get('label', '?')})\n"
        output += "\n"
    
    # Giải thích CoT
    output += "\n\n📝 PHÂN TÍCH QUY TRÌNH\n"
    output += "=" * 40 + "\n"
    output += explanation
    
    # Thêm phần RLHF
    output += "\n\n💬 PHẢN HỒI\n"
    output += "=" * 40 + "\n"
    output += "Để điều chỉnh phân loại, hãy nhập: 'điều chỉnh [tên file] [nhãn mới]'\n"
    output += "Ví dụ: điều chỉnh git-cheat-sheet.pdf B\n"
    
    return output

def handle_search_and_classify(query: str, directory: str = "data/documents", 
                      labels: List[str] = ["A", "B"]) -> Tuple[List[Dict], str]:
    """
    Tìm kiếm và phân loại các file dựa trên câu query.
    Trả về nhóm A nếu đúng nội dung cần tìm, nhóm B nếu có nội dung liên quan.
    
    Args:
        query: Câu truy vấn tìm kiếm
        directory: Thư mục chứa file cần tìm
        labels: Danh sách nhãn phân loại
        
    Returns:
        Tuple (danh sách thông tin các file tìm thấy, chuỗi CoT giải thích)
    """
    # Import here to avoid circular dependency
    from app.llm.chat_engine import chat_llm
    
    # Tìm các file liên quan
    relevant_files = search_files(query, directory)
    
    if not relevant_files:
        return [], f"Không tìm thấy file nào liên quan đến: '{query}'"
    else:
        print(f"🔍 Tìm thấy {len(relevant_files)} file liên quan đến: '{query}' - {relevant_files}")
    
    # Phân loại các file tìm thấy
    file_summaries = []
    classified_results = []
    
    for file_path in relevant_files:
        content = load_file(file_path)
        file_name = os.path.basename(file_path)
        
        if not content:
            continue
            
        # Phân loại nội dung sử dụng RLHF
        label = get_file_classification(file_path, labels, method="llm")
        print(f"Phân loại file: {file_name} - {label}")
        
        # Tạo tóm tắt để hiển thị và CoT
        summary = content[:3000] + "..." if len(content) > 3000 else content
        file_summaries.append(f"File: {file_name}\nNội dung: {summary}\nPhân loại: {label}")
        
        classified_results.append({
            "file_path": file_path,
            "file_name": file_name,
            "label": label,
            "content_preview": summary
        })
    
    # Tạo Chain of Thought giải thích
    if classified_results:
        cot_prompt = COT_PROMPT.format(
            query=query, 
            file_summaries="\n\n".join(file_summaries)
        )
        cot_explanation = chat_llm(cot_prompt, streaming=False)
    else:
        cot_explanation = f"Đã tìm thấy {len(relevant_files)} file nhưng không phân loại được."
    
    # Gửi metadata qua MCP
    send_classified_files(
        file_paths=[item["file_path"] for item in classified_results],
        labels=labels,
        classification_method="llm",
        include_summary=False
    )
    
    return format_search_results(classified_results, cot_explanation)

def process_rlhf_feedback(user_input: str) -> str:
    """
    Xử lý phản hồi từ người dùng về phân loại file (RLHF)
    
    Args:
        user_input: Phản hồi của người dùng, định dạng "điều chỉnh [tên file] [nhãn mới]"
        
    Returns:
        Thông báo kết quả
    """
    # Xử lý cú pháp: điều chỉnh [tên file] [nhãn mới]
    parts = user_input.strip().split(' ')
    if len(parts) < 3:
        return "❌ Cú pháp không đúng. Vui lòng sử dụng: 'điều chỉnh [tên file] [nhãn mới]'"
    
    file_name = parts[1]
    new_label = parts[2].upper()
    
    # Tìm file trong thư mục documents
    doc_dir = "data/documents"
    file_path = None
    for root, _, files in os.walk(doc_dir):
        for f in files:
            if f.lower() == file_name.lower():
                file_path = os.path.join(root, f)
                break
    
    if not file_path:
        return f"❌ Không tìm thấy file: {file_name}"
    
    # Lưu phản hồi vào RLHF store
    rlhf_data = load_rlhf_feedback()
    rlhf_data[file_path] = {
        "file_name": file_name,
        "user_label": new_label,
        "timestamp": str(Path(file_path).stat().st_mtime)
    }
    save_rlhf_feedback(rlhf_data)
    
    # Gửi metadata cập nhật
    try:
        send_classified_files(
            file_paths=[file_path],
            labels=["A", "B", new_label],
            classification_method="rlhf",
            include_summary=False
        )
        return f"✅ Đã cập nhật nhãn của file {file_name} thành {new_label}"
    except Exception as e:
        return f"⚠️ Đã lưu phản hồi nhưng gặp lỗi khi gửi metadata: {str(e)}" 