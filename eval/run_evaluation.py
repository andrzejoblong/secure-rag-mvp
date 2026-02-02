#!/usr/bin/env python3
"""
Run evaluation: query all questions and save results for manual scoring
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.scoring import (
    load_questions,
    QuestionEvaluation,
    EvaluationResults,
    save_evaluation,
    print_scoring_guide
)


def run_evaluation(api_url: str = "http://localhost:8000", top_k: int = 5):
    """
    Run evaluation by querying all questions
    
    Args:
        api_url: Base URL of the API
        top_k: Number of chunks to retrieve
    """
    print(f"\n🚀 Starting evaluation against {api_url}")
    print(f"   Using top_k={top_k}")
    
    # Load questions
    questions = load_questions("eval/questions.jsonl")
    print(f"\n✓ Loaded {len(questions)} questions")
    
    # Query each question
    evaluations = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Processing: {q['id']}")
        print(f"   Q: {q['question'][:60]}...")
        
        try:
            # Call /answer endpoint
            response = requests.post(
                f"{api_url}/answer",
                json={
                    "question": q["question"],
                    "top_k": top_k
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Got answer ({len(data.get('answer', ''))} chars, {len(data.get('citations', []))} citations)")
                
                evaluation = QuestionEvaluation(
                    question_id=q["id"],
                    question=q["question"],
                    expected=q["expected"],
                    answer=data.get("answer", ""),
                    citations=data.get("citations", []),
                    has_sufficient_context=data.get("has_sufficient_context", False)
                )
                evaluations.append(evaluation)
            else:
                print(f"   ✗ API error: {response.status_code}")
                print(f"   {response.text}")
                
                # Add empty evaluation
                evaluation = QuestionEvaluation(
                    question_id=q["id"],
                    question=q["question"],
                    expected=q["expected"],
                    answer=f"[ERROR {response.status_code}]: {response.text[:100]}",
                    citations=[],
                    has_sufficient_context=False
                )
                evaluations.append(evaluation)
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            
            # Add error evaluation
            evaluation = QuestionEvaluation(
                question_id=q["id"],
                question=q["question"],
                expected=q["expected"],
                answer=f"[EXCEPTION]: {str(e)}",
                citations=[],
                has_sufficient_context=False
            )
            evaluations.append(evaluation)
    
    # Save results
    results = EvaluationResults(evaluations=evaluations)
    output_file = "eval/evaluation_results.json"
    save_evaluation(results, output_file)
    
    print(f"\n✓ Evaluation complete!")
    print(f"✓ Results saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total questions: {len(evaluations)}")
    print(f"   Successful queries: {sum(1 for e in evaluations if not e.answer.startswith('[ERROR'))}")
    print(f"   With context: {sum(1 for e in evaluations if e.has_sufficient_context)}")
    print(f"   With citations: {sum(1 for e in evaluations if e.citations)}")
    
    print(f"\n📝 Next step: Manual scoring")
    print(f"   Edit {output_file} and add scores:")
    print(f"   - correctness: 0-2")
    print(f"   - citation_quality: 0-2")
    print(f"   - completeness: 0-2")
    print(f"   - notes: (optional)")
    
    print_scoring_guide()
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG evaluation")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)"
    )
    
    args = parser.parse_args()
    
    run_evaluation(api_url=args.api_url, top_k=args.top_k)
