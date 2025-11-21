from sqlmodel import SQLModel, create_engine, Session
from src.app.config import settings

engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    from src.app.models.role import RoleProfile
    from src.app.models.candidate import Candidate
    
    SQLModel.metadata.create_all(engine)
