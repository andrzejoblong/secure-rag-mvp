from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
import os
import uuid
from typing import Dict, Optional, List
from pydantic import BaseModel, Field

app = FastAPI(
    title="RAG MVP API",
    version="1.0.0",
    description="Retrieval-Augmented Generation API with citations support"
)

# Check if database is configured
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_DATABASE = DATABASE_URL is not None
EMBEDDING_TYPE = None  # Initialize globally

if USE_DATABASE:
    try:
        from app.models import Document, Chunk, Embedding, DocumentPage, Base
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from app.text_extraction import extract_text
        from app.chunker import chunk_pages
        from app.answer import generate_answer, AnswerWithCitations, Citation
        
        # Try local embeddings first, fall back to OpenAI
        try:
            from app.embedding_local import get_embedding, batch_embeddings
            EMBEDDING_TYPE = "local"
            print("✓ Using local embeddings (Sentence Transformers)")
        except ImportError:
            if OPENAI_API_KEY:
                from app.embedding import get_embedding, batch_embeddings
                EMBEDDING_TYPE = "openai"
                print("✓ Using OpenAI embeddings")
            else:
                EMBEDDING_TYPE = None
                print("⚠ No embedding system available")
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print(f"✓ Database connected: {DATABASE_URL}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        USE_DATABASE = False
        EMBEDDING_TYPE = None
else:
    EMBEDDING_TYPE = None

# In-memory storage (fallback when no database)
documents_db: Dict[str, dict] = {}

# Request models
class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        description="The question or search query to find relevant document chunks",
        example="What are the main security features of the system?"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of most relevant chunks to return (1-50)",
        example=5
    )

# Response models
class QueryResultItem(BaseModel):
    chunk_id: int = Field(..., description="Unique identifier of the chunk")
    text: str = Field(..., description="The text content of the chunk")
    page_number: int = Field(..., description="Page number where this chunk appears")
    metadata: Optional[Dict] = Field(None, description="Additional metadata about the chunk")
    document: str = Field(..., description="Title of the source document")
    similarity_score: float = Field(..., description="Similarity score (0-1, higher is more similar)")

class QueryResponse(BaseModel):
    question: str = Field(..., description="The original question that was queried")
    embedding_type: str = Field(..., description="Type of embedding used (local or openai)")
    results: List[QueryResultItem] = Field(..., description="List of relevant chunks ordered by similarity")
    total_results: int = Field(..., description="Total number of results returned")

