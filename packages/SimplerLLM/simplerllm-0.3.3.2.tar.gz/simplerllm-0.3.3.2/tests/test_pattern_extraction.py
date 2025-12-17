"""
Real LLM Pattern Extraction Test Suite for generate_structured_pattern

This script tests the generate_structured_pattern function with actual LLM API calls
to ensure it works correctly with real AI generation across various pattern types.

IMPORTANT: This script makes real API calls and will consume tokens/credits.
Ensure you have API keys configured in your .env file.

Usage:
    python tests/test_pattern_extraction.py

    Optional flags:
    --dry-run: Skip actual API calls (validation only)
    --verbose: Show detailed prompts and responses
    --provider: Choose LLM provider (openai, anthropic, gemini)

Examples:
    python tests/test_pattern_extraction.py --dry-run
    python tests/test_pattern_extraction.py --provider anthropic --verbose
"""

import os
import sys
import time
from typing import Optional
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm_addons import generate_structured_pattern
from SimplerLLM.language.llm_providers.llm_response_models import PatternExtractionResult


# ============================================================================
# Test Configuration and Helpers
# ============================================================================
class TestConfig:
    """Configuration for test execution."""
    def __init__(self):
        self.dry_run = "--dry-run" in sys.argv
        self.verbose = "--verbose" in sys.argv or "-v" in sys.argv
        self.provider_name = self._get_provider()

    def _get_provider(self) -> str:
        """Get provider from command line args."""
        for i, arg in enumerate(sys.argv):
            if arg == "--provider" and i + 1 < len(sys.argv):
                return sys.argv[i + 1].lower()
        return "openai"  # Default


class TestResult:
    """Store test results with metrics."""
    def __init__(self, name: str, pattern_type: str):
        self.name = name
        self.pattern_type = pattern_type
        self.success = False
        self.extracted_value = None
        self.extraction_result = None
        self.error = None
        self.time_ms = 0.0
        self.input_tokens = 0
        self.output_tokens = 0
        self.is_valid = False
        self.normalized_value = None


# ============================================================================
# Test Prompts for Each Pattern Type
# ============================================================================
TEST_PROMPTS = {
    "email": """
    What is the customer support email address for TechCorp?
    Provide a professional business email address.
    """,

    "phone": """
    What is the customer service phone number for a US-based company?
    Provide a US phone number in (XXX) XXX-XXXX format.
    """,

    "url": """
    What is the official website URL for a technology company called "InnovateTech"?
    Provide a complete URL with https protocol.
    """,

    "date": """
    When is the project deadline for the Q1 software release?
    Provide a specific date in 2025 (use YYYY-MM-DD format).
    """,

    "email_multiple": """
    List the contact emails for the following departments:
    - Sales
    - Support
    - Careers

    Provide realistic business email addresses.
    """,

    "phone_multiple": """
    Provide phone numbers for three different US-based company departments:
    - Main Office
    - Sales
    - Technical Support

    Use realistic US phone numbers.
    """,

    "ssn": """
    Generate a fictional Social Security Number in the format XXX-XX-XXXX.
    Use realistic digits (avoid 000, 666, or 9XX for the first group).
    IMPORTANT: This is for testing purposes only with fictional data.
    """,

    "credit_card": """
    Generate a test Visa credit card number that passes the Luhn algorithm.
    This is for testing payment validation systems.
    IMPORTANT: Use a fictional test card number (start with 4, 16 digits total).
    """,

    "ipv4": """
    What is a typical private IP address for a device on a home network?
    Provide an IPv4 address in the 192.168.x.x range.
    """,

    "custom_product_code": """
    Generate two product codes for our inventory system.
    Product codes follow the format: PROD-XXXXX (where X is a digit).
    Example: PROD-12345

    Provide two unique product codes.
    """,
}


