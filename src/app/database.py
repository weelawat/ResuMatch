from sqlmodel import create_engine, Session
from src.app.config import settings

engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
