# mcp_server.py
from mcp.server.fastmcp import FastMCP
import json
import sqlite3
from datetime import datetime
import sys

# Initialize MCP server với tên rõ ràng
mcp = FastMCP("Advanced Business Tools Server")

# Database setup cho persistent storage
def init_db():
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY,
            operation TEXT,
            result REAL,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_context (
            session_id TEXT,
            key TEXT,
            value TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@mcp.tool()
def calculate_basic(operation: str, a: float, b: float) -> dict:
    """
    Thực hiện phép tính cơ bản và lưu kết quả.
    
    Args:
        operation: Loại phép tính (add, subtract, multiply, divide)
        a: Số thứ nhất
        b: Số thứ hai
    
    Returns:
        dict: Kết quả phép tính và thông tin chi tiết
    """
    operations = {
        'add': a + b,
        'subtract': a - b,
        'multiply': a * b,
        'divide': a / b if b != 0 else None
    }
    
    if operation not in operations:
        return {"error": "Phép tính không hợp lệ"}
    
    result = operations[operation]
    if result is None:
        return {"error": "Không thể chia cho 0"}
    
    # Lưu vào database
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO calculations (operation, result, timestamp) VALUES (?, ?, ?)",
        (f"{a} {operation} {b}", result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    return {
        "operation": f"{a} {operation} {b}",
        "result": result,
        "formatted": f"{a} {operation} {b} = {result}",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def get_calculation_history(limit: int = 5) -> dict:
    """
    Lấy lịch sử các phép tính đã thực hiện.
    
    Args:
        limit: Số lượng bản ghi tối đa trả về
    
    Returns:
        dict: Danh sách lịch sử tính toán
    """
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT operation, result, timestamp FROM calculations ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    results = cursor.fetchall()
    conn.close()
    
    history = []
    for op, result, timestamp in results:
        history.append({
            "operation": op,
            "result": result,
            "timestamp": timestamp
        })
    
    return {
        "total_records": len(history),
        "history": history,
        "summary": f"Đã thực hiện {len(history)} phép tính gần đây"
    }

@mcp.tool()
def store_user_context(session_id: str, key: str, value: str) -> dict:
    """
    Lưu thông tin ngữ cảnh người dùng để sử dụng cho các tool khác.
    
    Args:
        session_id: ID phiên làm việc
        key: Khóa thông tin
        value: Giá trị thông tin
    
    Returns:
        dict: Trạng thái lưu trữ
    """
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO user_context (session_id, key, value, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, key, value, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Đã lưu {key} = {value} cho session {session_id}",
        "session_id": session_id,
        "key": key,
        "value": value
    }

@mcp.tool()
def get_user_context(session_id: str, key: str = None) -> dict:
    """
    Lấy thông tin ngữ cảnh đã lưu để hoàn thiện tham số cho tool khác.
    
    Args:
        session_id: ID phiên làm việc
        key: Khóa cần lấy (nếu None thì lấy tất cả)
    
    Returns:
        dict: Thông tin ngữ cảnh
    """
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    
    if key:
        cursor.execute(
            "SELECT value FROM user_context WHERE session_id = ? AND key = ? ORDER BY timestamp DESC LIMIT 1",
            (session_id, key)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "session_id": session_id,
                "key": key,
                "value": result[0],
                "found": True
            }
        else:
            return {
                "session_id": session_id,
                "key": key,
                "found": False,
                "message": "Không tìm thấy thông tin"
            }
    else:
        cursor.execute(
            "SELECT key, value, timestamp FROM user_context WHERE session_id = ? ORDER BY timestamp DESC",
            (session_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        context = {}
        for k, v, t in results:
            if k not in context:  # Chỉ lấy giá trị mới nhất
                context[k] = {"value": v, "timestamp": t}
        
        return {
            "session_id": session_id,
            "context": context,
            "total_keys": len(context)
        }

if __name__ == "__main__": 
    mcp.run(transport="stdio")
