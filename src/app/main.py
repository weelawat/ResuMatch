from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.database import create_db_and_tables
from src.app.api.v1 import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="ResuMatch API", lifespan=lifespan)

app.include_router(endpoints.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ResuMatch API"}

