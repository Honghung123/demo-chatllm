import os
from typing import List, Optional
from app.file.file_metadata_manager import get_list_personal_files, add_metadata
from schema.file import FileSystem
 
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
    
    