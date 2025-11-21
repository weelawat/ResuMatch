from fastapi import FastAPI, Depends
from sqlmodel import Session, text
from redis import Redis
from src.app.api.v1 import endpoints
from src.app.database import get_session
from src.app.config import settings
from src.app.celery_app import celery_app

app = FastAPI(title="ResuMatch API")

app.include_router(endpoints.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ResuMatch API"}

@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    health_status = {"database": "unknown", "redis": "unknown", "celery": "unknown"}
    
    # Database
    try:
        session.exec(text("SELECT 1"))
        health_status["database"] = "ok"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"

    # Redis
    try:
        r = Redis.from_url(settings.REDIS_URL, socket_timeout=1)
        if r.ping():
            health_status["redis"] = "ok"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"

    # Celery
    try:
        inspector = celery_app.control.inspect(timeout=1)
        if inspector.ping():
             health_status["celery"] = "ok"
        else:
             health_status["celery"] = "no workers active"
    except Exception as e:
        health_status["celery"] = f"error: {str(e)}"

    return health_status
