from fastapi import FastAPI
from src.app.api.v1 import endpoints

app = FastAPI(title="ResuMatch API")

app.include_router(endpoints.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ResuMatch API"}
