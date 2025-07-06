import os
from typing import List, Optional
from app.file.file_metadata_manager import get_list_personal_files, add_metadata, delete_metadata, update_metadata
from utils.file_utils import get_root_path
from schema.file import FileSystem
from app.search.vector_db import chroma_db
 
class FileService:

    @staticmethod
    def create(file: FileSystem, roles : List[str] = []) -> bool:
        """
        Create a new file entry in the metadata.json.
        
        Returns:
            bool: True if file was created successfully, False otherwise
        """
        # Save file to filesystem
        add_metadata(
            file_name=file.name,
            original_name=file.orginal_name,
            extension=file.extension,
            username=file.username,
            timestamp=file.timestamp.isoformat(),
            roles=roles
        )
        return True
    
    @staticmethod
    def get_by_username(username: str) -> List[FileSystem]:
        """Get all files for a specific user"""
        return get_list_personal_files(username)
    
    @staticmethod
    def delete(file_name: str) -> bool:
        """
        Delete a file entry from the metadata.json and remove the file from the filesystem.
        
        Returns:
            bool: True if file was deleted successfully, False otherwise
        """
        # Remove file metadata
        delete_metadata(file_name)

        # remove from vector_db
        docs = chroma_db.filter_documents(filenames=[file_name])
        for doc in docs:
            chroma_db.delete_document(doc.id)
        
        # Remove file from filesystem
        documents_dir = f"{get_root_path()}/data/files"
        file_path = os.path.join(documents_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return True
    
    # replace the original_name in metadata
    @staticmethod
    def rename_file(file_name_in_system: str, new_name: str) -> bool:
        """
        Rename a file entry in the metadata.json and rename the file in the filesystem.

        Args:
            file_name_in_system (str): The current name of the file in the system
            new_name (str): The new display name for the file (replace the original_name in metadata)
        
        Returns:
            bool: True if file was renamed successfully, False otherwise
        """
        # Rename file metadata
        update_metadata(
            file_name=file_name_in_system,
            original_name=new_name
        )
        return True
    
    
    