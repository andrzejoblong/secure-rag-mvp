# RAG MVP - Quick Start Guide

## ✅ Current Status

- ✅ PostgreSQL + pgvector running
- ✅ FastAPI application running
- ✅ Document upload working
- ✅ Text extraction (PDF) working
- ✅ Text chunking working
- ⚠️ Embeddings - needs OPENAI_API_KEY

## To Enable Full RAG Search:

### 1. Get OpenAI API Key

Visit: https://platform.openai.com/api-keys

### 2. Restart Application with API Key

```bash
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"
export OPENAI_API_KEY="sk-your-actual-key-here"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Upload Document (will auto-generate embeddings)

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/document.pdf"
```

### 4. Query Documents (Semantic Search)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the invoice amount?",
    "top_k": 5
  }'
```

## Current Test Commands

### Check API Status
```bash
curl http://localhost:8000/
```

### List All Documents
```bash
curl http://localhost:8000/documents
```

### Check Document Details
```bash
curl http://localhost:8000/documents/96c11562-d8b3-49d1-9b68-42c9ab6465a3
```

### API Documentation (Interactive)
Open in browser: http://localhost:8000/docs

## Architecture Summary

```
Upload PDF → Extract Text → Chunk Text → Generate Embeddings → Store in pgvector
                  ✅            ✅              ⚠️ (needs API key)      ✅
```

## What's Working Right Now

Your document "Invoice_EUINPL25_449046.pdf":
- Uploaded: ✅
- Text extracted: ✅
- Split into 5 chunks: ✅
- Stored in database: ✅
- Ready for embeddings: ⏳ (waiting for OpenAI API key)

Once you add the OpenAI API key and re-upload, you'll be able to:
- Search semantically: "What is the total amount?"
- Get relevant chunks with similarity scores
- Build full RAG applications
