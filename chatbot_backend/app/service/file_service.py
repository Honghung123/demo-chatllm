import sqlite3
import os
from typing import List, Optional
from schema.file import FileSystem

DB_PATH = "app/database/db.sqlite3"

class FileService:         
    def _get_connection() -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named column access
        return conn

    @staticmethod
    def create_table_if_not_exists() -> None:
        """Create the files table if it doesn't exist"""
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            orginal_name TEXT NOT NULL,
            extension TEXT NOT NULL,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        
    @staticmethod
    def create(file: FileSystem, file_content: bytes = None) -> None:
        """
        Save a file to the database and optionally save content to filesystem
        
        Args:
            file: File metadata
            file_content: Optional file content to save
        """
        conn = FileService._get_connection()
        cursor = conn.cursor()
        data = file.to_sqlite_dict()
        cursor.execute(
            """
            INSERT INTO files (name, orginal_name, extension, username, timestamp) 
            VALUES (:name, :orginal_name, :extension, :username, :timestamp)
            """, 
            data
        )
        conn.commit()
        conn.close()
        
        # If file content is provided, save it to the filesystem
        if file_content is not None:
            file_path = os.path.join(self.upload_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
    
    @staticmethod
    def get_by_name(filename: str) -> Optional[FileSystem]:
        """Get a file by name"""
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE name = ?", (filename,))
        row = cursor.fetchone()
        
        if row:
            file_data = dict(row)
            conn.close()
            return FileSystem(
                name=file_data['name'],
                orginal_name=file_data['orginal_name'],
                extension=file_data['extension'],
                username=file_data['username'],
                timestamp=file_data['timestamp']
            )
        conn.close()
        return None
    
    @staticmethod
    def get_all() -> List[FileSystem]:
        """Get all files"""
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        files = []
        for row in rows:
            file_data = dict(row)
            files.append(FileSystem(
                name=file_data['name'],
                orginal_name=file_data['orginal_name'],
                extension=file_data['extension'],
                username=file_data['username'],
                timestamp=file_data['timestamp']
            ))
        
        conn.close()
        return files
        
    @staticmethod
    def get_by_username(username: str) -> List[FileSystem]:
        """Get all files for a specific user"""
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE username = ? ORDER BY timestamp DESC", (username,))
        rows = cursor.fetchall()
        
        files = []
        for row in rows:
            file_data = dict(row)
            files.append(FileSystem(
                name=file_data['name'],
                orginal_name=file_data['orginal_name'],
                extension=file_data['extension'],
                username=file_data['username'],
                timestamp=file_data['timestamp']
            ))
        
        conn.close()
        return files
    
    @staticmethod
    def delete(filename: str) -> bool:
        """
        Delete a file by name from database and filesystem
        
        Returns:
            bool: True if file was deleted, False otherwise
        """
        # First check if file exists in database
        file = FileService.get_by_name(filename)
        if not file:
            return False
            
        # Delete from database
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE name = ?", (filename,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        # Delete from filesystem if exists
        file_path = os.path.join(FileService.upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return deleted
    
    @staticmethod
    def search_by_original_name(search_term: str) -> List[FileSystem]:
        """Search files by original name ralated to search_term"""
        conn = FileService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM files WHERE orginal_name LIKE ? ORDER BY timestamp DESC", 
            (f"%{search_term}%",)
        )
        rows = cursor.fetchall()
        
        files = []
        for row in rows:
            file_data = dict(row)
            files.append(FileSystem(
                name=file_data['name'],
                orginal_name=file_data['orginal_name'],
                extension=file_data['extension'],
                username=file_data['username'],
                timestamp=file_data['timestamp']
            ))
        
        conn.close()
        return files
