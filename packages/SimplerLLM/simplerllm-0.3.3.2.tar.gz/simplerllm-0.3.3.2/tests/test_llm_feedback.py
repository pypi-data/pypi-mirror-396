"""
Test script for LLMFeedbackLoop functionality.

This script demonstrates all three architectural patterns:
1. Single provider self-critique
2. Dual provider (generator + critic)
3. Multi-provider rotation

Usage:
    python tests/test_llm_feedback.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SimplerLLM.language import LLM, LLMProvider, LLMFeedbackLoop


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def print_result(result):
    """Print feedback result in a formatted way."""
    print(f"\nArchitecture: {result.architecture_used}")
    print(f"Total Iterations: {result.total_iterations}")
    print(f"Stopped Reason: {result.stopped_reason}")
    print(f"Score Improvement: {result.initial_score:.1f} → {result.final_score:.1f}")
    print(f"Total Execution Time: {result.total_execution_time:.2f}s\n")

    # Print improvement trajectory
    print("IMPROVEMENT TRAJECTORY:")
    print("-" * 80)
    for idx, score in enumerate(result.improvement_trajectory, 1):
        bar = "█" * int(score)
        print(f"Iteration {idx}: {score:.1f}/10 {bar}")

    # Print detailed iteration history
    print("\n\nITERATION HISTORY:")
    print("-" * 80)
    for iteration in result.all_iterations:
        print(f"\nIteration {iteration.iteration_number}:")
        print(f"  Provider: {iteration.provider_used} ({iteration.model_used})")
        print(f"  Temperature: {iteration.temperature_used:.2f}")
        print(f"  Quality Score: {iteration.critique.quality_score}/10")

        if iteration.improvement_from_previous is not None:
            print(f"  Improvement: +{iteration.improvement_from_previous:.1%}")

        print(f"  Strengths: {', '.join(iteration.critique.strengths[:2]) if iteration.critique.strengths else 'None'}")
        print(f"  Weaknesses: {', '.join(iteration.critique.weaknesses[:2]) if iteration.critique.weaknesses else 'None'}")
        print(f"  Answer preview: {iteration.answer[:100]}...")

    # Print final answer
    print("\n\nFINAL ANSWER:")
    print("-" * 80)
    print(result.final_answer)


def test_single_provider():
    """Test single provider self-critique pattern."""
    print_separator("TEST 1: SINGLE PROVIDER SELF-CRITIQUE")

    # Create single LLM
    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    # Initialize feedback loop
    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=3,
        convergence_threshold=0.1,
        verbose=True
    )

    # Test prompt
    prompt = "Explain what recursion is in programming in 2-3 sentences."

    print(f"Prompt: {prompt}\n")

    # Run improvement loop
    result = feedback.improve(
        prompt=prompt,
        focus_on=["clarity", "conciseness", "accuracy"]
    )

    print_result(result)


def test_dual_provider():
    """Test dual provider (generator + critic) pattern."""
    print_separator("TEST 2: DUAL PROVIDER (GENERATOR + CRITIC)")

    # Create generator and critic
    generator = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")
    critic = LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022")

    # Initialize feedback loop
    feedback = LLMFeedbackLoop(
        generator_llm=generator,
        critic_llm=critic,
        max_iterations=4,
        quality_threshold=8.5,  # Stop when score reaches 8.5
        verbose=True
    )

    # Test prompt
    prompt = "What is the difference between a list and a tuple in Python?"

    print(f"Prompt: {prompt}\n")

    # Run improvement loop
    result = feedback.improve(
        prompt=prompt,
        focus_on=["accuracy", "clarity", "examples"]
    )

    print_result(result)


def test_multi_provider_rotation():
    """Test multi-provider rotation pattern."""
    print_separator("TEST 3: MULTI-PROVIDER ROTATION")

    # Create multiple providers
    providers = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Initialize feedback loop
    feedback = LLMFeedbackLoop(
        providers=providers,
        max_iterations=3,
        check_convergence=True,
        verbose=True
    )

    # Test prompt
    prompt = "Explain the concept of object-oriented programming."

    print(f"Prompt: {prompt}\n")

    # Run improvement loop
    result = feedback.improve(
        prompt=prompt,
        focus_on=["completeness", "clarity", "examples"]
    )

    print_result(result)


def test_temperature_scheduling():
    """Test temperature scheduling (decreasing)."""
    print_separator("TEST 4: TEMPERATURE SCHEDULING (DECREASING)")

    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    # Initialize with decreasing temperature
    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=4,
        temperature=0.9,  # Start high
        temperature_schedule="decreasing",
        verbose=True
    )

    prompt = "Write a creative explanation of how neural networks work."

    print(f"Prompt: {prompt}\n")

    result = feedback.improve(prompt=prompt)

    print_result(result)

    # Show temperature schedule
    print("\n\nTEMPERATURE SCHEDULE:")
    print("-" * 80)
    for iteration in result.all_iterations:
        print(f"Iteration {iteration.iteration_number}: {iteration.temperature_used:.3f}")


def test_custom_temperature_schedule():
    """Test custom temperature schedule."""
    print_separator("TEST 5: CUSTOM TEMPERATURE SCHEDULE")

    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    # Custom temperature list
    custom_temps = [0.9, 0.7, 0.5, 0.3]

    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=4,
        temperature_schedule=custom_temps,
        verbose=True
    )

    prompt = "Explain quantum entanglement simply."

    print(f"Prompt: {prompt}\n")
    print(f"Custom temperature schedule: {custom_temps}\n")

    result = feedback.improve(prompt=prompt)

    print_result(result)


def test_convergence_detection():
    """Test convergence detection."""
    print_separator("TEST 6: CONVERGENCE DETECTION")

    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=10,  # High max, but should stop early
        convergence_threshold=0.05,  # 5% improvement threshold
        check_convergence=True,
        verbose=True
    )

    prompt = "What is machine learning?"

    print(f"Prompt: {prompt}\n")
    print("Note: Loop should stop early when improvements become minimal\n")

    result = feedback.improve(prompt=prompt)

    print_result(result)

    print(f"\n\nConvergence detected: {result.convergence_detected}")
    print(f"Stopped after {result.total_iterations} iterations (max was 10)")


def test_with_initial_answer():
    """Test starting with an existing answer."""
    print_separator("TEST 7: STARTING WITH INITIAL ANSWER")

    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=3,
        verbose=True
    )

    prompt = "Explain what an API is."

    # Provide a deliberately poor initial answer
    initial_answer = "API is a thing that computers use to talk. It's like a phone for programs."

    print(f"Prompt: {prompt}")
    print(f"\nInitial (poor) answer: {initial_answer}\n")

    result = feedback.improve(
        prompt=prompt,
        initial_answer=initial_answer,
        focus_on=["technical_accuracy", "clarity", "completeness"]
    )

    print_result(result)

    print("\n\nCOMPARISON:")
    print("-" * 80)
    print(f"Initial answer score: {result.initial_score}/10")
    print(f"Final answer score: {result.final_score}/10")
    print(f"Improvement: +{((result.final_score - result.initial_score) / result.initial_score):.1%}")


def test_focus_criteria():
    """Test focusing on specific criteria."""
    print_separator("TEST 8: FOCUSED IMPROVEMENT")

    llm = LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini")

    feedback = LLMFeedbackLoop(
        llm=llm,
        max_iterations=3,
        verbose=True
    )

    prompt = "Explain how blockchain works."

    print(f"Prompt: {prompt}")
    print("Focused improvement on: simplicity and clarity (ignoring technical depth)\n")

    result = feedback.improve(
        prompt=prompt,
        focus_on=["simplicity", "clarity"]  # Specifically ask for simple explanation
    )

    print_result(result)


def main():
    """Run all tests."""
    print("\n" + "#"*80)
    print("#  LLMFeedbackLoop Comprehensive Test Suite")
    print("#"*80)

    try:
        # Test 1: Single provider
        test_single_provider()

        # Test 2: Dual provider
        test_dual_provider()

        # Test 3: Multi-provider rotation
        test_multi_provider_rotation()

        # Test 4: Decreasing temperature
        test_temperature_scheduling()

        # Test 5: Custom temperature schedule
        test_custom_temperature_schedule()

        # Test 6: Convergence detection
        test_convergence_detection()

        # Test 7: Initial answer
        test_with_initial_answer()

        # Test 8: Focus criteria
        test_focus_criteria()

        print_separator("ALL TESTS COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
