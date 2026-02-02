# Setup Sample Documents

Ten przewodnik opisuje jak załadować przykładowe dokumenty do systemu RAG przed uruchomieniem ewaluacji.

## 📁 Sample Documents

System zawiera 3 przykładowe dokumenty testowe:

1. **SmartHome_Manual.txt** - Instrukcja obsługi systemu Smart Home Pro v2.1
   - 10 sekcji technicznych
   - Wymagania, instalacja, konfiguracja, rozwiązywanie problemów
   - ~7000 słów

2. **Invoice_FV_2025_0847.txt** - Faktura VAT
   - 10 pozycji (laptopy, monitory, akcesoria IT)
   - Szczegóły finansowe, terminy płatności
   - ~1500 słów

3. **Contract_SVC_0089.txt** - Umowa zlecenia na projekt IT
   - 10 paragrafów: zakres, terminy, wynagrodzenie, gwarancja
   - Kamienie milowe, kary umowne, prawa autorskie
   - ~3500 słów

## 🚀 Jak załadować dokumenty

### Opcja A: Przez API (zalecane)

```bash
# Upewnij się że API działa
curl http://localhost:8000/health

# Załaduj wszystkie 3 dokumenty
for file in sample_docs/*.txt; do
  echo "Uploading $file..."
  curl -X POST http://localhost:8000/documents \
    -F "file=@$file"
  echo ""
  sleep 5  # Poczekaj na przetworzenie
done
```

### Opcja B: Przez Swagger UI

1. Otwórz http://localhost:8000/docs
2. Endpoint `POST /documents`
3. Kliknij "Try it out"
4. Upload każdego pliku z `sample_docs/`
5. Poczekaj aż processing się zakończy (check logs)

### Opcja C: Skrypt Python

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

## ✅ Weryfikacja

Sprawdź czy dokumenty zostały przetworzone:

```bash
# Lista dokumentów
curl http://localhost:8000/documents

# Sprawdź szczegóły każdego
curl http://localhost:8000/documents/{document_id}
```

Każdy dokument powinien mieć:
- `chunks` > 0 (liczba chunków)
- `embeddings` > 0 (wygenerowane embeddingi)

Przykładowe liczby chunków (z chunk_size=1000, overlap=150):
- SmartHome_Manual.txt: ~45-55 chunków
- Invoice_FV_2025_0847.txt: ~8-12 chunków  
- Contract_SVC_0089.txt: ~20-25 chunków

## 🧪 Test pojedynczego zapytania

Przetestuj czy RAG działa:

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Jaki jest numer faktury?",
    "top_k": 5
  }'
```

Powinno zwrócić:
```json
{
  "answer": "Numer faktury to FV/2025/01/0847.",
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

## 📊 Uruchomienie pełnej ewaluacji

Po załadowaniu wszystkich dokumentów:

```bash
# Uruchom 30 pytań
python eval/run_evaluation.py

# Sprawdź wyniki
python eval/analyze_results.py
```

## 🔧 Troubleshooting

### Dokumenty się nie przetwarzają
- Sprawdź logi API (`docker-compose logs app`)
- Sprawdź czy sentence-transformers został pobrany
- Sprawdź połączenie z bazą danych

### Brak embeddingów
- Sprawdź zmienną `EMBEDDING_TYPE` w logach API
- Jeśli używasz local - zweryfikuj instalację sentence-transformers
- Jeśli OpenAI - sprawdź `OPENAI_API_KEY`

### Query nie zwraca wyników
- Sprawdź czy embeddingi zostały wygenerowane: `GET /documents/{id}`
- Sprawdź czy pgvector działa: `docker-compose ps`
- Zwiększ `top_k` do 10-20

## 📝 Dodawanie własnych dokumentów

Możesz dodać własne pliki .txt do `sample_docs/`:

1. Stwórz plik tekstowy z treścią
2. Upload przez API
3. Dodaj pytania do `eval/questions.jsonl`:
   ```json
   {"id":"q31","question":"...","expected":"...","must_cite":true,"category":"answerable","document":"your_doc"}
   ```
4. Uruchom ponownie ewaluację

## 🎯 Co dalej?

Po załadowaniu sample docs i uruchomieniu ewaluacji:

1. **Manualne scorowanie** - Edytuj `eval/evaluation_results.json`
2. **Analiza wyników** - `python eval/analyze_results.py`
3. **Iteracja** - Dostosuj chunking, prompts, lub top_k
4. **Re-evaluate** - Uruchom ponownie i porównaj wyniki
