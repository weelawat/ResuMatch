from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, Form
from typing import List
import base64
from src.app.tasks.resume_processor import analyze_resume_task
from src.app.database import get_session
from sqlmodel import Session

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    role_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Read file content
    content = await file.read()
    
    # Encode to base64 for JSON serialization in Celery
    content_b64 = base64.b64encode(content).decode('utf-8')
    
    # Trigger celery task
    task = analyze_resume_task.delay(content_b64, role_id, file.filename)
    
    return {
        "filename": file.filename, 
        "role_id": role_id,
        "task_id": task.id,
        "status": "processing started"
    }
