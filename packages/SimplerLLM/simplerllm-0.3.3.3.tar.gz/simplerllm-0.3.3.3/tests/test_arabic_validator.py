"""
Test script for validating Arabic root and pattern extraction using LLMValidator.

This script validates Arabic morphological analysis:
- Root extraction (جذر)
- Pattern identification (وزن)
"""

from SimplerLLM.language import LLM, LLMProvider
from SimplerLLM.language.llm_validator import LLMValidator


def validate_arabic_morphology(
    word: str,
    generated_root: str,
    generated_pattern: str,
    validators: list = None,
):
    """
    Validate Arabic root and pattern extraction.

    Args:
        word: The Arabic word being analyzed
        generated_root: The extracted root (e.g., "م-ر-ر" or "مرر")
        generated_pattern: The morphological pattern (e.g., "اِسْتِفْعَال")
        validators: Optional list of LLM validators

    Returns:
        ValidationResult with scores and explanations
    """
    # Create validators if not provided
    if validators is None:
        validators = [
            LLM.create(LLMProvider.OPENAI, model_name="gpt-5"),
            LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
            LLM.create(LLMProvider.GEMINI,model_name="gemini-2.5-flash")
        ]

    validator = LLMValidator(
        validators=validators,
        parallel=True,
        default_threshold=0.7,
        verbose=True,
    )

    # Build the content to validate
    content = f"""
Word (الكلمة): {word}
Extracted Root (الجذر): {generated_root}
Morphological Pattern (الوزن): {generated_pattern}
"""

    # Validation prompt with Arabic linguistics context
    validation_prompt = """
You are an expert in Arabic linguistics and morphology (علم الصرف).

Validate the following Arabic morphological analysis:
1. Is the extracted ROOT (جذر) correct for this word?
2. Is the morphological PATTERN (وزن) correct for this word?

Consider:
- Arabic roots are typically 3 consonants (trilateral/ثلاثي) or 4 consonants (quadrilateral/رباعي)
- The pattern should correctly represent the word's morphological form
- Common patterns include: فَعَلَ، فَعَّلَ، فَاعَلَ، أَفْعَلَ، تَفَعَّلَ، تَفَاعَلَ، اِنْفَعَلَ، اِفْتَعَلَ، اِفْعَلَّ، اِسْتَفْعَلَ

Score 1.0 if BOTH root and pattern are completely correct.
Score 0.5 if only ONE of them is correct.
Score 0.0 if BOTH are incorrect.

Provide detailed explanation of your analysis.
"""

    result = validator.validate(
        content=content,
        validation_prompt=validation_prompt,
        original_question=f"Extract the root and pattern for the Arabic word: {word}",
        aggregation="average",
    )

    return result


def main():
    print("=" * 70)
    print("Arabic Root & Pattern Validator")
    print("=" * 70)

    # Test case from user
    word = "استمرار"
    generated_root = "م-ر-ر مرر"
    generated_pattern = "اِسْتِفْعَال"

    print(f"\nWord: {word}")
    print(f"Generated Root: {generated_root}")
    print(f"Generated Pattern: {generated_pattern}")
    print("-" * 70)

    result = validate_arabic_morphology(
        word=word,
        generated_root=generated_root,
        generated_pattern=generated_pattern,
    )

    # Print results
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"\nOverall Score: {result.overall_score:.2f}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    print(f"Is Valid: {result.is_valid}")
    print(f"Consensus: {result.consensus}")
    print(f"Consensus Details: {result.consensus_details}")

    print("\n" + "-" * 70)
    print("Individual Validator Scores:")
    print("-" * 70)
    for v in result.validators:
        print(f"\n{v.provider_name} ({v.model_name}):")
        print(f"  Score: {v.score:.2f}")
        print(f"  Confidence: {v.confidence:.2f}")
        print(f"  Valid: {v.is_valid}")
        print(f"  Explanation: {v.explanation}")
        if v.error:
            print(f"  Error: {v.error}")


if __name__ == "__main__":
    main()
