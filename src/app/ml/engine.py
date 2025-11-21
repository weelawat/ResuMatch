from sentence_transformers import SentenceTransformer

# Load model once (if possible, or load per task if memory is tight)
# model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(text1: str, text2: str) -> float:
    # embeddings1 = model.encode(text1)
    # embeddings2 = model.encode(text2)
    # return util.cos_sim(embeddings1, embeddings2)
    return 0.95 # Placeholder

