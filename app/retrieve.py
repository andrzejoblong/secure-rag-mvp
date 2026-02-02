
from fastapi import APIRouter, Body
from app.embedding import get_embedding
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import time

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://rag_user:rag_pass@db:5432/rag_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post("/query")
def query(question: str = Body(...), top_k: int = Body(5)):
    # Retry/backoff for embedding
    for attempt in range(3):
        try:
            embedding = get_embedding(question)
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (2 ** attempt))
            else:
                raise e
    db = SessionLocal()
    sql = text("""
        SELECT c.text, c.metadata, e.embedding <=> :embedding AS score
        FROM chunks c
        JOIN embeddings e ON c.id = e.chunk_id
        ORDER BY score ASC
        LIMIT :top_k
    """)
    results = db.execute(sql, {"embedding": embedding.tolist(), "top_k": top_k}).fetchall()
    return [
        {
            "text": r[0],
            "metadata": r[1],
            "score": r[2]
        } for r in results
    ]
