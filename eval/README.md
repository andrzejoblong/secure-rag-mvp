# System Ewaluacji RAG z Cytowaniami

System do manualnej oceny jakości odpowiedzi RAG z cytowaniami **oparty o rzeczywistą treść dokumentów**.

## 📋 Struktura

```
eval/
├── questions.jsonl           # 30 pytań testowych o TREŚĆ dokumentów
├── questions_meta.jsonl      # Backup: pytania meta o system (nieużywane)
├── scoring.py               # System scoringu i modele Pydantic
├── run_evaluation.py        # Uruchomienie ewaluacji (zapytania API)
├── analyze_results.py       # Analiza wyników
└── evaluation_results.json  # Wyniki (generowane)

sample_docs/
├── SmartHome_Manual.txt     # Instrukcja obsługi (10 pytań)
├── Invoice_FV_2025_0847.txt # Faktura VAT (10 pytań)
├── Contract_SVC_0089.txt    # Umowa zlecenia (10 pytań)
└── SETUP.md                 # Instrukcje załadowania dokumentów
```

## 🎯 Koncepcja Ewaluacji

### ⚠️ WAŻNE: Pytania o TREŚĆ dokumentów, nie o system!

Ewaluacja RAG testuje czy:
1. ✅ System **znajduje właściwe fragmenty** w dokumentach (retrieval)
2. ✅ Odpowiedź jest **uziemiona w treści** (grounded)
3. ✅ Cytowania wskazują **konkretne miejsca** (document_id, page, chunk_id, quote)
4. ✅ Model **nie halucynuje** gdy brak odpowiedzi w dokumencie

### 📚 Sample Documents

System zawiera 3 przykładowe dokumenty:

**1. SmartHome_Manual.txt** (10 pytań: 7 answerable + 2 multi-hop + 1 unanswerable)
- Instrukcja obsługi systemu automatyki domowej
- Pytania o: wymagania, instalację, konfigurację, tryby pracy, troubleshooting

**2. Invoice_FV_2025_0847.txt** (10 pytań: 8 answerable + 1 multi-hop + 1 unanswerable)
- Faktura VAT za sprzęt IT
- Pytania o: numery, kwoty, terminy, pozycje, usługi, gwarancję

**3. Contract_SVC_0089.txt** (10 pytań: 7 answerable + 2 multi-hop + 1 unanswerable)
- Umowa zlecenia na projekt IT
- Pytania o: wynagrodzenie, terminy, milestone'y, kary umowne, gwarancję

### 📊 Mix pytań (30 total):
- **24 answerable** - odpowiedź jest w PDF, da się wskazać stronę i cytat
- **4 multi-hop** - odpowiedź wymaga 2+ fragmentów z różnych miejsc
- **2 unanswerable** - kontrola negatywna, brak odpowiedzi w dokumencie

## 🎯 System Scoringu

Każde pytanie oceniane jest w 3 kategoriach (0-2 punkty każda):

### 1. **Correctness** - 0-2 points
- **0** = Incorrect answer or hallucination
- **1** = Partially correct
- **2** = Correct answer

### 2. **Grounding/Citations** - 0-2 points
- **0** = No citations or irrelevant citations
- **1** = Citations present but weak/imprecise
- **2** = Citations accurate and support the answer

### 3. **Completeness** - 0-2 points
- **0** = Missing key elements
- **1** = Contains most information
- **2** = Complete answer

**Maximum score:**
- Per question: 6 points
- Total (30 questions): 180 points

## 🚀 Użycie

### ⚠️ Krok 0: Załaduj Sample Documents (WYMAGANE!)

Przed uruchomieniem ewaluacji **musisz** załadować 3 sample dokumenty:

```bash
# Przejdź do instrukcji
cat sample_docs/SETUP.md

# Szybkie załadowanie wszystkich
for file in sample_docs/*.txt; do
  echo "Uploading $file..."
  curl -X POST http://localhost:8000/documents -F "file=@$file"
  sleep 5
done

# Weryfikacja
curl http://localhost:8000/documents
```

Zobacz szczegóły w `sample_docs/SETUP.md`.

### Krok 1: Uruchomienie Ewaluacji

### Krok 1: Uruchomienie Ewaluacji

Upewnij się, że:
1. ✅ API działa (`http://localhost:8000`)
2. ✅ **3 sample dokumenty są załadowane** (zobacz Krok 0)
3. ✅ Embeddingi zostały wygenerowane (sprawdź `GET /documents/{id}`)
4. ✅ Endpoint `/answer` jest dostępny

### Krok 2: Uruchom zapytania

```bash
# Uruchom zapytania dla wszystkich 30 pytań
python eval/run_evaluation.py

# Opcjonalnie: użyj innego URL lub top_k
python eval/run_evaluation.py --api-url http://localhost:8000 --top-k 10
```

To wygeneruje plik `eval/evaluation_results.json` z odpowiedziami systemu.

### Krok 3: Manualne Scorowanie

Otwórz `eval/evaluation_results.json` i dla każdego pytania dodaj:

```json
{
  "question_id": "q01",
  "question": "Jaki jest cel projektu?",
  "expected": "...",
  "answer": "...",
  "citations": [...],
  "has_sufficient_context": true,
  
  "correctness": 2,        // ← Dodaj ocenę 0-2
  "citation_quality": 2,   // ← Dodaj ocenę 0-2
  "completeness": 2,       // ← Dodaj ocenę 0-2
  "notes": "Doskonała odpowiedź z trafnymi cytowaniami"  // ← Opcjonalne
}
```

