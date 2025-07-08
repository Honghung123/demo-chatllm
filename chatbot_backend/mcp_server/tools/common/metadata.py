from shared_mcp import mcp

from utils.file_metadata_manager import update_category_per_user, get_category_per_user

from ollama import Client

OLLAMA_HOST="http://192.168.128.1:11434"
OLLAMA_MODEL="mistral"

client = Client(
    host=OLLAMA_HOST
)

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
    description="Search the category of a user's file if the file has been classified before. This tool helps users to quickly find out which category a file belongs to.",
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
    description="Classify a file into a specific category based on the content of the file. Available categories include: " + ", ".join(categories) + ".",
    annotations={
        "title": "Anylyze the content of file and classify it into a category",
    }
)
def classify_file_based_on_content(content: str) -> str:
    messages = [
        {"role": "system", "content": "You are a file classification expert. Your task is to analyze the content of a file and classify it into one of the following categories: " + ", ".join(categories) + ". If the content does not fit any category, return 'Unclassified'. Only return the category name without any additional text."},
        {"role": "user", "content": content},
    ]

    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)
    
    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )


@mcp.tool(
    description="Store category of a file to metadata storage to use in the future.",
    annotations={
        "title": "Save category of file {file_name} to metadata",
    }
)
def save_file_category(file_name: str, file_category: str, username: str) -> str:
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