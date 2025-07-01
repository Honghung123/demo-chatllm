from datetime import datetime 
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

class FileSystem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    orginal_name: str 
    extension: str
    username: str
    timestamp: datetime = Field(default_factory=datetime.now) 
        
    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "id": str(self.id),
            "name": self.name,
            "orginal_name": self.orginal_name,
            "extension": self.extension,
            "username": self.username,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def generate_filename(cls, original_name: str) -> str:
        """Generate a unique filename based on the original name"""
        extension = original_name.split('.')[-1] if '.' in original_name else ''
        unique_id = str(uuid4()).replace('-', '')[:10]
        return f"{unique_id}.{extension}" if extension else unique_id
