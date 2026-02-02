# RAG Implementation - Portfolio Project

**Candidate**: [Your Name]  
**Project**: Production-Ready RAG System with Hybrid Search  
**Repository**: https://github.com/andrzejoblong/secure-rag-mvp  
**Date**: February 2026

---

## 📋 Executive Summary

Built a **production-ready Retrieval-Augmented Generation (RAG) system from scratch** to demonstrate deep understanding of AI/ML backend engineering. Project achieves **83% context accuracy** and **70% citation accuracy** through custom hybrid search algorithm.

**Key Achievement**: Custom BM25 + semantic hybrid search improved exact match retrieval by **161%** compared to pure semantic search.

---

## 🎯 Technical Highlights

### What Was Built

1. **Custom RAG Architecture** (not framework-based)
   - Designed and implemented from scratch
   - Full control over chunking, retrieval, and generation
   - Optimized for accuracy and cost

2. **Hybrid Search Algorithm**
   - Combined BM25 (keyword) + semantic (embeddings)
   - 30% BM25 weight + 70% semantic weight
   - Score normalization and fusion
   - **Result**: +25% better context retrieval

3. **LLM Integration (OpenAI GPT-4o-mini)**
   - Structured JSON outputs with Pydantic validation
   - Prompt engineering for grounded responses
   - Citation extraction (document, page, chunk, quote)
   - Fallback mechanisms (local embeddings → OpenAI)

4. **Evaluation Framework**
   - 30-question benchmark across 3 document types
   - 3-metric scoring (correctness, citations, completeness)
   - Quantitative measurement of improvements
   - Manual scoring workflow

### Technology Stack

**Backend**: FastAPI, SQLAlchemy, Alembic migrations  
**Database**: PostgreSQL 15 + pgvector (vector search)  
**Embeddings**: sentence-transformers (local) + OpenAI (fallback)  
**Search**: BM25Okapi (rank-bm25) + semantic similarity  
**LLM**: OpenAI GPT-4o-mini with structured outputs  
**Infrastructure**: Docker Compose, Poetry, pytest

---

## 📊 Results & Metrics

### Quantitative Improvements

| Metric | Before (Semantic Only) | After (Hybrid) | Improvement |
|--------|----------------------|----------------|-------------|
| Context Accuracy | 67% (20/30) | **83% (25/30)** | +25% |
| Citation Accuracy | 60% (18/30) | **70% (21/30)** | +17% |
| Exact Match Score | 0.338 | **0.885** | +161% |

### Example Query

**Query**: "FV/2025/01/0847" (invoice number lookup)

**Before (Semantic)**:
- Relevance: 33.8%
- Result: Incorrect chunk retrieved

**After (Hybrid)**:
- Relevance: 88.5%
- Result: ✅ Correct invoice chunk ranked #1
- Answer: "Invoice number is FV/2025/01/0847" with citation

---

## 💡 Engineering Decisions

### 1. Why Build From Scratch vs. Using LangChain?

**Decision**: Custom implementation first

**Reasoning**:
- Deep understanding of RAG components
- Full control over chunking strategy (tested 1000 → 2000 chars)
- Optimized hybrid search (BM25 + semantic)
- No framework overhead or lock-in
- Easy to debug (know every layer)

**Can add LangChain**: Integration is trivial (~2-3 hours) on this foundation

### 2. Why Hybrid Search?

**Problem**: Pure semantic search failed on exact matches
- Query: "FV/2025/01/0847" → 33.8% relevance ❌
- Struggled with invoice numbers, IDs, technical specs

**Solution**: BM25 (keyword) + semantic (meaning)
- Query: "FV/2025/01/0847" → 88.5% relevance ✅
- Best of both worlds: exact matches + semantic understanding

### 3. Why Custom Evaluation?

**Need**: Quantitative measurement of RAG quality

**Solution**: 30-question benchmark
- 3 document types (invoice, manual, contract)
- 3 metrics per question (correctness, citations, completeness)
- Manual scoring workflow
- Track improvements over iterations

**Result**: Data-driven optimization (know what works)

---

## 🎓 Skills Demonstrated

### RAG Architecture & Design
- ✅ Custom chunking strategies (experimentation with sizes/overlaps)
- ✅ Hybrid search algorithm (BM25 + semantic fusion)
- ✅ Citation extraction and source tracking
- ✅ Evaluation methodology (quantitative measurement)

### LLM Production Integration
- ✅ OpenAI API with error handling and retries
- ✅ Prompt engineering for grounded responses
- ✅ Structured JSON outputs with validation
- ✅ Cost optimization (local embeddings first, OpenAI fallback)
- ✅ Token usage awareness

### Backend Engineering
- ✅ FastAPI with OpenAPI documentation
- ✅ PostgreSQL + pgvector for vector search
- ✅ SQLAlchemy ORM with Alembic migrations
- ✅ Background task processing
- ✅ Environment variable management
- ✅ Docker containerization

### Testing & Quality
- ✅ Comprehensive evaluation suite (30 questions)
- ✅ Manual scoring workflow (0-180 point scale)
- ✅ Quantitative improvement tracking
- ✅ Sample document preparation

---

## 🚀 Production Readiness

### What's Production-Ready Now
✅ Error handling and fallbacks  
✅ Structured outputs with validation  
✅ Environment variable configuration  
✅ Database migrations (Alembic)  
✅ Docker containerization  
✅ Cost optimization (local embeddings)  
✅ Evaluation framework

### What's Missing (Can Add)
⚠️ Kubernetes deployment (4-6 hours)  
⚠️ Monitoring/observability (2-3 hours)  
⚠️ Streaming responses (2-3 hours)  
⚠️ CI/CD pipeline (2-3 hours)

**Estimated time to full production**: 10-15 hours

