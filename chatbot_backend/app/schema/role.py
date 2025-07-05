from pydantic import BaseModel
from typing import Dict, Any
class Role(BaseModel):
    id: str
    displayName: str 

    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "id": self.id,
            "displayName": self.displayName 
        }
 
