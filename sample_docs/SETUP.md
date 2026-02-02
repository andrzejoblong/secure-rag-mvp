# Setup Sample Documents

This guide describes how to load sample documents into the RAG system before running evaluation.

## 📁 Sample Documents

The system contains 3 sample test documents:

1. **SmartHome_Manual.txt** - Smart Home Pro v2.1 User Manual
   - 10 technical sections
   - Requirements, installation, configuration, troubleshooting
   - ~7000 words

2. **Invoice_FV_2025_0847.txt** - VAT Invoice
   - 10 line items (laptops, monitors, IT accessories)
   - Financial details, payment terms
   - ~1500 words

3. **Contract_SVC_0089.txt** - IT Project Service Agreement
   - 10 paragraphs: scope, timeline, payment, warranty
   - Milestones, penalties, copyright
   - ~3500 words

## 🚀 How to Load Documents

### Option A: Via API (recommended)

```bash
# Ensure API is running
curl http://localhost:8000/health

# Load all 3 documents
for file in sample_docs/*.txt; do
  echo "Uploading $file..."
  curl -X POST http://localhost:8000/documents \
    -F "file=@$file"
  echo ""
  sleep 5  # Wait for processing
done
```

### Option B: Via Swagger UI

1. Open http://localhost:8000/docs
2. Endpoint `POST /documents`
3. Click "Try it out"
4. Upload each file from `sample_docs/`
5. Wait until processing is complete (check logs)

### Option C: Python Script

```python
import requests
import time
from pathlib import Path

API_URL = "http://localhost:8000"
DOCS_DIR = Path("sample_docs")

for doc_file in DOCS_DIR.glob("*.txt"):
    print(f"Uploading {doc_file.name}...")
    
    with open(doc_file, 'rb') as f:
        response = requests.post(
            f"{API_URL}/documents",
            files={"file": (doc_file.name, f, "text/plain")}
        )
    
    if response.status_code == 200:
        doc_id = response.json()["id"]
        print(f"  ✓ Uploaded: {doc_id}")
    else:
        print(f"  ✗ Error: {response.text}")
    
    time.sleep(5)  # Wait for processing

print("\n✓ All documents uploaded!")
```

## ✅ Verification

Check if documents were processed:

```bash
# List documents
curl http://localhost:8000/documents

# Check details for each
curl http://localhost:8000/documents/{document_id}
```

Each document should have:
- `chunks` > 0 (number of chunks)
- `embeddings` > 0 (generated embeddings)

Example chunk counts (with chunk_size=1000, overlap=150):
- SmartHome_Manual.txt: ~45-55 chunks
- Invoice_FV_2025_0847.txt: ~8-12 chunks  
- Contract_SVC_0089.txt: ~20-25 chunks

## 🧪 Test Single Query

Test if RAG is working:

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the invoice number?",
    "top_k": 5
  }'
```

Should return:
```json
{
  "answer": "The invoice number is FV/2025/01/0847.",
  "citations": [
    {
      "document_id": "...",
      "document_title": "Invoice_FV_2025_0847.txt",
      "page_number": 1,
      "chunk_id": 3,
      "quote": "FAKTURA VAT / INVOICE Nr / No: FV/2025/01/0847"
    }
  ],
  "has_sufficient_context": true
}
```

## 📊 Run Full Evaluation

After loading all documents:

```bash
# Run 30 questions
python eval/run_evaluation.py

# Check results
python eval/analyze_results.py
```

## 🔧 Troubleshooting

### Documents not processing
- Check API logs (`docker-compose logs app`)
- Check if sentence-transformers was downloaded
- Check database connection

### No embeddings
- Check `EMBEDDING_TYPE` variable in API logs
- If using local - verify sentence-transformers installation
- If OpenAI - check `OPENAI_API_KEY`

### Query returns no results
- Check if embeddings were generated: `GET /documents/{id}`
- Check if pgvector is working: `docker-compose ps`
- Increase `top_k` to 10-20

## 📝 Adding Custom Documents

You can add your own .txt files to `sample_docs/`:

1. Create a text file with content
2. Upload via API
3. Add questions to `eval/questions.jsonl`:
   ```json
   {"id":"q31","question":"...","expected":"...","must_cite":true,"category":"answerable","document":"your_doc"}
   ```
4. Re-run evaluation

## 🎯 Next Steps

After loading sample docs and running evaluation:

1. **Manual scoring** - Edit `eval/evaluation_results.json`
2. **Analyze results** - `python eval/analyze_results.py`
3. **Iterate** - Adjust chunking, prompts, or top_k
4. **Re-evaluate** - Run again and compare results
