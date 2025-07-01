import sqlite3
from typing import List, Optional, Dict
from schema.role import Role, RoleName

DB_PATH = "app/database/db.sqlite3"
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
            name TEXT PRIMARY KEY,
            description TEXT
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
        role_names = Role.get_all_role_names()
        default_descriptions = {
            "admin": "Administrator role with full permissions",
            "hr": "Human Resources role with access to employee data",
            "sales": "Sales role with access to client and sales data",
            "marketing": "Marketing role with access to campaign data",
            "legal": "Legal role with access to contract data",
            "finance": "Finance role with access to financial data",
            "it": "IT role with access to technical systems"
        }
        
        # Insert or update roles
        for role_name in role_names:
            description = default_descriptions.get(role_name, "")
            cursor.execute(
                """
                INSERT OR IGNORE INTO roles (name, description)
                VALUES (?, ?)
                """, 
                (role_name, description)
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
            INSERT OR REPLACE INTO roles (name, description) 
            VALUES (:name, :description)
            """, 
            data
        )
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_by_name(role_name: str) -> Optional[Role]:
        """
        Get a role by name
        
        Args:
            role_name: Role name to search for
            
        Returns:
            Role object if found, None otherwise
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE name = ?", (role_name,))
        row = cursor.fetchone()
        
        if row:
            role_data = dict(row)
            conn.close()
            return Role(
                name=role_data['name'],
                description=role_data['description']
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
        cursor.execute("SELECT * FROM roles ORDER BY name")
        rows = cursor.fetchall()
        
        roles = []
        for row in rows:
            role_data = dict(row)
            roles.append(Role(
                name=role_data['name'],
                description=role_data['description']
            ))
        
        conn.close()
        return roles
        
    @staticmethod
    def update(role_name: str, description: str) -> bool:
        """
        Update a role's description
        
        Args:
            role_name: Name of the role to update
            description: New description
            
        Returns:
            True if role was updated, False if role was not found
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE roles SET description = ? WHERE name = ?", 
            (description, role_name)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
        
    @staticmethod
    def delete(role_name: str) -> bool:
        """
        Delete a role by name
        
        Args:
            role_name: Role name to delete
            
        Returns:
            True if role was deleted, False if role was not found
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roles WHERE name = ?", (role_name,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def role_exists(role_name: str) -> bool:
        """
        Check if a role exists
        
        Args:
            role_name: Role name to check
            
        Returns:
            True if role exists, False otherwise
        """
        conn = RoleService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM roles WHERE name = ?", (role_name,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    @staticmethod
    def validate_role(role_name: str) -> bool:
        """
        Validate if a role name is both valid in the enum and exists in the database
        
        Args:
            role_name: Role name to validate
            
        Returns:
            True if role is valid, False otherwise
        """
        # Check if the role name is valid in the enum
        if not Role.is_valid_role(role_name):
            return False
        
        # Check if the role exists in the database
        return RoleService.role_exists(role_name)
