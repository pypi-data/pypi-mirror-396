"""
Pydantic Edge Cases Unit Test Suite

This script tests the generate_json_example_from_pydantic function with Pydantic
edge case types that weren't covered in the basic test suites.

Test Coverage:
1. Enum fields (str and int enums)
2. datetime/date/time types
3. UUID fields
4. Literal types
5. Field aliases
6. Complex combinations of above

Usage:
    python tests/test_pydantic_edge_cases.py
"""

import json
import time
from typing import Dict, List, Optional, Literal
from enum import Enum
from datetime import datetime, date, time as time_type
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError
from SimplerLLM.tools.json_helpers import generate_json_example_from_pydantic


# ============================================================================
# TEST 1: Basic Enum
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


# ============================================================================
# TEST 2: Multiple Enum Types
# ============================================================================
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


# ============================================================================
# TEST 3: datetime/date/time Fields
# ============================================================================
class Event(BaseModel):
    """Model with various datetime types."""
    event_name: str = Field(min_length=3)
    event_date: date
    start_time: time_type
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============================================================================
# TEST 4: UUID Fields
# ============================================================================
class DatabaseRecord(BaseModel):
    """Model with UUID fields."""
    record_id: UUID
    user_id: UUID
    name: str = Field(min_length=2)
    description: Optional[str] = None


# ============================================================================
# TEST 5: Mixed datetime + UUID + Enum
# ============================================================================
class AuditLog(BaseModel):
    """Complex model combining UUID, datetime, enum, and literal."""
    log_id: UUID
    action: Literal["create", "update", "delete"]
    timestamp: datetime
    user_role: UserRole
    details: Optional[str] = None


# ============================================================================
# TEST 6: Literal Types
# ============================================================================
class Configuration(BaseModel):
    """Model with Literal type fields."""
    environment: Literal["development", "staging", "production"]
    debug: bool
    log_level: Literal["debug", "info", "warning", "error"]
    max_connections: int = Field(ge=1, le=1000)


# ============================================================================
# TEST 7: Field Aliases
# ============================================================================
class APIResponse(BaseModel):
    """Model with field aliases (camelCase JSON keys)."""
    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    user_id: str = Field(alias="userId", min_length=3)
    first_name: str = Field(alias="firstName", min_length=1)
    last_name: str = Field(alias="lastName", min_length=1)
    email_address: str = Field(alias="emailAddress")
    is_verified: bool = Field(alias="isVerified", default=False)


# ============================================================================
# TEST 8: Complex Combined Model
# ============================================================================
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
        self.generated_json = None
        self.validated_model = None


def test_model(test_name: str, model_class: type) -> TestResult:
    """
    Test a Pydantic model with edge case types.

    Args:
        test_name: Name of the test
        model_class: Pydantic model to test

    Returns:
        TestResult
    """
    result = TestResult(test_name, model_class)
    start_time = time.time()

    try:
        # Step 1: Generate JSON example
        json_string = generate_json_example_from_pydantic(model_class)
        result.generated_json = json_string

        # Step 2: Parse JSON
        json_obj = json.loads(json_string)

        # Step 3: Validate with Pydantic model
        # Use model_validate to handle aliases properly
        validated_model = model_class.model_validate(json_obj)
        result.validated_model = validated_model

        # Step 4: Additional validation for edge cases
        validation_errors = validate_edge_case_types(validated_model, model_class, json_obj)
        if validation_errors:
            result.error = f"Type validation failed: {'; '.join(validation_errors)}"
        else:
            result.success = True

        result.time_ms = (time.time() - start_time) * 1000

    except ValidationError as e:
        result.error = f"Validation Error: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    except json.JSONDecodeError as e:
        result.error = f"JSON Decode Error: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    except Exception as e:
        result.error = f"{type(e).__name__}: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    return result


def validate_edge_case_types(model_instance: BaseModel, model_class: type, json_obj: dict) -> List[str]:
    """
    Additional validation for edge case types.

    Args:
        model_instance: Validated Pydantic instance
        model_class: Original model class
        json_obj: Raw JSON object

    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []

    # Validate Enum fields
    for field_name, field_info in model_class.model_fields.items():
        value = getattr(model_instance, field_name, None)

        # Check if field is an Enum
        field_type = field_info.annotation
        try:
            # Remove Optional wrapper if present
            if hasattr(field_type, '__origin__'):
                from typing import get_origin, get_args
                if get_origin(field_type).__name__ == 'UnionType' or str(get_origin(field_type)) == 'typing.Union':
                    args = get_args(field_type)
                    if type(None) in args:
                        field_type = [arg for arg in args if arg is not type(None)][0]

            if isinstance(field_type, type) and issubclass(field_type, Enum):
                if value is not None and not isinstance(value, field_type):
                    errors.append(f"Field '{field_name}' should be {field_type.__name__}, got {type(value).__name__}")
        except (TypeError, AttributeError):
            pass

        # Check UUID fields
        if field_type == UUID:
            if value is not None and not isinstance(value, UUID):
                errors.append(f"Field '{field_name}' should be UUID, got {type(value).__name__}")

        # Check datetime fields
        if field_type in [datetime, date, time_type]:
            if value is not None and not isinstance(value, field_type):
                errors.append(f"Field '{field_name}' should be {field_type.__name__}, got {type(value).__name__}")

    # Validate field aliases are used in JSON
    for field_name, field_info in model_class.model_fields.items():
        if field_info.alias:
            if field_info.alias not in json_obj and field_name in json_obj:
                errors.append(f"Field alias '{field_info.alias}' not used (found '{field_name}' instead)")

    return errors


def run_all_tests():
    """Run all edge case tests."""
    print("="*80)
    print("PYDANTIC EDGE CASES TEST SUITE")
    print("="*80)
    print()

    # Define test cases
    tests = [
        ("1. Basic Enum (str)", UserWithRole),
        ("2. Multiple Enum Types (str + int)", Task),
        ("3. datetime/date/time Fields", Event),
        ("4. UUID Fields", DatabaseRecord),
        ("5. Mixed datetime + UUID + Enum", AuditLog),
        ("6. Literal Types", Configuration),
        ("7. Field Aliases", APIResponse),
        ("8. Complex Combined Model", CompleteOrder),
    ]

    results = []

    # Run tests
    for test_name, model_class in tests:
        print(f"Testing: {test_name}")
        print("-"*80)

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
    print(f"  Total Time: {total_time:.2f}ms")
    print(f"  Average Time: {avg_time:.2f}ms")

    # Detailed results
    print(f"\nDetailed Results:")
    print("-"*80)
    print(f"{'Test Name':<45} {'Status':<10} {'Time (ms)':<12}")
    print("-"*80)

    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"{result.name:<45} {status:<10} {result.time_ms:>10.2f}")

    print("-"*80)

    print("\n" + "="*80)
    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("All Pydantic edge case types are working correctly.")
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
