"""
Comprehensive Test Suite for generate_json_example_from_pydantic Function

This script tests the generate_json_example_from_pydantic function with various
Pydantic model structures to ensure it handles all common patterns correctly.

Test Coverage:
1. Simple types (str, int, float, bool)
2. Numeric constraints (ge, le, gt, lt)
3. String constraints (min_length, max_length)
4. Optional fields and Union types
5. Lists with constraints (min_items, max_items)
6. Dictionaries with typed values
7. Nested Pydantic models
8. Complex deeply nested structures
9. Models with json_schema_extra examples
10. Real-world complex models
"""

import json
import time
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ValidationError
from SimplerLLM.tools.json_helpers import generate_json_example_from_pydantic


# ============================================================================
# TEST 1: Simple Types
# ============================================================================
class SimpleModel(BaseModel):
    """Basic model with simple types."""
    name: str
    age: int
    score: float
    active: bool


# ============================================================================
# TEST 2: Numeric Constraints
# ============================================================================
class NumericConstraintsModel(BaseModel):
    """Model with numeric field constraints."""
    rating: float = Field(ge=1.0, le=10.0, description="Rating between 1 and 10")
    rank: int = Field(ge=1, description="Rank must be at least 1")
    percentage: float = Field(gt=0.0, lt=100.0, description="Percentage between 0 and 100 (exclusive)")
    count: int = Field(gt=0, le=1000, description="Count between 1 and 1000")


# ============================================================================
# TEST 3: String Constraints
# ============================================================================
class StringConstraintsModel(BaseModel):
    """Model with string field constraints."""
    username: str = Field(min_length=3, max_length=20, description="Username 3-20 chars")
    description: str = Field(min_length=10, description="Description at least 10 chars")
    code: str = Field(max_length=5, description="Code max 5 chars")
    bio: str = Field(min_length=50, max_length=200, description="Bio 50-200 chars")


# ============================================================================
# TEST 4: Optional Fields and Unions
# ============================================================================
class OptionalFieldsModel(BaseModel):
    """Model with optional fields."""
    required_field: str
    optional_string: Optional[str] = None
    optional_int: Optional[int] = None
    optional_list: Optional[List[str]] = None
    union_field: Union[str, int] = "default"


# ============================================================================
# TEST 5: Lists with Constraints
# ============================================================================
class ListConstraintsModel(BaseModel):
    """Model with list constraints."""
    tags: List[str] = Field(description="List of tags")
    scores: List[float] = Field(min_items=2, description="At least 2 scores")
    items: List[int] = Field(min_items=1, max_items=5, description="1-5 items")


# ============================================================================
# TEST 6: Dictionaries
# ============================================================================
class DictModel(BaseModel):
    """Model with dictionary fields."""
    metadata: Dict[str, str] = Field(description="String to string mapping")
    scores: Dict[str, float] = Field(description="String to float mapping")
    settings: Dict[str, Any] = Field(description="String to any type mapping")


# ============================================================================
# TEST 7: Nested Pydantic Models
# ============================================================================
class Address(BaseModel):
    """Nested address model."""
    street: str
    city: str
    zipcode: str = Field(min_length=5, max_length=10)


class Person(BaseModel):
    """Model containing nested Pydantic model."""
    name: str
    age: int = Field(ge=0, le=150)
    address: Address


# ============================================================================
# TEST 8: Complex Deeply Nested Structure
# ============================================================================
class Criteria(BaseModel):
    """Criteria for evaluation."""
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    description: str = Field(min_length=10)


class Evaluation(BaseModel):
    """Evaluation with criteria."""
    evaluator: str
    score: float = Field(ge=0.0, le=10.0)
    criteria: List[Criteria] = Field(min_items=1)
    comments: Optional[List[str]] = None


class Project(BaseModel):
    """Complex project model."""
    project_name: str = Field(min_length=3)
    description: str
    evaluations: List[Evaluation] = Field(min_items=1)
    metadata: Dict[str, str]
    priority: int = Field(ge=1, le=5)


# ============================================================================
# TEST 9: Model with json_schema_extra Example
# ============================================================================
class ModelWithExample(BaseModel):
    """Model that provides its own example via json_schema_extra."""
    product_id: int = Field(ge=1)
    product_name: str
    price: float = Field(ge=0.01)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 42,
                "product_name": "Example Product",
                "price": 99.99
            }
        }


# ============================================================================
# TEST 10: Real-world Complex Model (ProviderEvaluation)
# ============================================================================
class ProviderEvaluation(BaseModel):
    """Evaluation metrics for a single provider's response."""
    provider_name: str = Field(description="Name of the provider being evaluated")
    overall_score: float = Field(
        description="Overall quality score from 1-10",
        ge=1.0,
        le=10.0
    )
    rank: int = Field(
        description="Ranking position (1 = best, 2 = second best, etc.)",
        ge=1
    )
    criterion_scores: Dict[str, float] = Field(
        description="Scores for individual criteria (e.g., {'accuracy': 9.0, 'clarity': 8.5})",
        default_factory=dict
    )
    reasoning: str = Field(description="Judge's explanation for the scores and ranking")
    strengths: Optional[List[str]] = Field(
        default=None,
        description="List of identified strengths in this response"
    )
    weaknesses: Optional[List[str]] = Field(
        default=None,
        description="List of identified weaknesses in this response"
    )


