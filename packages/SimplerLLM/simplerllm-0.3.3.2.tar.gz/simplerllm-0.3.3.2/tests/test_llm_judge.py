"""
Test script for LLMJudge functionality.

This script demonstrates all three modes of LLMJudge:
1. select_best - Pick the best answer from multiple providers
2. synthesize - Combine all answers into improved response
3. compare - Detailed comparative analysis

Usage:
    python tests/test_llm_judge.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SimplerLLM.language import LLM, LLMProvider, LLMJudge, JudgeMode


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def print_result(result):
    """Print judge result in a formatted way."""
    print(f"\nMode: {result.mode.value}")
    print(f"Criteria: {', '.join(result.criteria_used)}")
    print(f"Total Execution Time: {result.total_execution_time:.2f}s\n")

    # Print all provider responses
    print("PROVIDER RESPONSES:")
    print("-" * 80)
    for response in result.all_responses:
        print(f"\n{response.provider_name} ({response.model_name}) - {response.execution_time:.2f}s:")
        print(response.response_text[:200] + "..." if len(response.response_text) > 200 else response.response_text)

    # Print evaluations
    print("\n\nEVALUATIONS:")
    print("-" * 80)
    for eval in result.evaluations:
        print(f"\nRank #{eval.rank}: {eval.provider_name}")
        print(f"Overall Score: {eval.overall_score}/10")
        print(f"Confidence: {result.confidence_scores[eval.provider_name]:.2f}")
        print(f"Criterion Scores: {eval.criterion_scores}")
        print(f"Reasoning: {eval.reasoning[:150]}...")

    # Print final answer
    print("\n\nFINAL ANSWER:")
    print("-" * 80)
    print(result.final_answer)

    # Print judge reasoning
    print("\n\nJUDGE'S REASONING:")
    print("-" * 80)
    print(result.judge_reasoning)


def test_select_best_mode():
    """Test select_best mode - picks the best answer."""
    print_separator("TEST 1: SELECT BEST MODE")

    # Create providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Create judge (using a stronger model)
    judge_llm = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-sonnet-20241022")

    # Initialize LLMJudge
    judge = LLMJudge(
        providers=providers,
        judge_llm=judge_llm,
        parallel=True,
        verbose=True
    )

    # Test prompt
    prompt = "Explain what machine learning is in 2-3 sentences."

    # Generate with select_best mode
    result = judge.generate(
        prompt=prompt,
        mode="select_best",
        criteria=["accuracy", "clarity", "conciseness"]
    )

    print_result(result)


def test_synthesize_mode():
    """Test synthesize mode - combines all answers."""
    print_separator("TEST 2: SYNTHESIZE MODE")

    # Create providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Create judge
    judge_llm = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-sonnet-20241022")

    # Initialize LLMJudge
    judge = LLMJudge(
        providers=providers,
        judge_llm=judge_llm,
        parallel=True,
        verbose=True
    )

    # Test prompt
    prompt = "What are the benefits of using Python for data science?"

    # Generate with synthesize mode
    result = judge.generate(
        prompt=prompt,
        mode="synthesize",
        criteria=["completeness", "accuracy", "clarity"]
    )

    print_result(result)


def test_compare_mode():
    """Test compare mode - detailed comparative analysis."""
    print_separator("TEST 3: COMPARE MODE")

    # Create providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Create judge
    judge_llm = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-sonnet-20241022")

    # Initialize LLMJudge
    judge = LLMJudge(
        providers=providers,
        judge_llm=judge_llm,
        parallel=True,
        verbose=True
    )

    # Test prompt
    prompt = "Explain the difference between supervised and unsupervised learning."

    # Generate with compare mode
    result = judge.generate(
        prompt=prompt,
        mode="compare",
        criteria=["accuracy", "clarity", "depth"]
    )

    print_result(result)


def test_router_summary():
    """Test router summary generation."""
    print_separator("TEST 4: ROUTER SUMMARY GENERATION")

    # Create providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Create judge
    judge_llm = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-sonnet-20241022")

    # Initialize LLMJudge
    judge = LLMJudge(
        providers=providers,
        judge_llm=judge_llm,
        parallel=True,
        verbose=True
    )

    # Test prompt (coding question)
    prompt = "Write a Python function to reverse a string."

    # Generate with router summary
    result = judge.generate(
        prompt=prompt,
        mode="select_best",
        generate_summary=True
    )

    print_result(result)

    # Access router summary
    if hasattr(judge, '_router_summary'):
        print("\n\nROUTER SUMMARY:")
        print("-" * 80)
        summary = judge._router_summary
        print(f"Query Type: {summary.query_type}")
        print(f"Winning Provider: {summary.winning_provider}")
        print(f"Provider Scores: {summary.provider_scores}")
        print(f"Recommendation: {summary.recommendation}")
        print(f"Criteria Winners: {summary.criteria_winners}")


def test_batch_evaluation():
    """Test batch evaluation and report generation."""
    print_separator("TEST 5: BATCH EVALUATION & REPORTING")

    # Create providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Create judge
    judge_llm = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-sonnet-20241022")

    # Initialize LLMJudge
    judge = LLMJudge(
        providers=providers,
        judge_llm=judge_llm,
        parallel=True,
        verbose=True
    )

    # Multiple test prompts
    prompts = [
        "What is artificial intelligence?",
        "Explain neural networks in simple terms.",
        "What are the applications of AI in healthcare?",
    ]

    print(f"Evaluating {len(prompts)} prompts in batch...\n")

    # Batch evaluation
    results = judge.evaluate_batch(prompts, mode="compare")

    print(f"\nCompleted {len(results)} evaluations\n")

    # Generate report
    report = judge.generate_evaluation_report(results, export_format="json")

    print("\nEVALUATION REPORT:")
    print("-" * 80)
    print(f"Total Queries: {report.total_queries}")
    print(f"Provider Win Counts: {report.provider_win_counts}")
    print(f"Average Scores: {report.average_scores}")
    print(f"Best Provider Overall: {report.best_provider_overall}")
    print(f"Best Provider by Criteria: {report.best_provider_by_criteria}")
    print(f"\nReport exported to JSON file.")


def main():
    """Run all tests."""
    print("\n" + "#"*80)
    print("#  LLMJudge Comprehensive Test Suite")
    print("#"*80)

    try:
        # Test 1: Select Best Mode
        test_select_best_mode()

        # Test 2: Synthesize Mode
        test_synthesize_mode()

        # Test 3: Compare Mode
        test_compare_mode()

        # Test 4: Router Summary
        test_router_summary()

        # Test 5: Batch Evaluation
        test_batch_evaluation()

        print_separator("ALL TESTS COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
