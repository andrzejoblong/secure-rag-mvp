"""
Manual Evaluation System for RAG with Citations

Scoring system (0-6 points per question):
- Correctness (0-2): Accuracy of the answer
- Grounding/Citations (0-2): Quality of citations
- Completeness (0-2): Answer completeness

Total: 30 questions × 6 points = 180 points max
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum
import json
from pathlib import Path


class CorrectnessScore(Enum):
    """Correctness scoring"""
    INCORRECT = 0  # Błędna / halucynacja
    PARTIAL = 1    # Częściowo poprawna
    CORRECT = 2    # Poprawna


class CitationScore(Enum):
    """Citation quality scoring"""
    NO_CITATIONS = 0      # Brak cytowań lub nietrafione
    WEAK_CITATIONS = 1    # Są cytowania, ale słabe
    STRONG_CITATIONS = 2  # Cytowania trafne, wspierają odpowiedź


class CompletenessScore(Enum):
    """Answer completeness scoring"""
    INCOMPLETE = 0  # Pomija kluczowe elementy
    MOSTLY = 1      # Większość jest
    COMPLETE = 2    # Kompletna


class QuestionEvaluation(BaseModel):
    """Single question evaluation"""
    question_id: str
    question: str
    expected: str
    answer: str
    citations: List[Dict]
    has_sufficient_context: bool
    
    # Manual scores
    correctness: Optional[int] = Field(None, ge=0, le=2, description="Correctness score (0-2)")
    citation_quality: Optional[int] = Field(None, ge=0, le=2, description="Citation quality score (0-2)")
    completeness: Optional[int] = Field(None, ge=0, le=2, description="Completeness score (0-2)")
    
    # Optional notes
    notes: Optional[str] = Field(None, description="Evaluator notes")
    
    @property
    def total_score(self) -> Optional[int]:
        """Calculate total score"""
        if all(s is not None for s in [self.correctness, self.citation_quality, self.completeness]):
            return self.correctness + self.citation_quality + self.completeness
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if evaluation is complete"""
        return all(s is not None for s in [self.correctness, self.citation_quality, self.completeness])


class EvaluationResults(BaseModel):
    """Complete evaluation results"""
    evaluations: List[QuestionEvaluation]
    
    @property
    def completed_count(self) -> int:
        """Number of completed evaluations"""
        return sum(1 for e in self.evaluations if e.is_complete)
    
    @property
    def total_questions(self) -> int:
        """Total number of questions"""
        return len(self.evaluations)
    
    @property
    def total_score(self) -> int:
        """Total score across all completed evaluations"""
        return sum(e.total_score for e in self.evaluations if e.total_score is not None)
    
    @property
    def max_possible_score(self) -> int:
        """Maximum possible score"""
        return self.completed_count * 6
    
    @property
    def percentage(self) -> Optional[float]:
        """Percentage score"""
        if self.max_possible_score > 0:
            return (self.total_score / self.max_possible_score) * 100
        return None
    
    @property
    def avg_correctness(self) -> Optional[float]:
        """Average correctness score"""
        scores = [e.correctness for e in self.evaluations if e.correctness is not None]
        return sum(scores) / len(scores) if scores else None
    
    @property
    def avg_citation_quality(self) -> Optional[float]:
        """Average citation quality score"""
        scores = [e.citation_quality for e in self.evaluations if e.citation_quality is not None]
        return sum(scores) / len(scores) if scores else None
    
    @property
    def avg_completeness(self) -> Optional[float]:
        """Average completeness score"""
        scores = [e.completeness for e in self.evaluations if e.completeness is not None]
        return sum(scores) / len(scores) if scores else None
    
    def get_summary(self) -> Dict:
        """Get evaluation summary"""
        return {
            "total_questions": self.total_questions,
            "completed_evaluations": self.completed_count,
            "total_score": self.total_score,
            "max_possible_score": self.max_possible_score,
            "percentage": round(self.percentage, 2) if self.percentage else None,
            "averages": {
                "correctness": round(self.avg_correctness, 2) if self.avg_correctness else None,
                "citation_quality": round(self.avg_citation_quality, 2) if self.avg_citation_quality else None,
                "completeness": round(self.avg_completeness, 2) if self.avg_completeness else None,
            },
            "breakdown": self._get_score_breakdown()
        }
    
    def _get_score_breakdown(self) -> Dict:
        """Get detailed score breakdown"""
        breakdown = {
            "correctness": {"0": 0, "1": 0, "2": 0},
            "citation_quality": {"0": 0, "1": 0, "2": 0},
            "completeness": {"0": 0, "1": 0, "2": 0}
        }
        
        for e in self.evaluations:
            if e.correctness is not None:
                breakdown["correctness"][str(e.correctness)] += 1
            if e.citation_quality is not None:
                breakdown["citation_quality"][str(e.citation_quality)] += 1
            if e.completeness is not None:
                breakdown["completeness"][str(e.completeness)] += 1
        
        return breakdown


