from enum import Enum
import sqlite3
from typing import List, Optional
from app.service.db_service import DB_PATH
from schema.role import Role
 
class RoleName(str, Enum):
    ADMIN = "admin|Admin"
    HR = "hr|Human Resource"
    SALES = "sales|Sales"
    MARKETING = "marketing|Marketing"
    LEGAL = "legal|Legal"
    FINANCE = "finance|Finance"
    IT = "it|IT"

class RoleService:  
    def _get_connection() -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named column access
        return conn

    @staticmethod
    def create_table_if_not_exists() -> None:
        """Create the roles table if it doesn't exist"""
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            displayName TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        
    @staticmethod
    def initialize_default_roles() -> None:
        """Initialize default roles from RoleName enum"""
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        
        # Get all role names from the enum
        roles = [{
            "id": role.value.split("|")[0],
            "displayName": role.value.split("|")[1]
        } for role in RoleName]  
        
        # Insert or update roles
        for role in roles: 
            cursor.execute(
                """
                INSERT OR IGNORE INTO roles (id, displayName)
                VALUES (?, ?)
                """, 
                (role['id'], role['displayName'])
            )
            
        conn.commit()
        conn.close()
        
    @staticmethod
    def create(role: Role) -> None:
        """
        Create a new role or update an existing one
        
        Args:
            role: Role object
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        data = role.to_sqlite_dict()
        cursor.execute(
            """
            INSERT OR REPLACE INTO roles (id, displayName) 
            VALUES (:id, :displayName)
            """, 
            data
        )
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_by_id(role_id: str) -> Optional[Role]:
        """
        Get a role by id
        
        Args:
            role_id: Role id to search for
            
        Returns:
            Role object if found, None otherwise
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        
        if row:
            role_data = dict(row)
            conn.close()
            return Role(
                id=role_data['id'],
                displayName=role_data['displayName']
            )
        conn.close()
        return None
        
    @staticmethod
    def get_all() -> List[Role]:
        """
        Get all roles
        
        Returns:
            List of Role objects
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles ORDER BY id")
        rows = cursor.fetchall()
        
        roles = []
        for row in rows:
            role_data = dict(row)
            roles.append(Role(
                id=role_data['id'],
                displayName=role_data['displayName'],
            ))
        
        conn.close()
        return roles
        
    @staticmethod
    def update(role_id: str, displayName: str) -> bool:
        """
        Update a role's name
        
        Args:
            role_id: Id of the role to update
            name: New name
            
        Returns:
            True if role was updated, False if role was not found
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE roles SET displayName = ? WHERE id = ?", 
            (displayName, role_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
        
    @staticmethod
    def delete(role_id: str) -> bool:
        """
        Delete a role by id
        
        Args:
            role_id: Id of the role to delete
            
        Returns:
            True if role was deleted, False if role was not found
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def role_exists(role_id: str) -> bool:
        """
        Check if a role exists
        
        Args:
            role_id: Id of the role to check
            
        Returns:
            True if role exists, False otherwise
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM roles WHERE id = ?", (role_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    @staticmethod
    def validate_role(role_id: str) -> bool:
        """
        Validate if a role id is both valid in the enum and exists in the database
        
        Args:
            role_id: Id of the role to validate
            
        Returns:
            True if role is valid, False otherwise
        """
        # Check if the role id is valid in the enum
        if not Role.is_valid_role(role_id):
            return False
        
        # Check if the role exists in the database
        return RoleService.role_exists(role_id)