# ============================================================================
# Test Execution Functions
# ============================================================================
def test_pattern_with_llm(
    pattern: str,
    prompt: str,
    llm_instance: LLM,
    config: TestConfig,
    extract_all: bool = False,
    validate: bool = True,
    normalize: bool = False,
    is_custom: bool = False
) -> TestResult:
    """
    Test pattern extraction with real LLM generation.

    Args:
        pattern: Pattern name or custom regex
        prompt: Prompt for LLM
        llm_instance: LLM instance
        config: Test configuration
        extract_all: Extract all matches
        validate: Validate extracted patterns
        normalize: Normalize extracted values
        is_custom: Whether this is a custom regex pattern

    Returns:
        TestResult with success/failure and metrics
    """
    pattern_type = pattern if not is_custom else "custom"
    result = TestResult(
        name=f"Extract {pattern_type.title()}",
        pattern_type=pattern_type
    )
    start_time = time.time()

    try:
        if config.dry_run:
            # Dry run mode - just simulate successful extraction
            result.success = True
            result.extracted_value = f"mock_{pattern_type}@example.com" if pattern_type == "email" else f"mock_{pattern_type}"
            result.time_ms = (time.time() - start_time) * 1000
            return result

        # Real LLM generation with full response
        response = generate_structured_pattern(
            pattern=pattern,
            prompt=prompt,
            llm_instance=llm_instance,
            extract_all=extract_all,
            validate=validate,
            normalize=normalize,
            max_retries=3,
            temperature=0.7,
            full_response=True
        )

        # Check if generation was successful
        if isinstance(response, str):
            # Error case
            result.success = False
            result.error = response
        else:
            # Success case - response is LLMFullResponse with extraction_result
            if hasattr(response, 'extraction_result'):
                extraction_result = response.extraction_result
                result.success = True
                result.extraction_result = extraction_result
                result.input_tokens = response.input_token_count or 0
                result.output_tokens = response.output_token_count or 0

                # Get first match data
                if extraction_result.matches:
                    first_match = extraction_result.matches[0]
                    result.extracted_value = first_match.value
                    result.is_valid = first_match.is_valid
                    result.normalized_value = first_match.normalized_value
            else:
                result.success = False
                result.error = "No extraction_result in response"

        result.time_ms = (time.time() - start_time) * 1000

    except Exception as e:
        result.success = False
        result.error = f"Exception: {type(e).__name__}: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    return result


def print_test_header(test_name: str, index: int, total: int):
    """Print test header."""
    print("\n" + "="*80)
    print(f"TEST {index}/{total}: {test_name}")
    print("="*80)


def print_test_result(result: TestResult, config: TestConfig):
    """Print test result details."""
    if result.success:
        print(f"[PASS] {result.name} ({result.time_ms:.0f}ms)")
        if not config.dry_run:
            print(f"Tokens: {result.input_tokens} in, {result.output_tokens} out")
            if result.extracted_value:
                print(f"Extracted: {result.extracted_value}")
            if result.normalized_value:
                print(f"Normalized: {result.normalized_value}")
            if hasattr(result, 'is_valid'):
                print(f"Valid: {result.is_valid}")
            if result.extraction_result:
                print(f"Total Matches: {result.extraction_result.total_matches}")
    else:
        print(f"[FAIL] {result.name} ({result.time_ms:.0f}ms)")
        if result.error:
            error_preview = result.error[:150] + "..." if len(result.error) > 150 else result.error
            print(f"Error: {error_preview}")


def print_summary(results: list, config: TestConfig):
    """Print comprehensive summary."""
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    if not config.dry_run:
        total_input_tokens = sum(r.input_tokens for r in results)
        total_output_tokens = sum(r.output_tokens for r in results)
        total_tokens = total_input_tokens + total_output_tokens

        # Cost estimation (GPT-4o-mini rates)
        cost_per_1m_input = 0.150
        cost_per_1m_output = 0.600
        estimated_cost = (
            (total_input_tokens / 1_000_000) * cost_per_1m_input +
            (total_output_tokens / 1_000_000) * cost_per_1m_output
        )

        print(f"\nToken Usage:")
        print(f"  Input Tokens: {total_input_tokens:,}")
        print(f"  Output Tokens: {total_output_tokens:,}")
        print(f"  Total Tokens: {total_tokens:,}")
        print(f"  Estimated Cost: ${estimated_cost:.4f}")

    # Performance stats
    total_time = sum(r.time_ms for r in results)
    avg_time = total_time / total if total > 0 else 0

    print(f"\nPerformance:")
    print(f"  Total Time: {total_time:.0f}ms ({total_time/1000:.1f}s)")
    print(f"  Average Time: {avg_time:.0f}ms")

    # Failed tests
    if failed > 0:
        print(f"\nFailed Tests ({failed}):")
        print("-"*80)
        for result in results:
            if not result.success:
                print(f"  [X] {result.name}")
                if result.error:
                    error_preview = result.error[:100] + "..." if len(result.error) > 100 else result.error
                    print(f"      {error_preview}")

    # Detailed results table
    print(f"\nDetailed Results:")
    print("-"*80)
    print(f"{'Test Name':<35} {'Status':<10} {'Time':<12} {'Tokens':<15}")
    print("-"*80)

    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        time_str = f"{result.time_ms:.0f}ms"
        tokens_str = f"{result.input_tokens + result.output_tokens}" if not config.dry_run else "N/A"

        print(f"{result.name:<35} {status:<10} {time_str:<12} {tokens_str:<15}")

    print("-"*80)

    # Final verdict
    print(f"\n{'='*80}")
    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("The generate_structured_pattern function works correctly with real LLMs")
        print("across all tested pattern types.")
    else:
        print(f"WARNING: {failed} test(s) failed.")
        print("Please review the errors above and check your API configuration.")
    print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================
