from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class Conversation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    title: str
    timestamp: datetime = Field(default_factory=datetime.now) 
        
    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "id": str(self.id),
            "title": self.title,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat()
        }
