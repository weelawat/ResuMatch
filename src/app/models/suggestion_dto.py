from sqlmodel import SQLModel
from typing import List, Optional


class SuggestionResponse(SQLModel):
    """Response model for resume-job comparison suggestions."""
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    keywords_to_add: List[str]
    overall_assessment: str
    match_score: Optional[float] = None
    raw_response: Optional[str] = None