### Krok 4: Analiza Wyników

```bash
# Pokaż podsumowanie
python eval/analyze_results.py

# Pokaż szczegóły konkretnego pytania
python eval/analyze_results.py --question q01

# Pokaż guide scoringu
python eval/analyze_results.py --guide
```

## 📊 Przykładowe Wyniki

```
==============================================================
EVALUATION SUMMARY
==============================================================
Total Questions: 30
Completed Evaluations: 30
Total Score: 156 / 180
Percentage: 86.67%

--------------------------------------------------------------
AVERAGE SCORES (out of 2):
  Correctness:      1.80
  Citation Quality: 1.73
  Completeness:     1.67

--------------------------------------------------------------
SCORE DISTRIBUTION:

Correctness:
  0 (Incorrect):     2
  1 (Partial):       4
  2 (Correct):       24

Citation Quality:
  0 (No/Bad):        3
  1 (Weak):          5
  2 (Strong):        22

Completeness:
  0 (Incomplete):    1
  1 (Mostly):        9
  2 (Complete):      20
==============================================================
```

## 📝 Format Pytań (questions.jsonl)

Każda linia w `questions.jsonl` to JSON z pytaniem **o treść dokumentu**:

```json
{
  "id": "q01",
  "question": "Jaki jest numer faktury?",
  "expected": "FV/2025/01/0847",
  "must_cite": true,
  "category": "answerable",
  "document": "invoice"
}
```

### Kategorie pytań:

- **answerable** (24 pytania) - odpowiedź jest w dokumencie, można podać cytat
- **multi-hop** (4 pytania) - wymaga zebrania info z 2+ chunków
- **unanswerable** (2 pytania) - brak odpowiedzi, test czy model nie halucynuje

### Scorowanie dla pytań unanswerable:

Dla pytań typu "unanswerable" (gdy **brak odpowiedzi w dokumencie**):

- **correctness = 2** tylko gdy model jasno mówi "Brak informacji w dokumentach" (bez zmyślania)
- **grounding = 2** gdy cytuje fragment "nie dotyczy" LUB poprawnie `citations=[]`
- **correctness = 0** jeśli model zmyśla odpowiedź z wiedzy ogólnej

To testuje czy RAG umie odmówić zamiast halucynować!

## 🔍 Co Oceniamy?

### Dobre odpowiedzi mają:
✅ Poprawne informacje z dokumentów  
✅ Precyzyjne cytowania (document, page, chunk, quote)  
✅ Kompletność (wszystkie kluczowe elementy)  
✅ Jasne wskazanie źródła dla każdego faktu  
✅ Przyznanie się do braku informacji gdy brak kontekstu  

### Złe odpowiedzi to:
❌ Halucynacje (informacje spoza dokumentów)  
❌ Brak cytowań  
❌ Cytowania nietrafione (nie wspierają odpowiedzi)  
❌ Niekompletne (brakuje kluczowych elementów)  
❌ Fałszywa pewność przy braku kontekstu  

## 🎓 Wskazówki dla Ewaluatorów

1. **Czytaj dokładnie:** Porównaj odpowiedź z `expected`
2. **Sprawdź cytowania:** Czy quotes rzeczywiście wspierają odpowiedź?
3. **Weryfikuj kontekst:** Czy `has_sufficient_context` jest prawidłowe?
4. **Bądź konsekwentny:** Używaj tej samej skali dla wszystkich pytań
5. **Dodawaj notatki:** Szczególnie dla edge cases

## 📈 Metryki Docelowe (MVP)

Dla systemu produkcyjnego:
- **Correctness:** > 1.5 średnia (75%)
- **Citations:** > 1.5 średnia (75%)
- **Completeness:** > 1.5 średnia (75%)
- **Overall:** > 135/180 (75%)

## 🔧 Troubleshooting

### Brak odpowiedzi dla pytań
- Sprawdź czy API działa: `curl http://localhost:8000/health`
- Sprawdź czy dokumenty są załadowane: `curl http://localhost:8000/documents`
- Sprawdź logi API

### Słabe cytowania
- Może być problem z chunk size (obecnie 1000)
- Może być problem z top_k (zwiększ do 10)
- Sprawdź jakość embeddingów

### Niski overall score
- Zidentyfikuj najczęstszy problem (correctness vs citations vs completeness)
- Przeanalizuj bottom 5 questions
- Dostosuj prompt lub parametry

## 📚 Pliki Wyjściowe

### evaluation_results.json
Pełne wyniki z:
- Wszystkimi pytaniami i odpowiedziami
- Cytowaniami
- Manualnymi scorami
- Notatkami

Format pozwala na:
- Łatwe przeglądanie w edytorze
- Dalszą analizę w Pythonie
- Eksport do innych formatów (CSV, Excel)

## 🚦 Next Steps

Po zakończeniu ewaluacji:

1. **Zidentyfikuj problemy:** Które kategorie są najsłabsze?
2. **Iteruj:** Popraw prompt, chunking, lub retrieval
3. **Re-evaluate:** Uruchom ponownie na tych samych pytaniach
4. **Track progress:** Porównaj wyniki między iteracjami

## 💡 Rozszerzenia (Future)

- Automatyczny scoring z GPT-4 jako judge
- Porównanie z baseline
- A/B testing różnych konfiguracji
- Tracking metryk w czasie
- Inter-rater reliability (wielu ewaluatorów)
