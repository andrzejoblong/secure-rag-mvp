#!/usr/bin/env python3
"""
Analyze evaluation results and display summary
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.scoring import load_evaluation, print_evaluation_summary, print_scoring_guide


def analyze_results(file_path: str = "eval/evaluation_results.json"):
    """
    Analyze and display evaluation results
    
    Args:
        file_path: Path to evaluation results JSON
    """
    results = load_evaluation(file_path)
    
    if not results:
        print(f"❌ No evaluation results found at: {file_path}")
        print(f"\n💡 Run evaluation first:")
        print(f"   python eval/run_evaluation.py")
        return
    
    print_evaluation_summary(results)
    
    # Show incomplete evaluations
    incomplete = [e for e in results.evaluations if not e.is_complete]
    if incomplete:
        print(f"⚠️  {len(incomplete)} evaluations still need scoring:")
        for e in incomplete[:5]:  # Show first 5
            print(f"   - {e.question_id}: {e.question[:50]}...")
        if len(incomplete) > 5:
            print(f"   ... and {len(incomplete) - 5} more")
    else:
        print("✅ All evaluations have been scored!")
    
    # Show top and bottom performers
    scored = [e for e in results.evaluations if e.is_complete]
    if scored:
        print("\n" + "="*60)
        print("TOP 5 BEST PERFORMING QUESTIONS:")
        print("="*60)
        top_5 = sorted(scored, key=lambda x: x.total_score, reverse=True)[:5]
        for i, e in enumerate(top_5, 1):
            print(f"\n{i}. {e.question_id} (Score: {e.total_score}/6)")
            print(f"   Q: {e.question[:60]}...")
            print(f"   Correctness: {e.correctness}, Citations: {e.citation_quality}, Completeness: {e.completeness}")
        
        print("\n" + "="*60)
        print("BOTTOM 5 WORST PERFORMING QUESTIONS:")
        print("="*60)
        bottom_5 = sorted(scored, key=lambda x: x.total_score)[:5]
        for i, e in enumerate(bottom_5, 1):
            print(f"\n{i}. {e.question_id} (Score: {e.total_score}/6)")
            print(f"   Q: {e.question[:60]}...")
            print(f"   Correctness: {e.correctness}, Citations: {e.citation_quality}, Completeness: {e.completeness}")
            if e.notes:
                print(f"   Notes: {e.notes}")
    
    print("\n" + "="*60)
    print("DETAILED RESULTS:")
    print("="*60)
    print(f"\nFull results saved in: {file_path}")
    print(f"To view individual answers, open the JSON file")


def show_question_detail(question_id: str, file_path: str = "eval/evaluation_results.json"):
    """Show detailed information for a specific question"""
    results = load_evaluation(file_path)
    
    if not results:
        print(f"❌ No evaluation results found")
        return
    
    # Find question
    evaluation = next((e for e in results.evaluations if e.question_id == question_id), None)
    
    if not evaluation:
        print(f"❌ Question {question_id} not found")
        return
    
    print("\n" + "="*60)
    print(f"QUESTION DETAIL: {evaluation.question_id}")
    print("="*60)
    print(f"\nQuestion: {evaluation.question}")
    print(f"\nExpected: {evaluation.expected}")
    print(f"\nAnswer:\n{evaluation.answer}")
    print(f"\nCitations ({len(evaluation.citations)}):")
    for i, citation in enumerate(evaluation.citations, 1):
        print(f"\n  [{i}] Document: {citation.get('document_title', 'N/A')}")
        print(f"      Page: {citation.get('page_number', 'N/A')}, Chunk: {citation.get('chunk_id', 'N/A')}")
        print(f"      Quote: {citation.get('quote', 'N/A')[:100]}...")
    
    print(f"\nContext Available: {'Yes' if evaluation.has_sufficient_context else 'No'}")
    
    if evaluation.is_complete:
        print(f"\nScores:")
        print(f"  Correctness:      {evaluation.correctness}/2")
        print(f"  Citation Quality: {evaluation.citation_quality}/2")
        print(f"  Completeness:     {evaluation.completeness}/2")
        print(f"  TOTAL:            {evaluation.total_score}/6")
        
        if evaluation.notes:
            print(f"\nNotes: {evaluation.notes}")
    else:
        print(f"\n⚠️  Not yet scored")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze RAG evaluation results")
    parser.add_argument(
        "--file",
        default="eval/evaluation_results.json",
        help="Path to evaluation results JSON"
    )
    parser.add_argument(
        "--question",
        help="Show details for specific question ID (e.g., q01)"
    )
    parser.add_argument(
        "--guide",
        action="store_true",
        help="Show scoring guide"
    )
    
    args = parser.parse_args()
    
    if args.guide:
        print_scoring_guide()
    elif args.question:
        show_question_detail(args.question, args.file)
    else:
        analyze_results(args.file)
