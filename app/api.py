from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models import Document, DocumentPage, Chunk, Embedding, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import uuid

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://rag_user:rag_pass@db:5432/rag_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/")
def root():
    return {"message": "RAG MVP API running"}

@app.post("/documents")
def upload_document(file: UploadFile = File(...)):
    # Save file
    ext = file.filename.split('.')[-1].lower()
    doc_id = uuid.uuid4()
    path = f"/data/{doc_id}.{ext}"
    with open(path, "wb") as f:
        f.write(file.file.read())
    # Create document record
    db = SessionLocal()
    doc = Document(id=doc_id, title=file.filename, source_type=ext)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": str(doc.id), "title": doc.title}

@app.get("/documents/{doc_id}")
def get_document_status(doc_id: str):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    chunk_count = db.query(Chunk).filter(Chunk.document_id == doc_id).count()
    return {"id": doc_id, "title": doc.title, "chunks": chunk_count}
