import json
import os
from datetime import datetime
from typing import Optional

METADATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../data/metadatas/metadata.json')

def load_metadata(file_path: str = METADATA_FILE_PATH) -> dict:
    """Load metadata from a file.""" 

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def save_metadata(metadata: dict, file_path: str = METADATA_FILE_PATH) -> None:
    """Save metadata to a file."""
    
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def get_metadata(file_name: str) -> dict:
    """Get metadata for a file."""

    metadatas = load_metadata()
    if file_name not in metadatas:
        raise KeyError(f"No metadata found for file: {file_name}")
    return metadatas[file_name]

def add_metadata(file_name: str, original_name: str, extension: str, timestamp: str ,username: str, roles: list) -> None:
    """Add metadata for a file."""
    
    metadatas = load_metadata()
    
    metadatas[file_name] = {
        "original_name": original_name,
        "extension": extension,
        "timestamp": timestamp,
        "username": username,
        "roles": roles,
        "category": {}
    }
    
    save_metadata(metadatas)

def delete_metadata(file_name: str) -> None:
    """Delete metadata for a file."""
    
    metadatas = load_metadata()
    
    if file_name not in metadatas:
        raise KeyError(f"No metadata found for file: {file_name}")
    
    del metadatas[file_name]
    
    save_metadata(metadatas)

def update_metadata(file_name: str, original_name: str, roles: list) -> None:
    """
        Update metadata for a file.
        How to use:
            update_metadata("file1.pdf", original_name="abcxyz.pdf" , roles=["admin", "user"])
    """
    
    metadatas = load_metadata()
    
    if file_name not in metadatas:
        raise KeyError(f"No metadata found for file: {file_name}")
    
    metadatas[file_name]['roles'] = roles
    metadatas[file_name]['original_name'] = original_name

    save_metadata(metadatas)

def get_category_per_user(file_name: str, user: str) -> Optional[str]:
    """Get the category of a file for a user."""
    
    metadatas = load_metadata()
    
    if file_name not in metadatas:
        raise KeyError(f"No metadata found for file: {file_name}")
    
    category = metadatas[file_name]['category'].get(user, None)
    
    return category

def update_category_per_user(file_name: str, user: str, category: str) -> None:
    """Update the category of a file for a user."""
    
    metadatas = load_metadata()
    
    if file_name not in metadatas:
        raise KeyError(f"No metadata found for file: {file_name}")
    
    metadatas[file_name]['category'][user] = category

    save_metadata(metadatas)

def get_list_file_names_by_user_and_role(user:str, role: str) -> list:
    """Get a list of file names by user and role."""
    
    metadatas = load_metadata()
    file_names = []
    
    for file_name, metadata in metadatas.items():
        if user == metadata.get('author', '') or role == "admin" or role in metadata.get("roles", []):
            file_names.append(file_name)
    
    return file_names

# file uploads by admin are considered system files
def get_list_system_files() -> list:
    """Get a list of all file names in the metadata."""
    
    metadatas = load_metadata()
    file_names = []

    for file_name, metadata in metadatas.items():
        if metadata.get('username') == 'admin':
            file_names.append(file_name)

    return list(metadatas.keys())

# file uploads by users are considered personal files
def get_list_personal_files(user: str) -> list:
    """Get a list of personal file names for a user."""
    
    metadatas = load_metadata()
    file_names = []
    
    if user != "admin":
        for file_name, metadata in metadatas.items():
            if metadata.get('username') == user:
                file_names.append(file_name)
    
    return file_names