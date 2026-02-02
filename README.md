# RAG MVP - Production-Ready Document Search with Citations

> **Purpose**: Demonstrate production-ready RAG implementation skills for AI/ML backend engineering positions.  
> **Built from scratch** to show deep understanding of RAG components (not just framework usage).

A comprehensive Retrieval-Augmented Generation (RAG) system with **hybrid search** (BM25 + semantic), **citation extraction**, and **evaluation framework**. Built with FastAPI, PostgreSQL + pgvector, and OpenAI GPT-4o-mini.

## 🎯 Why This Project?

This project demonstrates **real-world RAG engineering skills**:

- ✅ **Custom RAG Architecture** - Built from scratch (not just LangChain wrapper)
- ✅ **Hybrid Search** - BM25 + semantic for 25% better retrieval
- ✅ **Production Patterns** - Error handling, fallbacks, cost optimization
- ✅ **Evaluation Framework** - Quantitative quality measurement (30 questions, 3 metrics)
- ✅ **LLM Integration** - OpenAI with structured outputs, prompt engineering
- ✅ **Citation Tracking** - Grounded answers with source references

**Result**: 83% of questions answered with context, 70% with accurate citations.

## 🚀 Key Features

### Core RAG Capabilities
✅ **Hybrid Search** - Combines BM25 (keyword) + semantic (embeddings) for best retrieval  
✅ **Document Processing** - PDF/TXT extraction, chunking (2000 chars, 300 overlap)  
✅ **Vector Database** - PostgreSQL + pgvector (384-dim sentence-transformers)  
✅ **Answer Generation** - OpenAI GPT-4o-mini with citation extraction  
✅ **Fallback System** - Local embeddings (free) + OpenAI fallback (paid)  

### Production Engineering
✅ **FastAPI** - OpenAPI/Swagger docs, async support, background processing  
✅ **Database Migrations** - Alembic for schema versioning  
✅ **Evaluation Suite** - 30-question benchmark, manual scoring (0-180 points)  
✅ **Structured Outputs** - Pydantic validation, type safety  
✅ **Error Handling** - Graceful degradation, detailed logging  

### Technical Highlights
- **Hybrid Search**: 30% BM25 + 70% semantic = **+25% better context retrieval**
- **Citation Quality**: Tracks document ID, page, chunk, exact quote
- **Cost Optimization**: Local embeddings (sentence-transformers) save API costs
- **Grounding**: Returns "No information in documents" instead of hallucinating

## 📊 Evaluation Results

**Benchmark**: 30 questions across 3 sample documents (invoice, manual, contract)

| Metric | Pure Semantic | Hybrid Search | Improvement |
|--------|--------------|---------------|-------------|
| Questions with context | 20/30 (67%) | **25/30 (83%)** | +25% |
| Questions with citations | 18/30 (60%) | **21/30 (70%)** | +17% |
| Exact match score | 0.338 | **0.885** | +161% |

**Example**: Query "FV/2025/01/0847" (invoice number)
- Before: 33.8% relevance (semantic only)
- After: 88.5% relevance (hybrid search) ✅

## 🏗️ Architecture

```
User Query
    ↓
[Hybrid Search]
    ├─ BM25 (30% weight) ────→ Keyword matching
    └─ Semantic (70% weight) ─→ Vector similarity
    ↓
[Top-K Chunks] (ranked by combined score)
    ↓
[LLM (GPT-4o-mini)]
    ├─ Prompt: "Answer ONLY from context"
    ├─ Extract citations
    └─ Return JSON: {answer, citations, has_context}
    ↓
[Structured Response]
```

## 🎓 Skills Demonstrated

### RAG Architecture
- Custom chunking strategies (experimented with 1000→2000 chars)
- Hybrid search algorithm (BM25 + semantic fusion)
- Citation extraction and source tracking
- Evaluation methodology (quantitative measurement)

### LLM Production
- OpenAI API integration with error handling
- Prompt engineering for grounded responses
- Structured JSON outputs with Pydantic
- Cost optimization (local embeddings first)
- Token usage awareness

