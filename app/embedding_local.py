"""
Local embedding module using Sentence Transformers (no API key required)
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Embedding
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load model once (cached)
_model = None

def get_model(model_name="all-MiniLM-L6-v2"):
    """
    Load sentence transformer model (cached after first call)
    
    Popular models:
    - all-MiniLM-L6-v2 (384 dim, fast, good quality)
    - all-mpnet-base-v2 (768 dim, slower, better quality)
    - paraphrase-multilingual-MiniLM-L12-v2 (384 dim, supports Polish)
    """
    global _model
    if _model is None:
        print(f"Loading local embedding model: {model_name}...")
        _model = SentenceTransformer(model_name)
        print(f"✓ Model loaded successfully")
    return _model

def get_embedding(text, model_name="all-MiniLM-L6-v2"):
    """Generate embedding for single text using local model"""
    model = get_model(model_name)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding

def batch_embeddings(texts, model_name="all-MiniLM-L6-v2", batch_size=32):
    """Generate embeddings for multiple texts"""
    model = get_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    return [emb for emb in embeddings]

def save_embeddings_to_db(chunk_ids, embeddings):
    """Save embeddings to database"""
    db = SessionLocal()
    try:
        for chunk_id, emb in zip(chunk_ids, embeddings):
            # Convert to list for JSON storage
            if isinstance(emb, np.ndarray):
                emb = emb.tolist()
            db.merge(Embedding(chunk_id=chunk_id, embedding=emb))
        db.commit()
        print(f"✓ Saved {len(chunk_ids)} embeddings to database")
    finally:
        db.close()

# Model recommendations by use case:
MODELS = {
    "fast": "all-MiniLM-L6-v2",           # 384 dim, fastest
    "balanced": "all-mpnet-base-v2",       # 768 dim, balanced
    "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",  # 384 dim, 50+ languages
    "best": "sentence-transformers/all-mpnet-base-v2"  # 768 dim, best quality
}
