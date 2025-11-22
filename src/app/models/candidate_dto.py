from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class CandidateRead(SQLModel):
    id: int
    filename: str
    role_id: int
    match_score: Optional[float] = None
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: Optional[str] = None
    created_at: datetime

