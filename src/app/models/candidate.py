from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, JSON

class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    role_id: int = Field(foreign_key="roleprofile.id")
    match_score: Optional[float] = None
    
    # Optional metadata
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: Optional[str] = None
    resume_vector: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