def load_questions(file_path: str = "eval/questions.jsonl") -> List[Dict]:
    """Load questions from JSONL file"""
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            questions.append(json.loads(line.strip()))
    return questions


def save_evaluation(results: EvaluationResults, file_path: str = "eval/evaluation_results.json"):
    """Save evaluation results to JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results.model_dump(), f, indent=2, ensure_ascii=False)


def load_evaluation(file_path: str = "eval/evaluation_results.json") -> Optional[EvaluationResults]:
    """Load evaluation results from JSON"""
    path = Path(file_path)
    if not path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return EvaluationResults(**data)


def print_evaluation_summary(results: EvaluationResults):
    """Print formatted evaluation summary"""
    summary = results.get_summary()
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Total Questions: {summary['total_questions']}")
    print(f"Completed Evaluations: {summary['completed_evaluations']}")
    print(f"Total Score: {summary['total_score']} / {summary['max_possible_score']}")
    print(f"Percentage: {summary['percentage']}%" if summary['percentage'] else "Percentage: N/A")
    print("\n" + "-"*60)
    print("AVERAGE SCORES (out of 2):")
    print(f"  Correctness:      {summary['averages']['correctness']:.2f}" if summary['averages']['correctness'] else "  Correctness:      N/A")
    print(f"  Citation Quality: {summary['averages']['citation_quality']:.2f}" if summary['averages']['citation_quality'] else "  Citation Quality: N/A")
    print(f"  Completeness:     {summary['averages']['completeness']:.2f}" if summary['averages']['completeness'] else "  Completeness:     N/A")
    
    print("\n" + "-"*60)
    print("SCORE DISTRIBUTION:")
    breakdown = summary['breakdown']
    
    print("\nCorrectness:")
    print(f"  0 (Incorrect):     {breakdown['correctness']['0']}")
    print(f"  1 (Partial):       {breakdown['correctness']['1']}")
    print(f"  2 (Correct):       {breakdown['correctness']['2']}")
    
    print("\nCitation Quality:")
    print(f"  0 (No/Bad):        {breakdown['citation_quality']['0']}")
    print(f"  1 (Weak):          {breakdown['citation_quality']['1']}")
    print(f"  2 (Strong):        {breakdown['citation_quality']['2']}")
    
    print("\nCompleteness:")
    print(f"  0 (Incomplete):    {breakdown['completeness']['0']}")
    print(f"  1 (Mostly):        {breakdown['completeness']['1']}")
    print(f"  2 (Complete):      {breakdown['completeness']['2']}")
    print("="*60 + "\n")


def print_scoring_guide():
    """Print scoring guide for evaluators"""
    print("\n" + "="*60)
    print("SCORING GUIDE")
    print("="*60)
    print("\n1. CORRECTNESS (0-2 points):")
    print("   0 = Błędna odpowiedź lub halucynacja")
    print("   1 = Częściowo poprawna")
    print("   2 = Poprawna odpowiedź")
    
    print("\n2. GROUNDING/CITATIONS (0-2 points):")
    print("   0 = Brak cytowań lub cytowania nietrafione")
    print("   1 = Są cytowania, ale słabe/nieprecyzyjne")
    print("   2 = Cytowania trafne i wspierają odpowiedź")
    
    print("\n3. COMPLETENESS (0-2 points):")
    print("   0 = Pomija kluczowe elementy")
    print("   1 = Zawiera większość informacji")
    print("   2 = Kompletna odpowiedź")
    
    print("\nMAX SCORE PER QUESTION: 6 points")
    print("MAX TOTAL SCORE (30 questions): 180 points")
    print("="*60 + "\n")
