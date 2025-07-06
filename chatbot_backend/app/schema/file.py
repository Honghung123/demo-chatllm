from datetime import datetime
from typing import Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

class FileSystem(BaseModel):
    name: str
    orginal_name: str
    extension: str
    username: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    @classmethod
    def generate_filename(cls, original_name: str) -> str:
        """Generate a unique filename based on the original name"""
        extension = original_name.split('.')[-1] if '.' in original_name else ''
        unique_id = str(uuid4()).replace('-', '')[:10]
        return f"{unique_id}.{extension}" if extension else unique_id
