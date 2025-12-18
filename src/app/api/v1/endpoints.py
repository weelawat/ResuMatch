from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from typing import List
import base64
from sqlmodel import Session, select
from sentence_transformers import SentenceTransformer
from src.app.tasks.resume_processor import analyze_resume_task
from src.app.database import get_session
from src.app.models.role import RoleProfile
from src.app.models.candidate import Candidate
from src.app.models.role_dto import RoleProfileRead, RoleProfileCreate
from src.app.models.candidate_dto import CandidateRead
from src.app.models.suggestion_dto import SuggestionResponse
from src.app.ml.rag_service import get_rag_service

# Load model for synchronous embedding generation (or consider moving to async task)
# Note: For a simple role creation, running this in-process might be acceptable if low volume
ml_model = SentenceTransformer('all-MiniLM-L6-v2')

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    role_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Read file content
    content = await file.read()
    
    # Create Candidate record first (pending state)
    candidate = Candidate(
        filename=file.filename,
        role_id=role_id,
        match_score=None # Explicitly None to indicate pending
    )
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    
    # Encode to base64 for JSON serialization in Celery
    content_b64 = base64.b64encode(content).decode('utf-8')
    
    # Trigger celery task with candidate_id instead of raw params
    task = analyze_resume_task.delay(content_b64, candidate.id)
    
    return {
        "filename": file.filename, 
        "role_id": role_id,
        "candidate_id": candidate.id,
        "task_id": task.id,
        "status": "processing started"
    }

@router.post("/roles", response_model=RoleProfileRead)
def create_role(role_in: RoleProfileCreate, session: Session = Depends(get_session)):
    # Create db model from input
    role = RoleProfile(**role_in.dict())

    # Generate embedding for the role description + requirements
    text_to_embed = f"{role.title} {role.description} {role.requirements or ''}"
    embedding = ml_model.encode(text_to_embed).tolist()
    
    role.embedding = embedding
    session.add(role)
    session.commit()
    session.refresh(role)
    return role

@router.get("/roles", response_model=List[RoleProfileRead])
def list_roles(session: Session = Depends(get_session)):
    roles = session.exec(select(RoleProfile)).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleProfileRead)
def get_role(role_id: int, session: Session = Depends(get_session)):
    role = session.get(RoleProfile, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get("/candidates", response_model=List[CandidateRead])
def list_candidates(session: Session = Depends(get_session)):
    candidates = session.exec(select(Candidate)).all()
    return candidates

@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, session: Session = Depends(get_session)):
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/candidates/{candidate_id}/suggestions", response_model=SuggestionResponse)
def get_suggestions(candidate_id: int, session: Session = Depends(get_session)):
    """
    Get AI-powered suggestions comparing the candidate's resume with the job description.
    Uses RAG (Retrieval-Augmented Generation) to provide actionable feedback.
    """
    # Fetch candidate
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if resume has been processed
    if not candidate.resume_text:
        raise HTTPException(
            status_code=400, 
            detail="Resume has not been processed yet. Please wait for analysis to complete."
        )
    
    # Fetch the role/job description
    role = session.get(RoleProfile, candidate.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get RAG service and generate suggestions
    rag_service = get_rag_service()
    suggestions = rag_service.generate_suggestions(
        resume_text=candidate.resume_text,
        job_title=role.title,
        job_description=role.description,
        job_requirements=role.requirements,
        match_score=candidate.match_score
    )
    
    return suggestions
