# filesystem.py
import re
from typing import List, Optional
import os
from shared_mcp import mcp
from search.vector_db import ChromaManager
from utils.file_metadata_manager import get_list_file_names_by_user_and_role
from utils.file_utils import get_root_path
from utils.file_loader import load_file
from ollama_config import ask_llm 
 
db = ChromaManager(collection_name="my_documents", persist_directory=f"{get_root_path()}/data/vector_db")
 
@mcp.tool(
    description="Search related files have content related the user_input(the summary prompt of user). Return a list of file names, with the given username and role. Example list file names to be returned: ['abc.txt', 'user_guide.pdf', ...]", 
    annotations={
        "title": "Searching the file content and getting related files"
    }
)
def search_file_has_content_related(user_input: str, username: str, role: str) -> List[str]:
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
    description="Search the exact file that have name related to the provided filename, user and role. Return exactly the filename. Ex: summary.txt -> summaries.txt,... This tool makes sure the file is existed.",
    annotations={
        "title": "Searching file {filename}"
    }
)
def search_file_has_name_like(filename: str, username: str, role: str) -> str:
    """
    Search for file that have name similar to the provided filename.

    Args:
        filename: The name of the file to search for
        username: The username of the user
        role: The role of the user

    Returns:
        A filename that most matching the search criteria
    """
    filenames = get_list_file_names_by_user_and_role(username, role)
    messages = [
        {"role": "system", "content": f"You are a file search expert. I provide you a list of filenames: {filenames}, and your task is to find a file name that is almost or exactly the same name to the provided filename in the list I given. Only return the filename without any additional text in square brackets (ex: [summary.txt]). If there is no filename that is related to the provided one, response empty square brackets, e.g. '[]'."},
        {"role": "user", "content": filename},
    ]
    response = ask_llm(messages)
    result = response["message"]["content"] 
    return result.strip()

@mcp.tool(
    description="Make sure the file was checked that existed before using this tool. Read the content of the filename. Example filename: 'abc.txt', 'user_guide.pdf', ...", 
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
    description="Create a file with the given filename and write the content to the file",
    annotations={
        "title": "Writing file {file_name}"
    }
)
def create_and_write_file(content: str, file_name: str) -> str: 
    try:
        # Ensure the directory exists
        path = f"{get_root_path()}/data/files/{file_name}"
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_name}"
    except Exception as e:
        return f"Error writing to file {file_name}"
