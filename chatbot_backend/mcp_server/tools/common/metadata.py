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
    description="Search the category of a user's file if the file has been classified before (based on the history chat). This tool helps users to quickly find out which category a file belongs to.",
    annotations
    = {
        "title": "Search category of file {file_name} in metadata",
    }
)
def search_file_category(file_name: str, username: str) -> str:
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
    description="Make sure to pass file_content as an argument of this file or you will kill the workflow as it is not NULL or empty. This tools is used for classifying a file into only one category based on the content of the file. Available categories include: " + ", ".join(categories) + ".",
    annotations={
        "title": "Analyze the content of the file and classify it into a category",
    }
)
def classify_file_based_on_content(content: str) -> str:
    messages = [
        {"role": "system", "content": "You are a file classification expert. Your task is to analyze the content of the speicific file content and classify it into one of the following categories: " + ", ".join(categories) + ". Only return the category name without any additional text."},
        {"role": "user", "content": content},
    ]

    response = ask_llm(messages)
    return (
        response["message"]["content"]
        if "message" in response
        else ""
    )


@mcp.tool(
    description="Make sure the filename was checked, classified before using this tool. Store category for a file to metadata storage to use in the future. Remember to pass username as an argument of this tool. This tool is used to save the category of a file to metadata storage for future reference.",
    annotations={
        "title": "Save category of file {file_name} to metadata",
    }
)
def save_file_category(file_name: str, file_category: str, username: str = 'admin') -> str:
    """
    Save the category of a file to metadata storage.

    This tool is used to store the category of a file in metadata for future reference,
    allowing for better organization and retrieval of files.

    Args:
        file_name (str): The name of the file whose category is to be saved.
        file_category (str): The category to save for the file.
    """

    update_category_per_user(file_name=file_name, user=username, category=file_category)
    return f"Category '{file_category}' has been saved for file '{file_name}'."