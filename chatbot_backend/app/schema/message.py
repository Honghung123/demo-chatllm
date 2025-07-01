from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    user_id: UUID
    content: str
    from_user: bool = False
    is_error: bool = False
    timestamp: datetime = Field(default_factory=datetime.now) 
    
    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "message_id": str(self.message_id),
            "conversation_id": str(self.conversation_id),
            "user_id": str(self.user_id),
            "content": self.content,
            "from_user": 1 if self.from_user else 0,  # SQLite doesn't have boolean type
            "is_error": 1 if self.is_error else 0,    # Convert to integer
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_sqlite_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a Message instance from SQLite data"""
        return cls(
            message_id=data['message_id'],
            conversation_id=data['conversation_id'],
            user_id=data['user_id'],
            content=data['content'],
            from_user=bool(data['from_user']),  # Convert from integer to boolean
            is_error=bool(data['is_error']),    # Convert from integer to boolean
            timestamp=data['timestamp']
        )