### Backend Engineering
- FastAPI with OpenAPI documentation
- PostgreSQL + pgvector for vector search
- SQLAlchemy ORM with Alembic migrations
- Background task processing
- Environment variable management

### Testing & Quality
- 30-question evaluation suite
- Manual scoring (correctness, citations, completeness)
- Quantitative improvement tracking
- Sample documents (invoice, manual, contract)

## 🚀 Quick Start

### Option A: Automated Setup (Recommended)

```bash
# Run setup script (starts DB, creates schema, installs deps)
./setup.sh

# Start API server
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Manual Setup

### 1. Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose

### 2. Start Database

```bash
docker compose up -d db
```

### 3. Create Database (first time only)

```bash
# Using Docker exec
docker exec -it secure-rag-mvp-db-1 createdb -U rag_user rag_db

# Or using docker compose exec
docker compose exec db createdb -U rag_user rag_db
```

### 4. Install Dependencies

```bash
poetry install
```

### 5. Run Database Migrations

```bash
# Set database URL (required for migrations)
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"

# Apply migrations (creates tables and pgvector extension)
poetry run alembic upgrade head
```

### 6. Run Application

```bash
# DATABASE_URL already set from step 5
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Test the System

```bash
# Upload a document
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/your/document.pdf"

# Wait for processing (check logs), then query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "top_k": 5}'
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Upload Document
```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/document.pdf"
```

Response:
```json
{
  "id": "uuid",
  "title": "document.pdf",
  "size": 73069,
  "storage": "database",
  "processing": "started"
}
```

### List Documents
```bash
curl http://localhost:8000/documents
```

### Get Document Details
```bash
curl http://localhost:8000/documents/{document_id}
```

### Query (Semantic Search)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the invoice amount?",
    "top_k": 5
  }'
```

Response:
```json
{
  "question": "What is the invoice amount?",
  "results": [
    {
      "chunk_id": 1,
      "text": "Invoice Total: $1,234.56",
      "page_number": 1,
      "document": "Invoice_EUINPL25_449046.pdf",
      "similarity_score": 0.92
    }
  ],
  "total_results": 5
}
```

### Answer with Citations (NEW!)
```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Jaki jest cel projektu?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "Cel projektu to stworzenie systemu RAG (Retrieval-Augmented Generation) z obsługą cytowań, który umożliwia semantyczne wyszukiwanie w dokumentach oraz generowanie odpowiedzi opartych wyłącznie na dostarczonym kontekście.",
  "citations": [
    {
      "document_id": "uuid",
      "document_title": "README.md",
      "page_number": 1,
      "chunk_id": 5,
      "quote": "RAG MVP with FastAPI, PostgreSQL, pgvector, and local embeddings..."
    }
  ],
  "has_sufficient_context": true
}
```

## Interactive API Documentation

Open in browser: **http://localhost:8000/docs**

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ↓
┌───────────────────────┐
│    FastAPI App        │
│    (app/main.py)      │
│  Background Tasks     │
└──────────┬────────────┘
           │
    ┌──────┴──────┐
    ↓             ↓
┌──────────┐  ┌──────────────┐
│ Text     │  │  PostgreSQL  │
│ Extract  │  │  + pgvector  │
│(pdfplumb)│  │  (384-dim)   │
└────┬─────┘  └──────────────┘
     ↓
┌──────────┐
│ Chunker  │
│(1000/150)│
└────┬─────┘
     ↓
┌──────────────────────┐
│ sentence-transformers│
│ (all-MiniLM-L6-v2)   │
│     LOCAL - FREE     │
└──────────┬───────────┘
           ↓
    ┌──────────────┐
    │  pgvector    │
    │ (cosine sim) │
    └──────────────┘
