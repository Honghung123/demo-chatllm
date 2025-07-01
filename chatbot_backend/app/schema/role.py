from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class RoleName(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    SALES = "sales"
    MARKETING = "marketing"
    LEGAL = "legal"
    FINANCE = "finance"
    IT = "it"


class Role(BaseModel):
    name: str
    description: Optional[str] = None 

    def to_sqlite_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary suitable for SQLite insertion"""
        return {
            "name": self.name,
            "description": self.description or ""
        }
    
    @staticmethod
    def get_all_role_names() -> List[str]:
        """Get all available role names as strings"""
        return [role.value for role in RoleName]
    
    @staticmethod
    def is_valid_role(role_name: str) -> bool:
        """Check if a role name is valid"""
        return role_name in [role.value for role in RoleName]
