# filesystem.py
from typing import List, Optional
import os
from shared_mcp import mcp
from search.vector_db import ChromaManager
from utils.file_metadata_manager import get_list_file_names_by_user_and_role
from utils.file_utils import get_root_path
from utils.file_loader import load_file

db = ChromaManager(collection_name="my_documents", persist_directory=f"{get_root_path()}/data/vector_db")
 
@mcp.tool(
    description="Search related files based on user_input(the summary prompt of user). Return a list of file names, with the given username and role. Example: ['Q2 Sales Report.txt', 'user_guide.txt']", 
    annotations={
        "title": "Searching file and getting related files based on user input"
    }
)
def search_file(user_input: str, username: str, role: str) -> List[str]:
    """
    Read specific files or retrieve relevant documents based on a query.

    Args:
        query: The search query or context string
        filenames: Optional list of filenames to search within
        username: The username of the user
        role: The role of the user
    Returns:
        Combined content of matching documents as a single string
    """ 
    filenames = get_list_file_names_by_user_and_role(username, role)  
    results: List[str] = db.search_relative_documents(
        query=user_input, n_results=10, filenames=filenames
    )
    return results

@mcp.tool(
    description="Read the content of the file name. Example filename: 'Q2 Sales Report.txt', 'user_guide.txt'", 
    annotations={
        "title": "Reading file {filename}"
    }
)
def read_file(filename: str) -> str:
    """
    Read specific files or retrieve relevant documents based on a query.

    Args:
        query: The search query or context string
        filenames: Optional list of filenames to search within

    Returns:
        Combined content of matching documents as a single string
    """
    try: 
        loaded_file = load_file(f"{get_root_path()}/data/files/{filename}")
        return loaded_file
    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"

@mcp.tool(
    description="Write a file to the specified file path, default folder path is 'mcp_server/files'",
    annotations={
        "title": "Writing file {file_name}"
    }
)
def write_file(content: str, file_name: str, path: str = "../files") -> str:
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
    description="Create a file in the specified folder path, default folder is 'mcp_server/files'",
    annotations={
        "title": "Creating file {file_name}"
    }
)
def create_file(path: str, file_name: str) -> str:
    """Create a file"""
    try:
        with open(f"{path}/{file_name}", "w", encoding="utf-8") as f:
            f.write("")
        return f"Successfully created file {path}"
    except Exception as e:
        return f"Error creating file {path}: {str(e)}"
