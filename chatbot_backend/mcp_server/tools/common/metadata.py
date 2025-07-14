from shared_mcp import mcp

from utils.file_metadata_manager import update_category_per_user, get_category_per_user

from ollama_config import ask_llm
categories = [
    "Company Plans",
    "Company Reports",
    "Company Policies",
    "Bussiness Contracts",
    "Business Plans",
    "Project Plans",
    "Project Proposals",
    "Project Management Files",
    "Finance Reports",
    "Finance Plans",
    "Marketing Campaigns",
    "Sales Presentations",
    "Sales Reports",
    "Technical Documents",
    "Legal Documents",
    "Human Resources Records",
    "CVs and Resumes",
    "Meeting Notes",
    "Training Materials",
    "Customer Support Documents",
    "Product Documentation",
    "Internal Communications",
    "External Communications",
]


@mcp.tool(
    description="Search the category of a user's file if the file has been classified before (based on the history chat). This tool helps users to quickly find out which category a file belongs to. Required fields are file_name and username.",
    annotations
    = {
        "title": "Search category of file {file_name} in metadata",
    }
)
def search_file_category(file_name: str, username: str = "admin") -> str:
    """
    Search the category of a file for a specific user.

    This tool is used to check which category a file belongs to, which helps in organizing and managing files effectively.

    Args:
        file_name (str): The name of the file whose category is to be retrieved.
    """

    category = get_category_per_user(file_name=file_name, user=username)
    
    if not category:
        return f"File '{file_name}' has not been classified into any category yet."
    
    return f"File '{file_name}' is classified under '{category}' category."


@mcp.tool(
    description="Do not use this tool when user ask to update the category of a file. Classify a file into only one category based on the content of the file. Available categories include: " + ", ".join(categories) + ". Require the content of the file",
    annotations={
        "title": "Analyze the content of the file and classify it into a category",
    }
)
def classify_file_based_on_content(content: str) -> str:
    messages = [
        {"role": "system", "content": "You are a file classification expert. Your task is to analyze the content of the speicific file content and classify it into one of the following categories: " + ", ".join(categories) + ". ONLY return the category name, DO NOT include any additional text or explanation."},
        {"role": "user", "content": content},
    ]

    response = ask_llm(messages)
    # return (
    #     response["message"]["content"]
    #     if "message" in response
    #     else ""
    # )
    return response.text

@mcp.tool(
    description="Save a new category or update new category when user requires to update the category of a file to metadata storage. Required fields are file_name, category and username.",
    annotations={
        "title": "Updating the category for the file {file_name}",
    }
)
def save_file_category(file_name: str, category: str, username: str = 'admin') -> str:
    """
    Save the category of a file to metadata storage.

    This tool is used to store the category of a file in metadata for future reference,
    allowing for better organization and retrieval of files.

    Args:
        file_name (str): The name of the file whose category is to be saved.
        file_category (str): The category to save for the file.
    """

    update_category_per_user(file_name=file_name, user=username, category=category)
    return f"Category '{category}' has been updated for file '{file_name}'."