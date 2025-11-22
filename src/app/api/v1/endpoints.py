from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from typing import List
import base64
from sqlmodel import Session, select
from src.app.tasks.resume_processor import analyze_resume_task
from src.app.database import get_session
from src.app.models.role import RoleProfile
from src.app.models.candidate import Candidate

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

@router.get("/roles", response_model=List[RoleProfile])
def list_roles(session: Session = Depends(get_session)):
    roles = session.exec(select(RoleProfile)).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleProfile)
def get_role(role_id: int, session: Session = Depends(get_session)):
    role = session.get(RoleProfile, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get("/candidates", response_model=List[Candidate])
def list_candidates(session: Session = Depends(get_session)):
    candidates = session.exec(select(Candidate)).all()
    return candidates

@router.get("/candidates/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: int, session: Session = Depends(get_session)):
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
