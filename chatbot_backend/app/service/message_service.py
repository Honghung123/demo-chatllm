import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
from app.service.db_service import DB_PATH
from schema.message import Message
 
class MessageService: 
    def _get_connection() -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named column access
        return conn

    @staticmethod
    def create_table_if_not_exists() -> None:
        """Create the messages table if it doesn't exist"""
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            summary TEXT,
            content TEXT NOT NULL,
            from_user INTEGER NOT NULL,
            is_error INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        
    @staticmethod
    def create(message: Message) -> None:
        """
        Create a new message
        
        Args:
            message: Message object
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        data = message.to_sqlite_dict()
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, user_id, message_id, content, summary, from_user, is_error, timestamp) 
            VALUES (:conversation_id, :user_id, :message_id, :content, :summary, :from_user, :is_error, :timestamp)
            """, 
            data
        )
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_by_id(message_id: str) -> Optional[Message]:
        """
        Get a message by ID
        
        Args:
            message_id: Message ID to search for
            
        Returns:
            Message object if found, None otherwise
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
        row = cursor.fetchone()
        
        if row:
            message_data = dict(row)
            conn.close()
            return Message.from_sqlite_dict(message_data)
        conn.close()
        return None
        
    @staticmethod
    def get_all_chat(user_id: str, conversation_id: str) -> List[Message]:
        """
        Get all messages for a specific chat
        
        Args:
            chat_id: Chat ID to get messages for
            
        Returns:
            List of Message objects
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY timestamp ASC", (user_id, conversation_id))
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            message_data = dict(row)
            messages.append(Message.from_sqlite_dict(message_data))
        
        conn.close()
        return messages
        
    @staticmethod
    def delete(message_id: str) -> bool:
        """
        Delete a message by ID
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            True if message was deleted, False if message was not found
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
        
    @staticmethod
    def delete_all_by_conversation_id(conversation_id: str) -> int:
        """
        Delete all messages for a specific chat
        
        Args:
            chat_id: Chat ID to delete messages for
            
        Returns:
            Number of messages deleted
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count
    
    @staticmethod
    def search_by_content(conversation_id: str, search_term: str) -> List[Message]:
        """
        Search messages by content in a specific chat
        
        Args:
            chat_id: Chat ID to search messages in
            search_term: Content to search for
            
        Returns:
            List of Message objects matching the search term
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? AND content LIKE ? ORDER BY timestamp ASC", 
            (conversation_id, f"%{search_term}%")
        )
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            message_data = dict(row)
            messages.append(Message.from_sqlite_dict(message_data))
        
        conn.close()
        return messages
    
    @staticmethod
    def get_latest_messages(conversation_id: str, limit: int = 20) -> List[Message]:
        """
        Get the latest messages for a chat
        
        Args:
            chat_id: Chat ID to get messages for
            limit: Maximum number of messages to return
            
        Returns:
            List of latest Message objects
        """
        conn = MessageService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?", 
            (conversation_id, limit)
        )
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            message_data = dict(row)
            messages.append(Message.from_sqlite_dict(message_data))
        
        # Reverse to get chronological order
        messages.reverse()
        
        conn.close()
        return messages
