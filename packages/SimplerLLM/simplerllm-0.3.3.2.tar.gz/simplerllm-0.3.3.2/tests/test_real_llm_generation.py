"""
Real LLM Generation Test Suite for generate_pydantic_json_model

This script tests the generate_pydantic_json_model function with actual LLM API calls
to ensure it works correctly with real AI generation across various Pydantic model structures.

IMPORTANT: This script makes real API calls and will consume tokens/credits.
Ensure you have API keys configured in your .env file.

Usage:
    python tests/test_real_llm_generation.py

    Optional flags:
    --dry-run: Skip actual API calls (validation only)
    --verbose: Show detailed prompts and responses
    --provider: Choose LLM provider (openai, anthropic, gemini)
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ValidationError
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm_addons import generate_pydantic_json_model


# ============================================================================
# TEST MODEL 1: Simple Product Review
# ============================================================================
class ProductReview(BaseModel):
    """Simple model with basic types."""
    product_name: str
    rating: int = Field(ge=1, le=5, description="Integer rating from 1 to 5")
    pros: List[str] = Field(min_length=2, description="At least 2 pros")
    cons: List[str] = Field(min_length=1, description="At least 1 con")
    would_recommend: bool


# ============================================================================
# TEST MODEL 2: Movie Rating with Numeric Constraints
# ============================================================================
class MovieRating(BaseModel):
    """Model with numeric constraints."""
    movie_title: str
    year: int = Field(ge=1900, le=2025, description="Release year")
    overall_score: float = Field(ge=1.0, le=10.0, description="Score 1-10")
    stars: int = Field(ge=1, le=5, description="Star rating 1-5")
    box_office_millions: float = Field(gt=0.0, description="Box office in millions USD")


# ============================================================================
# TEST MODEL 3: Blog Post with String Constraints
# ============================================================================
class BlogPost(BaseModel):
    """Model with string length constraints."""
    title: str = Field(min_length=10, max_length=100, description="Blog title 10-100 chars")
    author: str = Field(min_length=2, max_length=50, description="Author name 2-50 chars")
    summary: str = Field(min_length=50, max_length=200, description="Summary 50-200 chars")
    tags: List[str] = Field(min_length=2, max_length=10, description="2-10 tags")
    word_count: int = Field(ge=100, le=10000, description="Word count 100-10000")


# ============================================================================
# TEST MODEL 4: User Profile with Optional Fields
# ============================================================================
class UserProfile(BaseModel):
    """Model with optional fields."""
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: Optional[int] = Field(None, ge=13, le=120)
    bio: Optional[str] = Field(None, min_length=10, max_length=500)
    interests: Optional[List[str]] = None
    is_verified: bool = False
    membership_level: Union[str, int] = "free"


# ============================================================================
# TEST MODEL 5: Recipe with List Constraints
# ============================================================================
class Recipe(BaseModel):
    """Model with list constraints."""
    dish_name: str
    cuisine_type: str
    ingredients: List[str] = Field(min_length=3, description="At least 3 ingredients")
    steps: List[str] = Field(min_length=3, max_length=15, description="3-15 cooking steps")
    prep_time_minutes: int = Field(ge=1, description="Prep time in minutes")
    difficulty: str


# ============================================================================
# TEST MODEL 6: Application Settings with Dictionaries
# ============================================================================
class AppSettings(BaseModel):
    """Model with dictionary fields."""
    app_name: str
    version: str
    config: Dict[str, str] = Field(description="Configuration key-value pairs")
    feature_flags: Dict[str, bool] = Field(description="Feature toggles")
    thresholds: Dict[str, float] = Field(description="Numeric thresholds")


# ============================================================================
# TEST MODEL 7: Company with Nested Models
# ============================================================================
class Address(BaseModel):
    """Nested address model."""
    street: str
    city: str
    state: str = Field(min_length=2, max_length=2, description="2-letter state code")
    zipcode: str = Field(min_length=5, max_length=10)


class Contact(BaseModel):
    """Nested contact model."""
    name: str
    title: str
    email: str
    phone: Optional[str] = None


class Company(BaseModel):
    """Model with nested Pydantic models."""
    company_name: str
    industry: str
    employee_count: int = Field(ge=1, description="Number of employees")
    headquarters: Address
    primary_contact: Contact
    founded_year: int = Field(ge=1800, le=2025)


# ============================================================================
# TEST MODEL 8: Conference Event with Complex Nesting
# ============================================================================
class Speaker(BaseModel):
    """Conference speaker."""
    name: str
    title: str
    company: str
    bio: str = Field(min_length=20)


class Session(BaseModel):
    """Conference session."""
    session_title: str
    duration_minutes: int = Field(ge=15, le=240)
    speakers: List[Speaker] = Field(min_length=1, max_length=5)
    topics: List[str] = Field(min_length=1)


class ConferenceEvent(BaseModel):
    """Complex nested event model."""
    event_name: str
    location: str
    date: str
    sessions: List[Session] = Field(min_length=1, description="At least one session")
    expected_attendees: int = Field(ge=10)


# ============================================================================
# TEST MODEL 9: Model with json_schema_extra Example
# ============================================================================
class ProductInventory(BaseModel):
    """Model that provides its own example."""
    sku: str = Field(min_length=3, max_length=20)
    product_name: str
    quantity: int = Field(ge=0)
    price: float = Field(ge=0.01)
    category: str

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "PROD-12345",
                "product_name": "Wireless Mouse",
                "quantity": 150,
                "price": 29.99,
                "category": "Electronics"
            }
        }


# ============================================================================
# TEST MODEL 10: Real-world ProviderEvaluation
# ============================================================================
class ProviderEvaluation(BaseModel):
    """Real-world complex model for LLM provider evaluation."""
    provider_name: str = Field(description="Name of the LLM provider")
    overall_score: float = Field(ge=1.0, le=10.0, description="Overall score 1-10")
    rank: int = Field(ge=1, description="Ranking position")
    criterion_scores: Dict[str, float] = Field(
        description="Individual criterion scores",
        default_factory=dict
    )
    reasoning: str = Field(min_length=20, description="Evaluation reasoning")
    strengths: Optional[List[str]] = Field(None, description="Identified strengths")
    weaknesses: Optional[List[str]] = Field(None, description="Identified weaknesses")


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
    def __init__(self, name: str, model_class: type):
        self.name = name
        self.model_class = model_class
        self.success = False
        self.generated_data = None
        self.error = None
        self.time_ms = 0.0
        self.input_tokens = 0
        self.output_tokens = 0
        self.retry_count = 0
        self.validation_errors = []


# ============================================================================
# Test Prompts for Each Model
# ============================================================================
TEST_PROMPTS = {
    "ProductReview": """
    Generate a review for a popular smartphone.
    IMPORTANT: rating must be a whole number (integer) from 1 to 5, NOT a decimal.
    Include at least 2 pros and 1 con.
    Be realistic and specific.
    """,

    "MovieRating": """
    Generate a rating for a recent blockbuster movie.
    Use realistic box office numbers (in millions).
    Provide a comprehensive score (decimal like 8.5) and star rating (integer 1-5).
    """,

    "BlogPost": """
    Generate metadata for a blog post about artificial intelligence.
    Make the title engaging and descriptive.
    Include relevant tags about AI, machine learning, etc.
    Ensure the summary is informative and within the character limits.
    """,

    "UserProfile": """
    Generate a user profile for a social media platform.
    Include optional fields like bio and interests.
    Make the user realistic - a 28-year old software developer.
    """,

    "Recipe": """
    Generate a recipe for a classic Italian pasta dish.
    IMPORTANT: Include at least 5 specific ingredients with quantities.
    Provide at least 5 clear step-by-step cooking instructions.
    Make it detailed and realistic.
    """,

    "AppSettings": """
    Generate application settings for a mobile app.
    IMPORTANT: The 'config' field must contain simple string key-value pairs only (e.g., "theme": "dark", "language": "en").
    Do NOT use nested objects or booleans in config - those go in feature_flags instead.
    Feature flags should be boolean values (true/false).
    Thresholds should be numeric decimal values.
    Example config: {"theme": "dark", "language": "en-US", "notification_pref": "all"}
    Example feature_flags: {"dark_mode": true, "beta_features": false}
    Example thresholds: {"max_upload_size": 10.5, "timeout_seconds": 30.0}
    """,

    "Company": """
    Generate information for a technology startup company.
    Include complete headquarters address in California.
    Provide details about the CEO as primary contact.
    Make the company founded in the last 10 years.
    """,

    "ConferenceEvent": """
    Generate details for a tech conference.
    Include 2-3 sessions with expert speakers.
    Each speaker should have a detailed bio.
    Make it a realistic AI/ML focused conference.
    """,

    "ProductInventory": """
    Generate inventory information for an electronic product in a warehouse.
    Use a realistic SKU format, quantity, and price.
    Choose an appropriate electronics category.
    """,

    "ProviderEvaluation": """
    Evaluate the response quality of an AI provider (OpenAI with GPT-4).
    The response was: "Quantum computing uses quantum bits that can exist in superposition,
    allowing parallel computation. It has applications in cryptography and drug discovery."

    Rate it on accuracy, clarity, and completeness (1-10 scale).
    Provide reasoning for your scores.
    List 2-3 strengths and 1-2 weaknesses.
    Give it an overall rank (assume comparing 3 providers).
    """
}


# ============================================================================
# Test Execution Functions
# ============================================================================
def test_model_with_llm(
    model_class: type,
    prompt: str,
    llm_instance: LLM,
    config: TestConfig
) -> TestResult:
    """
    Test a Pydantic model with real LLM generation.

    Args:
        model_class: Pydantic model class to test
        prompt: Prompt for LLM
        llm_instance: LLM instance
        config: Test configuration

    Returns:
        TestResult with success/failure and metrics
    """
    result = TestResult(name=model_class.__name__, model_class=model_class)
    start_time = time.time()

    try:
        if config.dry_run:
            # Dry run mode - just validate the model structure
            from SimplerLLM.tools.json_helpers import generate_json_example_from_pydantic
            json_example = generate_json_example_from_pydantic(model_class)
            result.generated_data = json.loads(json_example)
            result.success = True
            result.time_ms = (time.time() - start_time) * 1000
            return result

        # Real LLM generation with full response
        response = generate_pydantic_json_model(
            model_class=model_class,
            prompt=prompt,
            llm_instance=llm_instance,
            max_retries=3,
            temperature=0.7,
            full_response=True,
            system_prompt="You are a helpful AI that generates accurate, realistic data in structured JSON format."
        )

        # Check if generation was successful
        if isinstance(response, str):
            # Error case
            result.success = False
            result.error = response
        else:
            # Success case - response is LLMFullResponse
            result.success = True
            result.generated_data = response.model_object
            result.input_tokens = response.input_token_count or 0
            result.output_tokens = response.output_token_count or 0

        result.time_ms = (time.time() - start_time) * 1000

    except Exception as e:
        result.success = False
        result.error = f"Exception: {type(e).__name__}: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    return result


def validate_generated_data(result: TestResult) -> List[str]:
    """
    Validate the generated data for quality and constraint compliance.

    Args:
        result: TestResult with generated data

    Returns:
        List of validation issues (empty if all valid)
    """
    issues = []

    if not result.success or not result.generated_data:
        return issues

    model_instance = result.generated_data

    # Check if all required fields are present
    required_fields = [
        field_name for field_name, field_info in result.model_class.model_fields.items()
        if field_info.is_required()
    ]

    for field_name in required_fields:
        if not hasattr(model_instance, field_name):
            issues.append(f"Missing required field: {field_name}")

    # Additional semantic checks based on model type
    if result.name == "MovieRating":
        if hasattr(model_instance, 'movie_title'):
            if model_instance.movie_title.lower() in ['string', 'example', 'movie']:
                issues.append("Movie title appears to be placeholder text")

    elif result.name == "Recipe":
        if hasattr(model_instance, 'ingredients'):
            if len(model_instance.ingredients) < 3:
                issues.append(f"Recipe should have at least 3 ingredients, got {len(model_instance.ingredients)}")

    return issues


# ============================================================================
# Output Formatting
# ============================================================================
def print_test_header(test_name: str, index: int, total: int):
    """Print test header."""
    print(f"\n{'='*80}")
    print(f"TEST {index}/{total}: {test_name}")
    print(f"{'='*80}")


def print_test_result(result: TestResult, config: TestConfig):
    """Print individual test result."""
    if result.success:
        print(f"[PASS] {result.name} ({result.time_ms:.0f}ms)")

        if config.verbose and result.generated_data:
            print(f"\nGenerated Data:")
            if isinstance(result.generated_data, BaseModel):
                print(json.dumps(result.generated_data.model_dump(), indent=2))
            else:
                print(json.dumps(result.generated_data, indent=2))

        if not config.dry_run:
            print(f"Tokens: {result.input_tokens} in, {result.output_tokens} out")

    else:
        print(f"[FAIL] {result.name} ({result.time_ms:.0f}ms)")
        print(f"Error: {result.error}")


def print_summary(results: List[TestResult], config: TestConfig):
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
    print(f"{'Model Name':<30} {'Status':<10} {'Time':<12} {'Tokens':<15}")
    print("-"*80)

    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        time_str = f"{result.time_ms:.0f}ms"
        tokens_str = f"{result.input_tokens + result.output_tokens}" if not config.dry_run else "N/A"

        print(f"{result.name:<30} {status:<10} {time_str:<12} {tokens_str:<15}")

    print("-"*80)

    # Final verdict
    print(f"\n{'='*80}")
    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("The generate_pydantic_json_model function works correctly with real LLMs")
        print("across all tested Pydantic model structures.")
    else:
        print(f"WARNING: {failed} test(s) failed.")
        print("Please review the errors above and check your API configuration.")
    print("="*80)


# ============================================================================
# Main Test Runner
# ============================================================================
def run_all_tests():
    """Run all LLM generation tests."""
    config = TestConfig()

    print("="*80)
    print("REAL LLM GENERATION TEST SUITE")
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
    test_cases = [
        (ProductReview, TEST_PROMPTS["ProductReview"]),
        (MovieRating, TEST_PROMPTS["MovieRating"]),
        (BlogPost, TEST_PROMPTS["BlogPost"]),
        (UserProfile, TEST_PROMPTS["UserProfile"]),
        (Recipe, TEST_PROMPTS["Recipe"]),
        (AppSettings, TEST_PROMPTS["AppSettings"]),
        (Company, TEST_PROMPTS["Company"]),
        (ConferenceEvent, TEST_PROMPTS["ConferenceEvent"]),
        (ProductInventory, TEST_PROMPTS["ProductInventory"]),
        (ProviderEvaluation, TEST_PROMPTS["ProviderEvaluation"]),
    ]

    results = []

    # Run each test
    for index, (model_class, prompt) in enumerate(test_cases, 1):
        print_test_header(model_class.__name__, index, len(test_cases))

        if config.verbose:
            print(f"\nPrompt: {prompt.strip()}\n")

        result = test_model_with_llm(model_class, prompt, llm_instance, config)
        results.append(result)

        # Validate generated data
        if result.success:
            validation_issues = validate_generated_data(result)
            if validation_issues:
                print(f"\nValidation Warnings:")
                for issue in validation_issues:
                    print(f"  - {issue}")

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
