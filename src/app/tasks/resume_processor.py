import io
import base64

from sqlmodel import Session
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

from src.app.celery_app import celery_app
from src.app.database import engine
from src.app.models.role import RoleProfile
from src.app.models.candidate import Candidate

# Load ML Model ONCE (Global variable) to save RAM
# Note: In a production Celery setup, this runs when the worker starts
ml_model = SentenceTransformer('all-MiniLM-L6-v2')

@celery_app.task
def analyze_resume_task(file_content_b64: str, role_id: int, filename: str):
    # 1. Decode Content
    try:
        file_content = base64.b64decode(file_content_b64)
    except Exception as e:
        print(f"Error decoding content for {filename}: {e}")
        return None

    # 2. Extract Text
    try:
        pdf = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None

    # 3. Vectorize Resume
    # encode returns a numpy array, convert to list for JSON serialization/storage
    resume_vector = ml_model.encode(text).tolist()

    # 4. Calculate Match (Database Side)
    with Session(engine) as session:
        role = session.get(RoleProfile, role_id)
        
        if not role:
            print(f"Role with id {role_id} not found")
            return None

        # Calculate Cosine Similarity
        # If role has no embedding, we can't match. 
        # Assuming role.embedding is a list of floats.
        if not role.embedding:
             # Fallback or error
             score = 0.0
        else:
             score = cosine_similarity([resume_vector], [role.embedding])[0][0]
             # Ensure score is a standard Python float
             if hasattr(score, 'item'):
                 score = score.item()
        
        # 5. Save Result
        candidate = Candidate(
            filename=filename,
            role_id=role_id,
            match_score=round(float(score) * 100, 2),
            resume_text=text,
            resume_vector=resume_vector
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        
        return candidate.id
