# filesystem.py
import os
from shared_mcp import mcp;

# Import file_loader with error handling
try:
    from mcp_server.utils import file_loader
    FILE_LOADER_AVAILABLE = True
except ImportError:
    print("Warning: mcp_server.utils.file_loader could not be imported")
    FILE_LOADER_AVAILABLE = False

@mcp.tool(
    description="Read a file from the specified file path, file path is optional and default is 'mcp_server/files'",
    progress_message="Đang đọc file..."
)
def read_file(file_name: str, root_path: str = "mcp_server/files") -> str:
    """Read a file from the specified file path, default is 'files/test.txt'"""
    try:
        full_path = f"{root_path}/{file_name}"
        
        # First try with file_loader if available
        if FILE_LOADER_AVAILABLE:
            try:
                content = file_loader.load_file(full_path)
                if content:
                    return content
            except Exception as e:
                print(f"Error using file_loader: {e}")
        
        # Fallback to direct text file reading
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(full_path, 'r', encoding='latin-1') as f:
                return f.read()
    except Exception as e:
        return f"Error reading file {file_name}: {str(e)}"

@mcp.tool(
    description="Write a file to the specified file path, default folder path is 'mcp_server/files'",
    progress_message="Đang ghi file..."
)
def write_file(content: str, file_name: str, path: str = "mcp_server/files") -> str:
    """Write a file to the specified file path, default is 'mcp_server/files/test.txt'"""
    try:
        # Ensure the directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(f"{path}/{file_name}", "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"

@mcp.tool(
    description="List files in the specified path, default is 'mcp_server/files'",
    progress_message="Đang liệt kê các file..."
)
def list_files(path: str = "mcp_server/files") -> str:
    """List files in the specified path, default is 'mcp_server/files'"""
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files in {path}: {str(e)}"

@mcp.tool(
    description="Create a file in the specified folder path, default folder is 'mcp_server/files'",
    progress_message="Đang tạo file..."
)
def create_file(path: str, file_name: str) -> str:
    """Create a file"""
    try:  
        with open(f"{path}/{file_name}", "w", encoding="utf-8") as f:
            f.write("")
        return f"Successfully created file {path}"
    except Exception as e:
        return f"Error creating file {path}: {str(e)}"