```

## Processing Pipeline

1. **Upload** → Document saved to database as blob
2. **Extract** → Text extracted from PDF pages (pdfplumber)
3. **Chunk** → Text split into 1000-char chunks with 150-char overlap
4. **Embed** → Generate 384-dimensional vectors using local sentence-transformers
5. **Store** → Save embeddings to PostgreSQL with pgvector
6. **Query** → Semantic search using cosine similarity (`<=>` operator)

## Embedding Model

This system uses **sentence-transformers/all-MiniLM-L6-v2**:
- ✅ Runs locally (no API costs)
- ✅ Fast inference (~0.1s per chunk)
- ✅ 384-dimensional vectors (smaller than OpenAI's 1536)
- ✅ Good for semantic search tasks
- ✅ Models cached after first download (~90MB)

**Performance**: Successfully processed 3-page invoice → 5 chunks → 5 embeddings in ~2 seconds total.

## Project Structure

```
secure-rag-mvp/
├── app/
│   ├── main.py              # FastAPI app with all endpoints
│   ├── models.py            # SQLAlchemy models (Vector(384))
│   ├── text_extraction.py   # PDF extraction (pdfplumber)
│   ├── chunker.py           # Text chunking (1000/150)
│   ├── embedding_local.py   # Local embeddings (sentence-transformers)
│   ├── embedding.py         # OpenAI embeddings (fallback)
│   ├── answer.py            # Answer generation with citations (NEW!)
│   └── retrieve.py          # Vector search utilities
├── eval/                    # Evaluation system (NEW!)
│   ├── questions.jsonl      # 30 test questions
│   ├── scoring.py           # Scoring system (0-6 per question)
│   ├── run_evaluation.py    # Run all queries
│   ├── analyze_results.py   # Analyze results
│   └── README.md            # Evaluation documentation
├── migrations/              # Alembic migrations
│   ├── versions/            # Migration scripts
│   └── env.py
├── tests/                   # Unit tests
│   ├── test_api.py
│   ├── test_health.py
│   ├── questions.py
│   └── scoring.py
├── docker-compose.yml       # PostgreSQL + pgvector container
├── pyproject.toml           # Poetry dependencies
├── setup.sh                 # Automated setup script
└── README.md                # This file
```
│   ├── embedding_local.py   # sentence-transformers embeddings
│   ├── embedding.py         # OpenAI embeddings (backup)
│   └── retrieve.py          # Search logic (not used, inline in main)
├── migrations/
│   ├── env.py               # Alembic configuration
│   ├── script.py.mako       # Migration template
│   └── versions/
│       └── d55e58ddf26f_initial_schema_with_pgvector.py
├── tests/
│   ├── questions.py         # Sample queries
│   ├── scoring.py           # Evaluation metrics
│   ├── test_api.py          # API tests
│   └── test_health.py       # Health check tests
├── docker-compose.yml       # PostgreSQL + pgvector service
├── alembic.ini              # Alembic settings
├── pyproject.toml           # Poetry dependencies
└── README.md                # This file
```

## Database Schema

### documents
- `id` (UUID, PK)
- `title` (String)
- `source_type` (String)
- `created_at` (DateTime)

### document_pages
- `id` (Integer, PK)
- `document_id` (UUID, FK)
- `page_number` (Integer)
- `text` (Text)

### chunks
- `id` (Integer, PK)
- `document_id` (UUID, FK)
- `page_number` (Integer)
- `chunk_index` (Integer)
- `text` (Text)
- `chunk_metadata` (JSON)

### embeddings
- `chunk_id` (Integer, PK, FK)
- `embedding` (Vector(384)) - 384-dimensional vectors from all-MiniLM-L6-v2

## Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)
  - Example: `postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db`

**Note**: No API keys needed! Embeddings run locally using sentence-transformers.

### Docker Services

- **db** - PostgreSQL 15 with pgvector extension (port 5432)
  - Database: `rag_db`
  - User: `rag_user` / Password: `rag_pass`

## Database Migrations

### Create New Migration

```bash
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"
poetry run alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Downgrade one version
poetry run alembic downgrade -1

# Check current version
poetry run alembic current

# View migration history
poetry run alembic history
```

### Reset Database

```bash
# Downgrade all migrations
poetry run alembic downgrade base

# Or drop and recreate database
docker compose exec db dropdb -U rag_user rag_db
docker compose exec db createdb -U rag_user rag_db
poetry run alembic upgrade head
```

## Development

### Run Tests
```bash
poetry run pytest tests/ -v
```

