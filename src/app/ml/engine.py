from sentence_transformers import SentenceTransformer

# Load ML Model ONCE (Global variable) to save RAM
# Note: In a production Celery setup, this runs when the worker starts
ml_model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(text1: str, text2: str) -> float:
    # embeddings1 = model.encode(text1)
    # embeddings2 = model.encode(text2)
    # return util.cos_sim(embeddings1, embeddings2)
    return 0.95 # Placeholder

