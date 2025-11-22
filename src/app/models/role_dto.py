from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class RoleProfileRead(SQLModel):
    id: int
    title: str
    description: str
    requirements: Optional[str] = None
    created_at: datetime

class RoleProfileCreate(SQLModel):
    title: str
    description: str
    requirements: Optional[str] = None

