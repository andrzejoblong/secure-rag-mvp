
from openai import OpenAI
import numpy as np
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Embedding
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://rag_user:rag_pass@db:5432/rag_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_embedding(text, model="text-embedding-3-small", api_key=None, max_retries=3, retry_delay=2):
    """Generate embedding using OpenAI API (v1.0+)"""
    client = OpenAI(api_key=api_key)
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(input=text, model=model)
            return np.array(response.data[0].embedding)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                raise e

def batch_embeddings(texts, model="text-embedding-3-small", api_key=None, batch_size=64, max_retries=3, retry_delay=2):
    """Generate embeddings for multiple texts"""
    client = OpenAI(api_key=api_key)
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(input=batch, model=model)
                for item in response.data:
                    embeddings.append(np.array(item.embedding))
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    raise e
    return embeddings

def save_embeddings_to_db(chunk_ids, embeddings):
    """Save embeddings to database"""
    db = SessionLocal()
    try:
        for chunk_id, emb in zip(chunk_ids, embeddings):
            db.merge(Embedding(chunk_id=chunk_id, embedding=emb.tolist()))
        db.commit()
    finally:
        db.close()
