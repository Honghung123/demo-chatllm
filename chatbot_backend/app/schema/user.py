from pydantic import BaseModel, Field
from typing import Dict, Any 
from uuid import UUID, uuid4


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    password: str
    role: str 
    
    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "id": str(self.id),
            "username": self.username,
            "password": self.password,
            "role": self.role
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Return a dictionary without sensitive information for API responses"""
        return {
            "id": str(self.id),
            "username": self.username,
            "role": self.role
        }
    
    def verify_password(self, password: str) -> bool: 
        return self.password == password 
