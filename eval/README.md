# System Ewaluacji RAG z Cytowaniami

System do manualnej oceny jakości odpowiedzi RAG z cytowaniami.

## 📋 Struktura

```
eval/
├── questions.jsonl           # 30 pytań testowych
├── scoring.py               # System scoringu i modele Pydantic
├── run_evaluation.py        # Uruchomienie ewaluacji (zapytania API)
├── analyze_results.py       # Analiza wyników
└── evaluation_results.json  # Wyniki (generowane)
```

## 🎯 System Scoringu

Każde pytanie oceniane jest w 3 kategoriach (0-2 punkty każda):

### 1. **Correctness (Poprawność)** - 0-2 punkty
- **0** = Błędna odpowiedź lub halucynacja
- **1** = Częściowo poprawna
- **2** = Poprawna odpowiedź

### 2. **Grounding/Citations (Cytowania)** - 0-2 punkty
- **0** = Brak cytowań lub cytowania nietrafione
- **1** = Są cytowania, ale słabe/nieprecyzyjne
- **2** = Cytowania trafne i wspierają odpowiedź

### 3. **Completeness (Kompletność)** - 0-2 punkty
- **0** = Pomija kluczowe elementy
- **1** = Zawiera większość informacji
- **2** = Kompletna odpowiedź

**Maksymalny wynik:**
- Na pytanie: 6 punktów
- Łącznie (30 pytań): 180 punktów

## 🚀 Użycie

### Krok 1: Przygotowanie

Upewnij się, że:
1. API działa (`http://localhost:8000`)
2. Dokumenty są załadowane i przetworzone
3. Endpoint `/answer` jest dostępny

### Krok 2: Uruchomienie Ewaluacji

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

Każda linia w `questions.jsonl` to JSON z pytaniem:

```json
{
  "id": "q01",
  "question": "Jaki jest cel projektu?",
  "expected": "Oczekiwana odpowiedź lub kluczowe elementy",
  "must_cite": true
}
```

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
