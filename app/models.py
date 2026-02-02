from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DocumentPage(Base):
    __tablename__ = "document_pages"
    id = Column(Integer, primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)

class Embedding(Base):
    __tablename__ = "embeddings"
    chunk_id = Column(Integer, ForeignKey("chunks.id"), primary_key=True)
    # 384 dimensions for all-MiniLM-L6-v2 (local sentence-transformers model)
    # Change to 1536 for OpenAI text-embedding-3-small
    # Change to 768 for all-mpnet-base-v2 (local model)
    embedding = Column(Vector(384))