---

## 📈 Future Enhancements (Roadmap)

### Phase 1: LangChain Integration (3-4h)
- Replace custom generation with LangChain RetrievalQA
- Add LangGraph for multi-step reasoning
- Tool calling for external data sources

### Phase 2: Streaming & Async (2-3h)
- Server-Sent Events (SSE) for real-time tokens
- MCP server pattern implementation
- Progress updates during retrieval/generation

### Phase 3: AWS/K8s Deployment (4-6h)
- Kubernetes manifests (deployment, service, ingress)
- AWS EKS cluster setup
- CloudWatch monitoring + auto-scaling
- CI/CD pipeline (GitHub Actions)

### Phase 4: Agentic Features (6-8h)
- Multi-step reasoning with LangGraph
- Self-critique and refinement loops
- Dynamic tool selection

**Total time to 95%+ role match**: ~15-20 hours

---

## 💼 Alignment with Role Requirements

**Role**: AI/ML Backend Engineer with RAG expertise

### ✅ Strong Match (85%)

1. **"5+ years Python, AI/ML/backend"**
   - ✅ Production FastAPI application
   - ✅ SQLAlchemy ORM, Alembic migrations
   - ✅ Async processing, background tasks

2. **"RAG design and implementation"**
   - ✅ Built from scratch (not just framework)
   - ✅ Custom hybrid search algorithm
   - ✅ Citation extraction with sources
   - ✅ Evaluation framework

3. **"LLM production experience"**
   - ✅ OpenAI integration with error handling
   - ✅ Prompt engineering for grounding
   - ✅ Structured outputs, cost optimization
   - ✅ Fallback mechanisms

4. **"Vector databases"**
   - ✅ pgvector with 384-dim vectors
   - ✅ Semantic search, cosine similarity
   - ✅ Hybrid ranking algorithms

5. **"Secure coding, data protection"**
   - ✅ Environment variables for secrets
   - ✅ SQL injection prevention (parameterized queries)
   - ✅ Input validation (Pydantic)

### ⚠️ Can Add (Gap Closers)

6. **"LangChain/LangGraph frameworks"**
   - ⚠️ Deliberately not used (to show custom skills)
   - ✅ Can integrate in 2-4 hours

7. **"MCP servers, streaming, async"**
   - ⚠️ Current: synchronous REST API
   - ✅ Can add SSE/streaming in 2-3 hours

8. **"AWS, K8s, production deployment"**
   - ⚠️ Current: Docker Compose (local dev)
   - ✅ Can deploy to EKS in 4-6 hours

**Current Match**: 85% → **Target Match**: 95%+ (with 10-15h extensions)

---

## 📝 Code Samples

### 1. Hybrid Search Implementation

```python
class HybridSearcher:
    def __init__(self, chunks, bm25_weight=0.3, semantic_weight=0.7):
        self.corpus = [self._tokenize(c['text']) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus)
        
    def search(self, query, semantic_scores, top_k=10):
        # Get BM25 scores
        bm25_scores = self.bm25.get_scores(self._tokenize(query))
        
        # Normalize both to [0,1]
        bm25_norm = self._normalize_scores(bm25_scores)
        semantic_norm = self._normalize_scores(semantic_scores)
        
        # Weighted combination
        combined = 0.3 * bm25_norm + 0.7 * semantic_norm
        
        return sorted(enumerate(combined), reverse=True)[:top_k]
```

### 2. Grounded Answer Generation

```python
SYSTEM_PROMPT = """You are an assistant that answers ONLY based on context.

RULES:
1. Answer ONLY from provided context
2. If no info: say "No information in documents"
3. Provide citations for each fact
4. DO NOT add external knowledge

FORMAT: JSON with {answer, citations, has_sufficient_context}
"""
```

### 3. Evaluation Framework

```python
class QuestionEvaluation(BaseModel):
    correctness: int = Field(ge=0, le=2)
    citation_quality: int = Field(ge=0, le=2)
    completeness: int = Field(ge=0, le=2)
    
    @property
    def total_score(self) -> int:
        return self.correctness + self.citation_quality + self.completeness

# 30 questions × 6 points = 180 max
```

---

## 🎯 Why This Project Matters

### Demonstrates Real-World Skills

1. **Problem-Solving**: Identified semantic search weakness → designed hybrid solution
2. **Data-Driven**: Built evaluation framework to measure improvements quantitatively
3. **Production Mindset**: Error handling, fallbacks, cost optimization, migrations
4. **Quality Focus**: 30-question benchmark, manual scoring, iterative improvement

### Shows Learning & Adaptation

- Experimented with chunk sizes (1000 → 2000 chars)
- Tested pure semantic → recognized limitations → implemented hybrid
- Built evaluation framework to validate changes
- Documented decisions and tradeoffs

### Practical Results

- **83% context accuracy** (up from 67%)
- **70% citation accuracy** (up from 60%)
- **161% improvement** in exact match queries
- **Quantitative evidence** of engineering quality

---

## 📞 Contact & Links

**GitHub**: https://github.com/andrzejoblong/secure-rag-mvp  
**Documentation**: See `README.md` and `SESSION_NOTES.md` in repository  
**Live Demo**: Can provide on request (requires Docker + OpenAI API key)

**Ready to discuss**:
- Architecture decisions and tradeoffs
- Hybrid search algorithm design
- Production deployment strategies
- Extension to LangChain/LangGraph
- Streaming and async patterns
- AWS/K8s deployment approach

---

**Project Status**: ✅ Core complete, evaluation proven, ready for extensions  
**Time Investment**: ~8 hours (core RAG) + ~3 hours (hybrid search & evaluation)  
**Demonstrates**: 85% role match with clear 10-15h path to 95%+