# ============================================================================
# Test Runner
# ============================================================================
class TestResult:
    """Store test results."""
    def __init__(self, name: str, model_class: type, success: bool,
                 time_ms: float, error: str = None, generated_json: str = None):
        self.name = name
        self.model_class = model_class
        self.success = success
        self.time_ms = time_ms
        self.error = error
        self.generated_json = generated_json


def test_model(test_name: str, model_class: type) -> TestResult:
    """
    Test a Pydantic model with generate_json_example_from_pydantic.

    Args:
        test_name: Descriptive name for the test
        model_class: Pydantic model class to test

    Returns:
        TestResult with success/failure information
    """
    start_time = time.time()

    try:
        # Step 1: Generate JSON example
        json_string = generate_json_example_from_pydantic(model_class)

        # Step 2: Validate it's valid JSON
        json_obj = json.loads(json_string)

        # Step 3: Validate it conforms to the Pydantic model
        validated_model = model_class(**json_obj)

        # Success!
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=test_name,
            model_class=model_class,
            success=True,
            time_ms=elapsed_ms,
            generated_json=json_string
        )

    except ValidationError as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = f"Validation Error: {str(e)}"
        return TestResult(
            name=test_name,
            model_class=model_class,
            success=False,
            time_ms=elapsed_ms,
            error=error_msg
        )

    except json.JSONDecodeError as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = f"JSON Decode Error: {str(e)}"
        return TestResult(
            name=test_name,
            model_class=model_class,
            success=False,
            time_ms=elapsed_ms,
            error=error_msg
        )

    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = f"Unexpected Error: {type(e).__name__}: {str(e)}"
        return TestResult(
            name=test_name,
            model_class=model_class,
            success=False,
            time_ms=elapsed_ms,
            error=error_msg
        )


def run_all_tests():
    """Run all test cases and display results."""
    print("=" * 80)
    print("COMPREHENSIVE PYDANTIC MODEL STRUCTURE TESTS")
    print("=" * 80)
    print()

    # Define all tests
    tests = [
        ("Simple Types", SimpleModel),
        ("Numeric Constraints (ge, le, gt, lt)", NumericConstraintsModel),
        ("String Constraints (min_length, max_length)", StringConstraintsModel),
        ("Optional Fields and Unions", OptionalFieldsModel),
        ("Lists with Constraints", ListConstraintsModel),
        ("Dictionaries", DictModel),
        ("Nested Pydantic Models", Person),
        ("Complex Deeply Nested Structure", Project),
        ("Model with json_schema_extra", ModelWithExample),
        ("Real-world Complex Model (ProviderEvaluation)", ProviderEvaluation),
    ]

    results = []

    # Run each test
    for test_name, model_class in tests:
        print(f"Testing: {test_name}")
        print("-" * 80)

        result = test_model(test_name, model_class)
        results.append(result)

        if result.success:
            print(f"[PASS] ({result.time_ms:.2f}ms)")
            print(f"Generated JSON: {result.generated_json[:100]}..." if len(result.generated_json) > 100 else f"Generated JSON: {result.generated_json}")
        else:
            print(f"[FAIL] ({result.time_ms:.2f}ms)")
            print(f"Error: {result.error}")

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    if failed > 0:
        print("\nFailed Tests:")
        print("-" * 80)
        for result in results:
            if not result.success:
                print(f"  [X] {result.name}")
                print(f"    Error: {result.error[:100]}...")
                print()

    # Detailed results table
    print("\nDetailed Results:")
    print("-" * 80)
    print(f"{'Test Name':<45} {'Status':<10} {'Time (ms)':<12}")
    print("-" * 80)

    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"{result.name:<45} {status:<10} {result.time_ms:>10.2f}")

    print("-" * 80)

    # Performance stats
    total_time = sum(r.time_ms for r in results)
    avg_time = total_time / total if total > 0 else 0

    print(f"\nPerformance:")
    print(f"  Total Time: {total_time:.2f}ms")
    print(f"  Average Time per Test: {avg_time:.2f}ms")
    print(f"  Fastest Test: {min(results, key=lambda r: r.time_ms).name} ({min(r.time_ms for r in results):.2f}ms)")
    print(f"  Slowest Test: {max(results, key=lambda r: r.time_ms).name} ({max(r.time_ms for r in results):.2f}ms)")

    print("\n" + "=" * 80)

    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("The generate_json_example_from_pydantic function handles all tested Pydantic structures correctly.")
    else:
        print(f"WARNING: {failed} test(s) failed. Please review the errors above.")

    print("=" * 80)

    return results


if __name__ == "__main__":
    results = run_all_tests()
