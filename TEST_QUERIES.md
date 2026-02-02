# RAG System - Test Queries

## System is working! 🎉

### Test 1: Invoice Number ✅
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the invoice number?", "top_k": 3}'
```
**Result:** Found EUINPL25-449046 with 47% similarity!

### Test 2: Total Amount
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total amount?", "top_k": 3}'
```

### Test 3: Invoice Date
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "When was the invoice issued?", "top_k": 3}'
```

### Test 4: Customer Name
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the customer?", "top_k": 3}'
```

### Test 5: AWS Services
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What AWS services were charged?", "top_k": 5}'
```

## Summary

✅ **Document Upload** - Working  
✅ **Text Extraction** - Working (pdfplumber)  
✅ **Chunking** - Working (5 chunks created)  
✅ **Embeddings** - Working (Sentence Transformers - LOCAL & FREE!)  
✅ **Semantic Search** - Working (pgvector)  
✅ **Vector Database** - Working (PostgreSQL + pgvector)  

**Total Cost: $0 - Completely FREE!** 🎉

No OpenAI API costs, runs 100% locally with Sentence Transformers!
