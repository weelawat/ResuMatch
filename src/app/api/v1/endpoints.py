from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from typing import List
from src.app.tasks.resume_processor import process_resume
from src.app.database import get_session
from sqlmodel import Session

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session)
):
    # Placeholder: Read file, save candidate to DB, trigger async task
    content = await file.read()
    # logic to save candidate placeholder
    # candidate = Candidate(...)
    # session.add(candidate)
    # session.commit()
    
    # Trigger celery task
    # process_resume.delay(candidate.id, content)
    
    return {"filename": file.filename, "status": "processing started"}

