from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    resume_text: Optional[str] = None
    resume_vector: Optional[str] = None  # Stored as JSON or specialized vector type if using pgvector
    created_at: datetime = Field(default_factory=datetime.utcnow)

