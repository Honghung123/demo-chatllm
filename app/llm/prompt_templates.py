# Template prompt

# Tool selection prompt (English)
TOOL_SELECTION_FORMAT = {
    "tool_name": "string",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    },
    "execute_flag": "boolean"
}

TOOL_SELECTION_PROMPT = (
    "You are an AI assistant that helps select appropriate tools to fulfill user requests.\n\n"
    "User query: \"{query}\"\n\n" 
    "Based on the user query, provide a list of tools that should be executed in sequence to fulfill the request.\n"
    "Return your response as a JSON array with the following structure for each tool:\n"
    "```json\n"
    "[\n"
    "  {{\n"
    "    \"tool_name\": \"string\",\n"
    "    \"parameters\": {{\n"
    "      \"param1\": \"value1\",\n"
    "      \"param2\": \"value2\"\n"
    "    }},\n"
    "    \"execute_flag\": boolean\n"
    "  }}\n"
    "]\n"
    "```\n"
    "Note: Set execute_flag to true if this tool needs to be executed to provide additional context. Only include tools that are necessary to complete the task. List them in the order they should be executed. No comment or explanation."
) 




# Phân loại file văn bản theo nhãn (zero-shot)
CLASSIFY_PROMPT = (
    "Bạn là một AI có nhiệm vụ phân loại nội dung file văn bản.\n"
    "Nội dung file:\n\"\"\"\n{content}\n\"\"\"\n"
    "Hãy phân loại file này vào một trong các nhóm sau: {labels}.\n"
    "Chỉ trả về tên nhóm phù hợp nhất, không giải thích thêm."
)

# Tìm kiếm file liên quan đến truy vấn
SEARCH_PROMPT = (
    "Bạn là một AI hỗ trợ tìm kiếm tài liệu.\n"
    "Câu hỏi của người dùng: \"{query}\"\n"
    "Dưới đây là danh sách các file và nội dung tóm tắt:\n{file_summaries}\n"
    "Hãy liệt kê tên các file liên quan nhất đến câu hỏi trên. "
    "Chỉ trả về danh sách tên file, không giải thích."
)

# Giải thích quy trình tìm kiếm và phân loại (Chain of Thought)
COT_PROMPT = (
    "Bạn hãy giải thích từng bước bạn đã thực hiện để tìm kiếm và phân loại file cho truy vấn: \"{query}\"\n"
    "Danh sách file và nội dung:\n{file_summaries}\n"
    "Hãy trình bày các bước xử lý (index, tìm kiếm, phân loại) một cách ngắn gọn"
)

# Xác nhận nhãn phân loại với người dùng (RLHF)
RLHF_CONFIRM_PROMPT = (
    "Tôi đã phân loại file \"{filename}\" vào nhóm \"{label}\" dựa trên nội dung:\n"
    "\"\"\"\n{content}\n\"\"\"\n"
    "Bạn có đồng ý với nhãn này không? Nếu không, hãy đề xuất nhãn phù hợp hơn."
)

# Tóm tắt metadata để xuất file
EXPORT_METADATA_PROMPT = (
    "Dưới đây là metadata của các file đã được phân loại:\n"
    "{metadata_list}\n"
    "Hãy kiểm tra lại thông tin trước khi xuất ra file. Nếu có gì cần chỉnh sửa, hãy nêu rõ."
)