import sqlite3
from typing import List, Optional, Dict
from app.service.db_service import DB_PATH
from schema.user import User

class UserService: 
    @staticmethod
    def _get_connection() -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named column access
        return conn

    @staticmethod
    def create_table_if_not_exists() -> None:
        """Create the users table if it doesn't exist"""
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        
    @staticmethod
    def create(user: User) -> None:
        """
        Create a new user
        
        Args:
            user: User object
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        data = user.to_sqlite_dict()
        cursor.execute(
            """
            INSERT INTO users (id, username, password, role) 
            VALUES (:id, :username, :password, :role)
            """, 
            data
        )
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """
        Get a user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            user_data = dict(row)
            conn.close()
            return User(
                id=user_data['id'],
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role']
            )
        conn.close()
        return None
    
    @staticmethod
    def get_all() -> List[User]:
        """
        Get all users
        
        Returns:
            List of User objects
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user_data = dict(row)
            users.append(User(
                id=user_data['id'],
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role']
            ))
        
        conn.close()
        return users
    
    @staticmethod
    def update(user: User) -> bool:
        """
        Update an existing user
        
        Args:
            user: User object with updated information
            
        Returns:
            True if user was updated, False if user was not found
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        data = user.to_sqlite_dict()
        cursor.execute(
            """
            UPDATE users 
            SET password = :password, role = :role 
            WHERE username = :username
            """, 
            data
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    @staticmethod
    def delete(username: str) -> bool:
        """
        Delete a user by username
        
        Args:
            username: Username to delete
            
        Returns:
            True if user was deleted, False if user was not found
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

    @staticmethod
    def get_users_by_role(role: str) -> List[User]:
        """
        Get all users with a specific role
        
        Args:
            role: Role to search for
            
        Returns:
            List of User objects with the specified role
        """
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = ?", (role,))
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user_data = dict(row)
            users.append(User(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role']
            ))
        
        conn.close()
        return users 
    
    @staticmethod
    def delete_all_data() -> None:
        """
        Delete all data from the users table
        """ 
        conn = UserService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        
        