def process_document_async(doc_id: str, file_path: str, db):
    """Background task to process document: extract text, chunk, embed"""
    try:
        print(f"Processing document {doc_id}...")
        
        # 1. Extract text from PDF
        pages = extract_text(file_path)
        print(f"  ✓ Extracted {len(pages)} pages")
        
        # 2. Save pages to database
        for page_num, page_text in enumerate(pages):
            page = DocumentPage(
                document_id=uuid.UUID(doc_id),
                page_number=page_num + 1,
                text=page_text
            )
            db.add(page)
        db.commit()
        print(f"  ✓ Saved pages to database")
        
        # 3. Chunk text
        chunks_data = chunk_pages(pages, chunk_size=1000, overlap=150)
        print(f"  ✓ Created {len(chunks_data)} chunks")
        
        # 4. Save chunks to database
        chunk_ids = []
        for chunk_data in chunks_data:
            chunk = Chunk(
                document_id=uuid.UUID(doc_id),
                page_number=chunk_data["page_number"],
                chunk_index=chunk_data["chunk_index"],
                text=chunk_data["text"],
                chunk_metadata={"page": chunk_data["page_number"]}
            )
            db.add(chunk)
            db.flush()
            chunk_ids.append(chunk.id)
        db.commit()
        print(f"  ✓ Saved chunks to database")
        
        # 5. Generate embeddings if available
        if EMBEDDING_TYPE:
            print(f"  → Generating embeddings using {EMBEDDING_TYPE}...")
            for chunk_id, chunk_data in zip(chunk_ids, chunks_data):
                try:
                    if EMBEDDING_TYPE == "openai":
                        embedding_vector = get_embedding(
                            chunk_data["text"],
                            api_key=OPENAI_API_KEY
                        )
                    else:  # local
                        embedding_vector = get_embedding(chunk_data["text"])
                    
                    embedding = Embedding(
                        chunk_id=chunk_id,
                        embedding=embedding_vector.tolist() if hasattr(embedding_vector, 'tolist') else embedding_vector
                    )
                    db.merge(embedding)
                except Exception as e:
                    print(f"  ✗ Failed to generate embedding for chunk {chunk_id}: {e}")
            db.commit()
            print(f"  ✓ Generated and saved embeddings")
        else:
            print(f"  ⚠ Skipping embeddings (no embedding system available)")
        
        print(f"✓ Document {doc_id} processed successfully!")
        
    except Exception as e:
        print(f"✗ Error processing document {doc_id}: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
def root():
    embedding_status = "not available"
    if USE_DATABASE and EMBEDDING_TYPE:
        embedding_status = f"{EMBEDDING_TYPE} (ready)"
    
    return {
        "message": "RAG MVP API running",
        "database": "connected" if USE_DATABASE else "in-memory",
        "embeddings": embedding_status,
        "endpoints": {
            "docs": "/docs",
            "upload": "POST /documents",
            "list": "GET /documents",
            "detail": "GET /documents/{id}",
            "query": "POST /query"
        }
    }

@app.get("/health")
def health():
    doc_count = len(documents_db) if not USE_DATABASE else "N/A"
    return {
        "status": "healthy",
        "database": "connected" if USE_DATABASE else "in-memory",
        "openai": "configured" if OPENAI_API_KEY else "not configured",
        "documents_count": doc_count
    }

@app.post("/documents")
def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Save file
    ext = file.filename.split('.')[-1].lower()
    doc_id = str(uuid.uuid4())
    
    # Create data directory if it doesn't exist
    os.makedirs("/tmp/rag_data", exist_ok=True)
    path = f"/tmp/rag_data/{doc_id}.{ext}"
    
    # Read and save file
    content = file.file.read()
    file_size = len(content)
    
    with open(path, "wb") as f:
        f.write(content)
    
    if USE_DATABASE:
        # Store in database
        db = SessionLocal()
        try:
            doc = Document(id=uuid.UUID(doc_id), title=file.filename, source_type=ext)
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            # Process document in background
            if background_tasks:
                background_tasks.add_task(process_document_async, doc_id, path, SessionLocal())
            
            return {
                "id": str(doc.id),
                "title": doc.title,
                "size": file_size,
                "storage": "database",
                "processing": "started" if background_tasks else "queued"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
    else:
        # Store in memory
        documents_db[doc_id] = {
            "id": doc_id,
            "title": file.filename,
            "source_type": ext,
            "path": path,
            "size": file_size,
            "chunks": 0
        }
        
        return {
            "id": doc_id,
            "title": file.filename,
            "size": file_size,
            "storage": "in-memory"
        }

@app.get("/documents")
def list_documents():
    if USE_DATABASE:
        db = SessionLocal()
        try:
            docs = db.query(Document).all()
            result = []
            for d in docs:
                chunk_count = db.query(Chunk).filter(Chunk.document_id == d.id).count()
                result.append({
                    "id": str(d.id),
                    "title": d.title,
                    "source_type": d.source_type,
                    "chunks": chunk_count,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                })
            return {
                "documents": result,
                "total": len(result),
                "storage": "database"
            }
        finally:
            db.close()
    else:
        return {
            "documents": list(documents_db.values()),
            "total": len(documents_db),
            "storage": "in-memory"
        }

@app.get("/documents/{doc_id}")
def get_document_status(doc_id: str):
    if USE_DATABASE:
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
            chunk_count = db.query(Chunk).filter(Chunk.document_id == doc_id).count()
            embedding_count = db.query(Embedding).join(Chunk).filter(Chunk.document_id == doc_id).count()
            return {
                "id": str(doc.id),
                "title": doc.title,
                "source_type": doc.source_type,
                "chunks": chunk_count,
                "embeddings": embedding_count,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "storage": "database"
            }
        finally:
            db.close()
    else:
        if doc_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents_db[doc_id]
        return {
            "id": doc_id,
            "title": doc["title"],
            "source_type": doc["source_type"],
            "size": doc["size"],
            "chunks": doc["chunks"],
            "storage": "in-memory"
        }

@app.post("/query", response_model=QueryResponse, tags=["Query"])
def query_documents(
    query: QueryRequest
):
    """
    Query documents using semantic search to find most relevant chunks.
    
    This endpoint performs Retrieval-Augmented Generation (RAG) by:
    1. Converting the question into an embedding vector
    2. Searching for the most similar document chunks using vector similarity
    3. Returning the top-k most relevant chunks with their metadata
    
    **Requirements:**
    - Database connection must be configured
    - Embedding system must be available (local Sentence Transformers or OpenAI)
    - At least one document must be uploaded and processed
    
    **Example Request:**
    ```json
    {
        "question": "What are the security features?",
        "top_k": 5
    }
    ```
    
    **Returns:**
    - List of most relevant document chunks
    - Similarity scores for each chunk
    - Source document and page information
    
    **Errors:**
    - 501: Database or embedding system not configured
    - 500: Query processing failed
    """
    if not USE_DATABASE:
        raise HTTPException(status_code=501, detail="Query requires database connection")
    
    if not EMBEDDING_TYPE:
        raise HTTPException(status_code=501, detail="Query requires embedding system (install sentence-transformers or set OPENAI_API_KEY)")
    
    db = SessionLocal()
    try:
        # Generate embedding for query
        if EMBEDDING_TYPE == "openai":
            query_embedding = get_embedding(query.question, api_key=OPENAI_API_KEY)
        else:  # local
            query_embedding = get_embedding(query.question)
        
        # Convert to list if numpy array
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()
        
        # Search for similar chunks using pgvector
        # Use CAST to convert array to vector type
        sql = text("""
            SELECT 
                c.id,
                c.text,
                c.page_number,
                c.chunk_metadata,
                d.title,
                e.embedding <=> CAST(:embedding AS vector) AS distance
            FROM chunks c
            JOIN embeddings e ON c.id = e.chunk_id
            JOIN documents d ON c.document_id = d.id
            ORDER BY distance ASC
            LIMIT :top_k
        """)
        
        results = db.execute(
            sql,
            {"embedding": query_embedding, "top_k": query.top_k}
        ).fetchall()
        
        return {
            "question": query.question,
            "embedding_type": EMBEDDING_TYPE,
            "results": [
                {
                    "chunk_id": r[0],
                    "text": r[1],
                    "page_number": r[2],
                    "metadata": r[3],
                    "document": r[4],
                    "similarity_score": 1 - float(r[5])  # Convert distance to similarity
                }
                for r in results
            ],
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
    finally:
        db.close()


@app.post("/answer", response_model=AnswerWithCitations, tags=["Answer"])
def answer_question(
    query: QueryRequest
):
    """
    Answer a question with citations from source documents.
    
    This endpoint performs RAG with citation support:
    1. Retrieves relevant chunks using vector similarity search
    2. Uses LLM (OpenAI) to generate a grounded answer
    3. Returns answer with specific citations (document, page, chunk, quote)
    
    **Key Features:**
    - Answers ONLY based on provided context
    - Returns "Brak informacji w dokumentach" if context insufficient
    - Each fact in the answer is backed by a citation
    - Citations include: document_id, page_number, chunk_id, and quote
    
    **Requirements:**
    - Database connection must be configured
    - Embedding system must be available
    - OPENAI_API_KEY recommended for best results (falls back to simple extraction)
    
    **Example Request:**
    ```json
    {
        "question": "Jakie są główne funkcje systemu?",
        "top_k": 5
    }
    ```
    
    **Returns:**
    - `answer`: The generated answer (or "Brak informacji w dokumentach")
    - `citations`: List of citations with document references
    - `has_sufficient_context`: Whether enough context was available
    
    **Errors:**
    - 501: Database or embedding system not configured
    - 500: Answer generation failed
    """
    if not USE_DATABASE:
        raise HTTPException(status_code=501, detail="Answer endpoint requires database connection")
    
    if not EMBEDDING_TYPE:
        raise HTTPException(status_code=501, detail="Answer endpoint requires embedding system")
    
    db = SessionLocal()
    try:
        # 1. Generate embedding for query
        if EMBEDDING_TYPE == "openai":
            query_embedding = get_embedding(query.question, api_key=OPENAI_API_KEY)
        else:  # local
            query_embedding = get_embedding(query.question)
        
        # Convert to list if numpy array
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()
        
        # 2. Search for similar chunks
        sql = text("""
            SELECT 
                c.id,
                c.text,
                c.page_number,
                c.chunk_metadata,
                d.title,
                d.id as document_id,
                e.embedding <=> CAST(:embedding AS vector) AS distance
            FROM chunks c
            JOIN embeddings e ON c.id = e.chunk_id
            JOIN documents d ON c.document_id = d.id
            ORDER BY distance ASC
            LIMIT :top_k
        """)
        
        results = db.execute(
            sql,
            {"embedding": query_embedding, "top_k": query.top_k}
        ).fetchall()
        
        # 3. Prepare chunks for answer generation
        chunks = [
            {
                "chunk_id": r[0],
                "text": r[1],
                "page_number": r[2],
                "metadata": r[3],
                "document": r[4],
                "document_id": str(r[5]),
                "similarity_score": 1 - float(r[6])
            }
            for r in results
        ]
        
        # 4. Generate answer with citations
        use_openai = OPENAI_API_KEY is not None
        answer = generate_answer(query.question, chunks, use_openai=use_openai)
        
        return answer
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")
    finally:
        db.close()