def run_all_tests():
    """Run all pattern extraction tests."""
    config = TestConfig()

    print("="*80)
    print("REAL LLM PATTERN EXTRACTION TEST SUITE")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Provider: {config.provider_name}")
    print(f"  Dry Run: {config.dry_run}")
    print(f"  Verbose: {config.verbose}")

    # Initialize LLM
    llm_instance = None
    if not config.dry_run:
        try:
            if config.provider_name == "openai":
                llm_instance = LLM.create(provider=LLMProvider.OPENAI, model_name="gpt-4o-mini")
            elif config.provider_name == "anthropic":
                llm_instance = LLM.create(provider=LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022")
            elif config.provider_name == "gemini":
                llm_instance = LLM.create(provider=LLMProvider.GEMINI, model_name="gemini-1.5-flash")
            else:
                print(f"\nError: Unknown provider '{config.provider_name}'")
                print("Available providers: openai, anthropic, gemini")
                sys.exit(1)

            print(f"  LLM Initialized: {llm_instance.model_name}")
        except Exception as e:
            print(f"\nError initializing LLM: {e}")
            print("\nMake sure you have:")
            print("  1. API keys configured in .env file")
            print("  2. Correct provider name specified")
            print("\nRun with --dry-run to test without API calls")
            sys.exit(1)

    # Define all test cases
    # Each tuple: (test_name, pattern, prompt, extract_all, validate, normalize, is_custom)
    test_cases = [
        # Test 1: Extract single email
        (
            "Extract Email (Single)",
            "email",
            TEST_PROMPTS["email"],
            False,  # extract_all
            True,   # validate
            True,   # normalize
            False   # is_custom
        ),

        # Test 2: Extract single phone
        (
            "Extract Phone (Single)",
            "phone",
            TEST_PROMPTS["phone"],
            False,
            True,
            True,
            False
        ),

        # Test 3: Extract URL
        (
            "Extract URL",
            "url",
            TEST_PROMPTS["url"],
            False,
            True,
            True,
            False
        ),

        # Test 4: Extract date
        (
            "Extract Date",
            "date",
            TEST_PROMPTS["date"],
            False,
            True,
            True,
            False
        ),

        # Test 5: Extract multiple emails
        (
            "Extract Email (Multiple)",
            "email",
            TEST_PROMPTS["email_multiple"],
            True,   # extract_all = True
            True,
            True,
            False
        ),

        # Test 6: Extract multiple phones
        (
            "Extract Phone (Multiple)",
            "phone",
            TEST_PROMPTS["phone_multiple"],
            True,   # extract_all = True
            True,
            True,
            False
        ),

        # Test 7: Extract SSN
        (
            "Extract SSN",
            "ssn",
            TEST_PROMPTS["ssn"],
            False,
            True,
            True,
            False
        ),

        # Test 8: Extract credit card
        (
            "Extract Credit Card",
            "credit_card",
            TEST_PROMPTS["credit_card"],
            False,
            True,
            False,
            False
        ),

        # Test 9: Extract IPv4 address
        (
            "Extract IPv4 Address",
            "ipv4",
            TEST_PROMPTS["ipv4"],
            False,
            True,
            False,
            False
        ),

        # Test 10: Custom regex pattern (product codes)
        (
            "Extract Product Code (Custom)",
            {"custom": r"PROD-\d{5}"},
            TEST_PROMPTS["custom_product_code"],
            True,   # extract_all to get multiple codes
            False,  # no validator for custom
            False,
            True    # is_custom
        ),
    ]

    results = []

    # Run each test
    for index, (test_name, pattern, prompt, extract_all, validate, normalize, is_custom) in enumerate(test_cases, 1):
        print_test_header(test_name, index, len(test_cases))

        if config.verbose:
            print(f"\nPrompt: {prompt.strip()}\n")
            print(f"Pattern: {pattern}")
            print(f"Extract All: {extract_all}, Validate: {validate}, Normalize: {normalize}\n")

        result = test_pattern_with_llm(
            pattern=pattern,
            prompt=prompt,
            llm_instance=llm_instance,
            config=config,
            extract_all=extract_all,
            validate=validate,
            normalize=normalize,
            is_custom=is_custom
        )
        results.append(result)

        print_test_result(result, config)

        # Small delay between tests to avoid rate limiting
        if not config.dry_run and index < len(test_cases):
            time.sleep(0.5)

    # Print summary
    print_summary(results, config)

    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()
        # Exit with error code if any tests failed
        failed_count = sum(1 for r in results if not r.success)
        sys.exit(1 if failed_count > 0 else 0)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
