"""
Pydantic Edge Cases LLM Integration Test Suite

This script tests the generate_pydantic_json_model function with Pydantic
edge case types using REAL LLM API calls.

Test Coverage:
1. Enum fields (str and int enums)
2. datetime/date/time types
3. UUID fields
4. Literal types
5. Field aliases
6. Complex combinations of above

Usage:
    python tests/test_pydantic_edge_cases_llm.py
"""

import json
import time
from typing import Dict, List, Optional, Literal
from enum import Enum
from datetime import datetime, date, time as time_type
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm_addons import generate_pydantic_json_model


# ============================================================================
# TEST MODELS (Same as unit tests)
# ============================================================================
class UserRole(str, Enum):
    """String-based enum for user roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserWithRole(BaseModel):
    """Simple model with enum field."""
    name: str
    role: UserRole
    is_active: bool = True


class Status(str, Enum):
    """String-based status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Priority(int, Enum):
    """Integer-based priority enum."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Task(BaseModel):
    """Model with both str and int enums."""
    name: str = Field(min_length=3)
    status: Status
    priority: Priority
    description: Optional[str] = None


class Event(BaseModel):
    """Model with various datetime types."""
    event_name: str = Field(min_length=3)
    event_date: date
    start_time: time_type
    created_at: datetime
    updated_at: Optional[datetime] = None


class DatabaseRecord(BaseModel):
    """Model with UUID fields."""
    record_id: UUID
    user_id: UUID
    name: str = Field(min_length=2)
    description: Optional[str] = None


class AuditLog(BaseModel):
    """Complex model combining UUID, datetime, enum, and literal."""
    log_id: UUID
    action: Literal["create", "update", "delete"]
    timestamp: datetime
    user_role: UserRole
    details: Optional[str] = None


class Configuration(BaseModel):
    """Model with Literal type fields."""
    environment: Literal["development", "staging", "production"]
    debug: bool
    log_level: Literal["debug", "info", "warning", "error"]
    max_connections: int = Field(ge=1, le=1000)


class APIResponse(BaseModel):
    """Model with field aliases (camelCase JSON keys)."""
    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    user_id: str = Field(alias="userId", min_length=3)
    first_name: str = Field(alias="firstName", min_length=1)
    last_name: str = Field(alias="lastName", min_length=1)
    email_address: str = Field(alias="emailAddress")
    is_verified: bool = Field(alias="isVerified", default=False)


class CompleteOrder(BaseModel):
    """Comprehensive model combining all edge case types."""
    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    order_id: UUID
    customer_name: str = Field(min_length=2)
    order_status: Literal["pending", "processing", "shipped", "delivered"]
    priority: Priority  # int Enum
    order_date: date
    delivery_time: time_type
    created_at: datetime
    user_id: str = Field(alias="userId")
    notes: Optional[str] = None


# ============================================================================
# Test Runner
# ============================================================================
class TestResult:
    """Store test result."""
    def __init__(self, name: str, model_class: type):
        self.name = name
        self.model_class = model_class
        self.success = False
        self.time_ms = 0.0
        self.error = None
        self.generated_model = None
        self.prompt = ""


def test_llm_generation(test_name: str, model_class: type, prompt: str, llm_instance: LLM) -> TestResult:
    """
    Test LLM-based generation with a Pydantic model.

    Args:
        test_name: Name of the test
        model_class: Pydantic model to test
        prompt: Prompt for LLM
        llm_instance: LLM instance to use

    Returns:
        TestResult
    """
    result = TestResult(test_name, model_class)
    result.prompt = prompt
    start_time = time.time()

    try:
        # Generate model using LLM
        model_instance = generate_pydantic_json_model(
            model_class=model_class,
            prompt=prompt,
            llm_instance=llm_instance,
            max_retries=3,
            temperature=0.7
        )

        # Check if result is error string
        if isinstance(model_instance, str):
            result.error = model_instance
        elif isinstance(model_instance, model_class):
            result.generated_model = model_instance
            result.success = True
        else:
            result.error = f"Unexpected return type: {type(model_instance)}"

        result.time_ms = (time.time() - start_time) * 1000

    except Exception as e:
        result.error = f"{type(e).__name__}: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    return result


def run_all_tests():
    """Run all LLM edge case tests."""
    print("="*80)
    print("PYDANTIC EDGE CASES LLM INTEGRATION TEST SUITE")
    print("="*80)
    print()

    # Initialize LLM
    print("Initializing LLM (OpenAI GPT-4o-mini)...")
    llm_instance = LLM.create(provider=LLMProvider.OPENAI, model_name="gpt-4o-mini")
    print()

    # Define test cases (model, prompt)
    tests = [
        (
            "1. Basic Enum (str)",
            UserWithRole,
            "Create a user profile for an admin user named 'Alice' who is currently active."
        ),
        (
            "2. Multiple Enum Types (str + int)",
            Task,
            "Create a task for implementing user authentication with high priority and active status."
        ),
        (
            "3. datetime/date/time Fields",
            Event,
            "Create an event for a team meeting scheduled for tomorrow at 2:00 PM."
        ),
        (
            "4. UUID Fields",
            DatabaseRecord,
            "Create a database record for user 'John Smith' with valid UUIDs."
        ),
        (
            "5. Mixed datetime + UUID + Enum",
            AuditLog,
            "Create an audit log entry for a 'create' action performed by an admin user just now."
        ),
        (
            "6. Literal Types",
            Configuration,
            "Create a configuration for a production environment with info log level, no debugging, and 100 max connections."
        ),
        (
            "7. Field Aliases",
            APIResponse,
            "Create an API response for user 'john_doe' with first name 'John', last name 'Doe', email 'john@example.com', and verified status."
        ),
        (
            "8. Complex Combined Model",
            CompleteOrder,
            "Create a complete order for customer 'Jane Smith' with high priority, pending status, scheduled for delivery tomorrow at 3:30 PM."
        ),
    ]

    results = []

    # Run tests
    for test_name, model_class, prompt in tests:
        print(f"Testing: {test_name}")
        print("-"*80)
        print(f"Prompt: {prompt[:60]}..." if len(prompt) > 60 else f"Prompt: {prompt}")

        result = test_llm_generation(test_name, model_class, prompt, llm_instance)
        results.append(result)

        if result.success:
            print(f"[PASS] ({result.time_ms:.0f}ms)")
            # Print a few key fields from the generated model
            model_dict = result.generated_model.model_dump()
            preview = str(model_dict)[:100]
            print(f"Generated: {preview}..." if len(str(model_dict)) > 100 else f"Generated: {preview}")
        else:
            print(f"[FAIL] ({result.time_ms:.0f}ms)")
            error_preview = result.error[:100] + "..." if len(result.error) > 100 else result.error
            print(f"Error: {error_preview}")

        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    if failed > 0:
        print("\nFailed Tests:")
        print("-"*80)
        for result in results:
            if not result.success:
                print(f"  [X] {result.name}")
                error_preview = result.error[:100] + "..." if len(result.error) > 100 else result.error
                print(f"      {error_preview}")
                print()

    # Performance
    total_time = sum(r.time_ms for r in results)
    avg_time = total_time / total if total > 0 else 0

    print(f"\nPerformance:")
    print(f"  Total Time: {total_time:.0f}ms ({total_time/1000:.1f}s)")
    print(f"  Average Time: {avg_time:.0f}ms")

    # Detailed results
    print(f"\nDetailed Results:")
    print("-"*80)
    print(f"{'Test Name':<45} {'Status':<10} {'Time (ms)':<12}")
    print("-"*80)

    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"{result.name:<45} {status:<10} {result.time_ms:>10.0f}")

    print("-"*80)

    print("\n" + "="*80)
    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("All Pydantic edge case types work correctly with LLM generation.")
    else:
        print(f"WARNING: {failed} test(s) failed.")
        print("Review the errors above.")
    print("="*80)

    return results, failed


if __name__ == "__main__":
    import sys
    try:
        results, failed_count = run_all_tests()
        sys.exit(1 if failed_count > 0 else 0)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