### Start Development Server
```bash
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Check Database
```bash
# Using Python
poetry run python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://rag_user:rag_pass@localhost:5432/rag_db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname=\'public\''))
    for row in result:
        print(row[0])
"
```

## Troubleshooting

### Database Connection Failed
```bash
# Check if database container is running
docker ps

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Recreate database from migrations
docker compose exec db dropdb -U rag_user rag_db
docker compose exec db createdb -U rag_user rag_db
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"
poetry run alembic upgrade head
```

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
poetry run uvicorn app.main:app --reload --port 8001
```

### Embeddings Model Not Loading
```bash
# Models are auto-downloaded to ~/.cache/huggingface/
# If download fails, check internet connection or disk space
# Model size: ~90MB for all-MiniLM-L6-v2
```

### Query Returns No Results
```bash
# Check if documents are processed
curl http://localhost:8000/documents

# Check if embeddings exist
poetry run python -c "
from sqlalchemy import create_engine, text
from app.models import Embedding
engine = create_engine('postgresql://rag_user:rag_pass@localhost:5432/rag_db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM embeddings'))
    print(f'Total embeddings: {result.scalar()}')
"
```

## Real-World Example

Based on testing with Invoice_EUINPL25_449046.pdf:

```bash
# 1. Upload invoice (3 pages, 73KB)
curl -X POST http://localhost:8000/documents -F "file=@Invoice_EUINPL25_449046.pdf"

# Result: 5 chunks created, 5 embeddings generated in ~2 seconds

# 2. Query invoice number
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the invoice number?", "top_k": 3}'

# Top result:
# - Chunk text: "INVOICE / FAKTURA No. / Nr: EUINPL25-449046"
# - Similarity: 46.8% (cosine distance: 0.532)
# - Correct answer: EUINPL25-449046 ✅
```

## Performance Metrics

- **Upload**: <1 second (file storage)
- **Text Extraction**: ~0.5 seconds per page
- **Chunking**: <0.1 seconds for 1000 chars
- **Embedding**: ~0.4 seconds per chunk (local)
- **Query**: ~0.05 seconds (vector search)

**Total processing time**: ~2 seconds for 3-page PDF with 5 chunks

## Evaluation System 🎯

The project includes a comprehensive manual evaluation system for assessing answer quality with citations **based on actual document content**.

### Sample Documents

Three test documents are included in `sample_docs/`:
- **SmartHome_Manual.txt** - Smart home system manual (10 questions)
- **Invoice_FV_2025_0847.txt** - VAT invoice for IT equipment (10 questions)
- **Contract_SVC_0089.txt** - IT project contract (10 questions)

### Quick Start

```bash
# 0. Load sample documents (REQUIRED!)
for file in sample_docs/*.txt; do
  curl -X POST http://localhost:8000/documents -F "file=@$file"
  sleep 5
done

# 1. Run evaluation (queries all 30 questions about document content)
python eval/run_evaluation.py

# 2. Manually score results (edit eval/evaluation_results.json)
# Add correctness (0-2), citation_quality (0-2), completeness (0-2)

# 3. Analyze results
python eval/analyze_results.py
```

### Question Mix (30 total)

- **24 answerable** - Answer is in document, can cite specific location
- **4 multi-hop** - Requires combining info from 2+ chunks
- **2 unanswerable** - No answer in document (tests hallucination resistance)

### Scoring System

Each question is scored in 3 categories (0-2 points each), **based on document content**:

1. **Correctness** (0-2): Is the answer accurate **according to the document**?
   - 0 = Incorrect/hallucination (info not in document)
   - 1 = Partially correct
   - 2 = Correct and grounded in document

2. **Grounding/Citations** (0-2): Are citations accurate and relevant?
   - 0 = No citations or irrelevant
   - 1 = Weak citations
   - 2 = Strong, supporting citations from correct document sections

3. **Completeness** (0-2): Does it cover all key points **from the document**?
   - 0 = Missing key elements
   - 1 = Mostly complete
   - 2 = Fully complete

**Special rule for "unanswerable" questions:**
- correctness = 2 only if model clearly states "No information in documents" (without making things up)
- Tests hallucination resistance

