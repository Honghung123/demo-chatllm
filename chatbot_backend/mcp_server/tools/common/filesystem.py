# filesystem.py
from typing import List, Optional
import os
from shared_mcp import mcp
from search.vector_db import ChromaManager

db = ChromaManager(collection_name="my_documents", persist_directory="data/vector_store")

# Import file_loader with error handling
try:
    from mcp_server.utils import file_loader

    FILE_LOADER_AVAILABLE = True
except ImportError:
    print("Warning: mcp_server.utils.file_loader could not be imported")
    FILE_LOADER_AVAILABLE = False


@mcp.tool(
    description="Read one or more files from the specified path, or use RAG to retrieve relevant content. Query is the content. Filenames param is a list of filename, if there is only one file, this is an array of 1 element"
)
def read_file(query: str, filenames: Optional[List[str]] = None) -> str:
    """
    Read specific files or retrieve relevant documents based on a query.

    Args:
        query: The search query or context string
        filenames: Optional list of filenames to search within

    Returns:
        Combined content of matching documents as a single string
    """
    return """
        🧾 Q2 Sales Report

        - Total revenue: $150,000
        - Top product: Eco T-shirt
        - Conversion rate: 4.5%
        - Ad spend: $8,000
        - Customer feedback: Positive sentiment increased by 15%

        Key insights:
        - Strong weekend performance
        - High CTR on Instagram campaigns
        - Best response to limited-time offers
        """
    # filenames = filenames or []
    # results: List[str] = db.search_relative_documents(
    #     query=query, n_results=10, filenames=filenames
    # )
    # return "\n\n".join(results) if results else "No content found."


@mcp.tool(
    description="Write a file to the specified file path, default folder path is 'mcp_server/files'"
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
    description="Create a file in the specified folder path, default folder is 'mcp_server/files'"
)
def create_file(path: str, file_name: str) -> str:
    """Create a file"""
    try:
        with open(f"{path}/{file_name}", "w", encoding="utf-8") as f:
            f.write("")
        return f"Successfully created file {path}"
    except Exception as e:
        return f"Error creating file {path}: {str(e)}"
