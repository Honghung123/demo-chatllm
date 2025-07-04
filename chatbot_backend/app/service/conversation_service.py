import sqlite3
from typing import List, Optional
from schema.conversation import Conversation

DB_PATH = "database/db.sqlite3"

class ConversationService: 
    def _get_connection() -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named column access
        return conn

    @staticmethod
    def create_table_if_not_exists() -> None:
        """Create the conversations table if it doesn't exist"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            user_id UUID NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        
    @staticmethod
    def create(conversation: Conversation) -> None:
        """Save a conversation to the database"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        data = conversation.to_sqlite_dict()
        cursor.execute(
            """
            INSERT INTO conversations (id, title, user_id, timestamp) 
            VALUES (:id, :title, :user_id, :timestamp)
            """, 
            data
        )
        conn.commit()
        conn.close() 
    
    @staticmethod
    def get_by_id(conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        row = cursor.fetchone()
        
        if row:
            conversation_data = dict(row)
            conn.close()
            return Conversation(
                id=conversation_data['id'],
                title=conversation_data['title'],
                user_id=conversation_data['user_id'],
                timestamp=conversation_data['timestamp']
            )
        conn.close()
        return None
    
    @staticmethod
    def get_all_by_user_id(user_id: str) -> List[Conversation]:
        """Get all conversations"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conversation_data = dict(row)
            conversations.append(Conversation(
                id=conversation_data['id'],
                title=conversation_data['title'],
                user_id=conversation_data['user_id'],
                timestamp=conversation_data['timestamp']
            ))
        
        conn.close()
        return conversations
        
    @staticmethod
    def update(conversation: Conversation) -> None:
        """Update an existing conversation"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        data = conversation.to_sqlite_dict()
        cursor.execute(
            """
            UPDATE conversations 
            SET title = :title, user_id = :user_id, timestamp = :timestamp 
            WHERE id = :id
            """, 
            data
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(conversation_id: str) -> bool:
        """Delete a conversation by ID"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def search_by_title(search_term: str) -> List[Conversation]:
        """Search conversations by title"""
        conn = ConversationService._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM conversations WHERE title LIKE ? ORDER BY timestamp DESC", 
            (f"%{search_term}%",)
        )
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conversation_data = dict(row)
            conversations.append(Conversation(
                id=conversation_data['id'],
                title=conversation_data['title'],
                user_id=conversation_data['user_id'],
                timestamp=conversation_data['timestamp']
            ))
        
        conn.close()
        return conversations