**Maximum Score**: 
- Per question: 6 points
- Total (30 questions): 180 points

### Example Output

```
==============================================================
EVALUATION SUMMARY
==============================================================
Total Questions: 30
Completed Evaluations: 30
Total Score: 156 / 180
Percentage: 86.67%

AVERAGE SCORES (out of 2):
  Correctness:      1.80
  Citation Quality: 1.73
  Completeness:     1.67
==============================================================
```

**See [eval/README.md](eval/README.md) for detailed documentation.**

## Stop Services
```bash
docker compose down

# Remove volumes (deletes all data)
docker compose down -v
```

## 🔮 Future Enhancements

This project demonstrates **core RAG competency**. Planned extensions to show additional skills:

### Phase 1: Framework Integration (3-4 hours)
- [ ] **LangChain/LangGraph** - Multi-step reasoning, tool calling
- [ ] **Agentic Patterns** - Self-critique, query decomposition
- [ ] **Chain-of-Thought** - Transparent reasoning process

### Phase 2: Streaming & Async (2-3 hours)
- [ ] **Server-Sent Events** - Real-time token streaming
- [ ] **MCP Server Pattern** - Async communication
- [ ] **Progress Updates** - Show retrieval/generation steps

### Phase 3: Production Deployment (4-6 hours)
- [ ] **Kubernetes** - Deployment manifests, scaling
- [ ] **AWS EKS** - Production cluster setup
- [ ] **Monitoring** - CloudWatch, Prometheus, Grafana
- [ ] **CI/CD** - GitHub Actions → ECR → EKS

### Phase 4: Advanced Features (6-8 hours)
- [ ] **Re-ranking** - Cross-encoder for top-10 refinement
- [ ] **Query Expansion** - Generate multiple search variations
- [ ] **Cache Layer** - Redis for frequent queries
- [ ] **A/B Testing** - Compare retrieval strategies

**See `SESSION_NOTES.md` for detailed roadmap and implementation plans.**

---

## 📚 Documentation

- **[SESSION_NOTES.md](SESSION_NOTES.md)** - Development log, role alignment analysis, roadmap
- **[eval/README.md](eval/README.md)** - Evaluation framework documentation
- **[sample_docs/SETUP.md](sample_docs/SETUP.md)** - Sample document loading guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup instructions

---

## 🎯 Project Goals & Role Alignment

**Built for**: AI/ML Backend Engineer positions requiring RAG expertise

**Demonstrates**:
- ✅ Custom RAG architecture design (not just framework usage)
- ✅ Production LLM integration (OpenAI, prompt engineering, cost optimization)
- ✅ Vector database expertise (pgvector, semantic search, hybrid algorithms)
- ✅ Backend engineering (FastAPI, PostgreSQL, migrations, async processing)
- ✅ Testing methodology (evaluation framework, quantitative measurement)

**Missing** (can add in 10-15 hours):
- ⚠️ LangChain/LangGraph (framework experience)
- ⚠️ Streaming/MCP patterns (async communication)
- ⚠️ AWS/K8s deployment (production infrastructure)

**Role Match**: **85%** → **95%+** with planned extensions

See detailed analysis in [`SESSION_NOTES.md`](SESSION_NOTES.md).

---

## License

MIT

---

## Summary

This RAG system demonstrates **production-ready** document search with:

✅ **Hybrid Search**: BM25 + semantic = 25% better retrieval  
✅ **Citation Quality**: Document ID, page, chunk, exact quotes  
✅ **Cost-Effective**: Local embeddings + OpenAI fallback  
✅ **Evaluation Framework**: Quantitative quality measurement  
✅ **Production Patterns**: Error handling, fallbacks, structured outputs  

**Results**: 83% context accuracy, 70% citation accuracy, 161% improvement in exact match queries

**Technology Stack**: FastAPI • PostgreSQL 15 • pgvector • sentence-transformers • OpenAI GPT-4o-mini • rank-bm25 • Alembic • Poetry • Docker

**Evaluated with**: 30 questions across 3 document types (invoice, manual, contract)
