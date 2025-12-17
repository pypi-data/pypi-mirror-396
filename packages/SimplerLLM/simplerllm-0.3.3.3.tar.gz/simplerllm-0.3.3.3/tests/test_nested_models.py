"""
Nested Pydantic Models Test Suite

This script comprehensively tests the generate_json_example_from_pydantic function
with nested Pydantic models, progressing from simple to highly complex nesting patterns.

Test Levels:
- Level 1: Simple nesting (1-2 levels)
- Level 2: Lists of nested models
- Level 3: Multi-level nesting (3+ levels)
- Level 4: Complex patterns (circular references, dicts of models, real-world)

Usage:
    python tests/test_nested_models.py                 # Run all tests
    python tests/test_nested_models.py --unit-only     # Unit tests only (no API)
    python tests/test_nested_models.py --llm-only      # LLM tests only
    python tests/test_nested_models.py --level 2       # Test specific level
    python tests/test_nested_models.py --fail-fast     # Stop at first failure
    python tests/test_nested_models.py --verbose       # Show generated JSON
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from SimplerLLM.tools.json_helpers import generate_json_example_from_pydantic


# ============================================================================
# LEVEL 1: SIMPLE NESTING (1-2 levels)
# ============================================================================

# TEST 1.1: Single Nested Model
class Address(BaseModel):
    """Simple address model."""
    street: str = Field(min_length=5)
    city: str = Field(min_length=2)
    state: str = Field(min_length=2, max_length=2)
    zipcode: str = Field(min_length=5, max_length=10)


class Person(BaseModel):
    """Person with nested address."""
    name: str = Field(min_length=2)
    age: int = Field(ge=0, le=150)
    address: Address


# TEST 1.2: Optional Nested Model
class ContactInfo(BaseModel):
    """Contact information."""
    email: str
    phone: Optional[str] = None
    preferred_method: str = "email"


class User(BaseModel):
    """User with optional contact info."""
    username: str = Field(min_length=3, max_length=20)
    full_name: str
    contact: Optional[ContactInfo] = None
    is_active: bool = True


# TEST 1.3: Multiple Nested Models
class Department(BaseModel):
    """Department information."""
    dept_name: str
    dept_code: str = Field(min_length=2, max_length=5)
    budget: float = Field(gt=0.0)


class Employee(BaseModel):
    """Employee with address and department."""
    employee_id: int = Field(ge=1)
    name: str
    address: Address
    department: Department
    salary: float = Field(gt=0.0)


# ============================================================================
# LEVEL 2: LISTS OF NESTED MODELS
# ============================================================================

# TEST 2.1: List of Nested Models
class TeamMember(BaseModel):
    """Individual team member."""
    name: str
    role: str
    years_experience: int = Field(ge=0, le=50)


class Team(BaseModel):
    """Team with list of members."""
    team_name: str = Field(min_length=3)
    team_lead: str
    members: List[TeamMember] = Field(min_length=2, description="At least 2 members")


# TEST 2.2: Nested Model with List
class OrderItem(BaseModel):
    """Individual order item."""
    product_name: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(gt=0.0)


class Order(BaseModel):
    """Order with list of items."""
    order_id: str = Field(min_length=3)
    customer_name: str
    items: List[OrderItem] = Field(min_length=1, description="At least one item")
    total_amount: float = Field(gt=0.0)


# TEST 2.3: List of Nested with Constraints
class Student(BaseModel):
    """Student information."""
    student_id: str = Field(min_length=5)
    name: str
    gpa: float = Field(ge=0.0, le=4.0)
    enrolled_year: int = Field(ge=2000, le=2030)


class Course(BaseModel):
    """Course with minimum 3 students."""
    course_code: str = Field(min_length=3, max_length=10)
    course_name: str
    instructor: str
    students: List[Student] = Field(min_length=3, description="At least 3 students")
    max_capacity: int = Field(ge=3, le=100)


# ============================================================================
# LEVEL 3: MULTI-LEVEL NESTING (3+ levels)
# ============================================================================

# TEST 3.1: Three-Level Nesting
class EmployeeAddress(BaseModel):
    """Employee address (level 3)."""
    street: str
    city: str
    zipcode: str = Field(min_length=5)


class CompanyEmployee(BaseModel):
    """Employee with address (level 2)."""
    name: str
    position: str
    address: EmployeeAddress


class CompanyDepartment(BaseModel):
    """Department with employees (level 1)."""
    dept_name: str
    manager: CompanyEmployee
    employees: List[CompanyEmployee] = Field(min_length=1)


class Company(BaseModel):
    """Company with departments (root)."""
    company_name: str
    founded_year: int = Field(ge=1800, le=2030)
    departments: List[CompanyDepartment] = Field(min_length=1)
    headquarters: Address


# TEST 3.2: Nested Lists at Multiple Levels
class UniversityStudent(BaseModel):
    """Student (level 3)."""
    name: str
    student_id: str = Field(min_length=5)
    major: str


class UniversityCourse(BaseModel):
    """Course with students (level 2)."""
    course_code: str
    course_name: str
    students: List[UniversityStudent] = Field(min_length=2)


class UniversityDepartment(BaseModel):
    """Department with courses (level 1)."""
    dept_name: str
    dept_head: str
    courses: List[UniversityCourse] = Field(min_length=1)


class University(BaseModel):
    """University with departments (root)."""
    university_name: str
    location: str
    departments: List[UniversityDepartment] = Field(min_length=1)
    established_year: int = Field(ge=1000, le=2030)


# TEST 3.3: Mixed Nesting (Lists, Nested, Optional)
class Task(BaseModel):
    """Individual task (level 3)."""
    task_name: str
    status: str
    priority: int = Field(ge=1, le=5)


class Project(BaseModel):
    """Project with tasks (level 2)."""
    project_name: str
    deadline: str
    tasks: List[Task] = Field(min_length=1)
    budget: Optional[float] = None


class OrganizationTeam(BaseModel):
    """Team with projects (level 1)."""
    team_name: str
    team_size: int = Field(ge=1)
    projects: List[Project] = Field(min_length=1)
    manager: Optional[str] = None


class Organization(BaseModel):
    """Organization with teams (root)."""
    org_name: str
    industry: str
    teams: List[OrganizationTeam] = Field(min_length=1)
    ceo: str


# ============================================================================
# LEVEL 4: COMPLEX PATTERNS
# ============================================================================

# TEST 4.1: Self-Referential (Circular Reference)
class TreeNode(BaseModel):
    """Tree node with optional children (self-referential)."""
    node_id: str
    node_value: str
    children: Optional[List['TreeNode']] = None


# TEST 4.2: Dict of Nested Models
class ProjectTeam(BaseModel):
    """Team for a project."""
    team_lead: str
    members: List[str] = Field(min_length=1)
    budget: float = Field(gt=0.0)


class ProjectWithTeams(BaseModel):
    """Project with dict of teams."""
    project_name: str
    description: str
    teams: Dict[str, ProjectTeam] = Field(description="Teams by department")


# TEST 4.3: Real-World E-commerce Order
class PaymentMethod(BaseModel):
    """Payment method details."""
    method_type: str  # credit_card, paypal, etc
    last_four: Optional[str] = Field(None, min_length=4, max_length=4)
    cardholder_name: Optional[str] = None


class Customer(BaseModel):
    """Customer information."""
    customer_id: str = Field(min_length=5)
    name: str
    email: str
    shipping_address: Address
    billing_address: Address
    payment_method: PaymentMethod


class PriceDetails(BaseModel):
    """Price breakdown for an item."""
    base_price: float = Field(gt=0.0)
    tax: float = Field(ge=0.0)
    discount: float = Field(ge=0.0, le=100.0)  # percentage
    final_price: float = Field(gt=0.0)


class Product(BaseModel):
    """Product information."""
    product_id: str
    name: str
    category: str
    in_stock: bool = True


class EcommerceOrderItem(BaseModel):
    """Order item with product and pricing."""
    item_id: str
    product: Product
    quantity: int = Field(ge=1)
    pricing: PriceDetails


class ShippingCarrier(BaseModel):
    """Shipping carrier info."""
    carrier_name: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None


class ShippingInfo(BaseModel):
    """Shipping information."""
    shipping_address: Address
    carrier: ShippingCarrier
    shipping_cost: float = Field(ge=0.0)


class Transaction(BaseModel):
    """Payment transaction."""
    transaction_id: str
    amount: float = Field(gt=0.0)
    status: str
    timestamp: str


class EcommerceOrder(BaseModel):
    """Complete e-commerce order with all nested details."""
    order_id: str = Field(min_length=5)
    customer: Customer
    items: List[EcommerceOrderItem] = Field(min_length=1)
    shipping_info: ShippingInfo
    transactions: List[Transaction] = Field(min_length=1)
    order_date: str
    status: str
    total_amount: float = Field(gt=0.0)


# ============================================================================
# Test Configuration and Runner
# ============================================================================

class TestConfig:
    """Configuration for test execution."""
    def __init__(self):
        self.unit_only = "--unit-only" in sys.argv
        self.llm_only = "--llm-only" in sys.argv
        self.fail_fast = "--fail-fast" in sys.argv
        self.verbose = "--verbose" in sys.argv or "-v" in sys.argv
        self.level = self._get_level()

    def _get_level(self) -> Optional[int]:
        """Get specific level to test."""
        for i, arg in enumerate(sys.argv):
            if arg == "--level" and i + 1 < len(sys.argv):
                try:
                    return int(sys.argv[i + 1])
                except ValueError:
                    return None
        return None


class TestResult:
    """Store test result."""
    def __init__(self, name: str, level: int, test_type: str):
        self.name = name
        self.level = level
        self.test_type = test_type  # "unit" or "llm"
        self.success = False
        self.time_ms = 0.0
        self.error = None
        self.tokens = 0
        self.generated_data = None


def run_unit_test(model_class: type, test_name: str) -> TestResult:
    """
    Run unit test (validate JSON generation without LLM).

    Args:
        model_class: Pydantic model to test
        test_name: Name of the test

    Returns:
        TestResult
    """
    # Extract level from test name (e.g., "1.1" -> 1)
    level = int(test_name.split('.')[0])
    result = TestResult(test_name, level, "unit")
    start_time = time.time()

    try:
        # Generate JSON example
        json_string = generate_json_example_from_pydantic(model_class)

        # Parse JSON
        json_obj = json.loads(json_string)

        # Validate with Pydantic model
        validated_model = model_class(**json_obj)

        # Success
        result.success = True
        result.generated_data = validated_model
        result.time_ms = (time.time() - start_time) * 1000

    except ValidationError as e:
        result.error = f"Validation Error: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    except Exception as e:
        result.error = f"{type(e).__name__}: {str(e)}"
        result.time_ms = (time.time() - start_time) * 1000

    return result


def validate_nested_structure(model_instance: BaseModel, model_class: type) -> List[str]:
    """
    Validate that nested models are properly instantiated.

    Args:
        model_instance: Instance to validate
        model_class: Original model class

    Returns:
        List of validation issues (empty if all valid)
    """
    issues = []

    # Check that all required fields exist
    for field_name, field_info in model_class.model_fields.items():
        if field_info.is_required() and not hasattr(model_instance, field_name):
            issues.append(f"Missing required field: {field_name}")

    # TODO: Add more specific nested validation
    # - Check nested models are BaseModel instances, not dicts
    # - Validate list lengths at each nesting level
    # - Check optional fields are properly None or instances

    return issues


def print_test_header(level: int, level_name: str):
    """Print level header."""
    print(f"\n{'='*80}")
    print(f"LEVEL {level}: {level_name}")
    print(f"{'='*80}")


def print_test_result(result: TestResult, config: TestConfig):
    """Print test result."""
    indent = "  "
    status = "[PASS]" if result.success else "[FAIL]"
    time_str = f"{result.time_ms:.2f}ms" if result.time_ms < 1000 else f"{result.time_ms/1000:.1f}s"

    if result.test_type == "unit":
        print(f"{indent}{status} Unit Test ({time_str})")
    else:
        tokens_str = f", {result.tokens} tokens" if result.tokens > 0 else ""
        print(f"{indent}{status} LLM Test ({time_str}{tokens_str})")

    if not result.success:
        error_preview = result.error[:100] + "..." if len(result.error) > 100 else result.error
        print(f"{indent}  Error: {error_preview}")

    if config.verbose and result.success and result.generated_data:
        print(f"{indent}  Generated:")
        if isinstance(result.generated_data, BaseModel):
            data_dict = result.generated_data.model_dump()
        else:
            data_dict = result.generated_data
        print(f"{indent}    {json.dumps(data_dict, indent=6)[:200]}...")


def run_all_tests():
    """Run all nested model tests."""
    config = TestConfig()

    print("="*80)
    print("NESTED PYDANTIC MODELS TEST SUITE")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Mode: {'Unit Only' if config.unit_only else 'LLM Only' if config.llm_only else 'Both'}")
    print(f"  Level Filter: {config.level if config.level else 'All levels'}")
    print(f"  Fail Fast: {config.fail_fast}")
    print(f"  Verbose: {config.verbose}")

    # Define test cases by level
    test_cases = {
        1: [
            ("1.1", "Single Nested Model", Person),
            ("1.2", "Optional Nested Model", User),
            ("1.3", "Multiple Nested Models", Employee),
        ],
        2: [
            ("2.1", "List of Nested Models", Team),
            ("2.2", "Nested Model with List", Order),
            ("2.3", "List of Nested with Constraints", Course),
        ],
        3: [
            ("3.1", "Three-Level Nesting", Company),
            ("3.2", "Nested Lists at Multiple Levels", University),
            ("3.3", "Mixed Nesting", Organization),
        ],
        4: [
            ("4.1", "Self-Referential Model", TreeNode),
            ("4.2", "Dict of Nested Models", ProjectWithTeams),
            ("4.3", "Real-World E-commerce Order", EcommerceOrder),
        ],
    }

    level_names = {
        1: "SIMPLE NESTING (1-2 levels)",
        2: "LISTS OF NESTED MODELS",
        3: "MULTI-LEVEL NESTING (3+ levels)",
        4: "COMPLEX PATTERNS"
    }

    results = []
    should_stop = False

    # Run tests by level
    for level in sorted(test_cases.keys()):
        if config.level and level != config.level:
            continue

        if should_stop:
            break

        print_test_header(level, level_names[level])

        for test_id, test_desc, model_class in test_cases[level]:
            if should_stop:
                break

            print(f"\nTEST {test_id}: {test_desc}")

            # Run unit test
            if not config.llm_only:
                unit_result = run_unit_test(model_class, test_id)
                results.append(unit_result)
                print_test_result(unit_result, config)

                if config.fail_fast and not unit_result.success:
                    print(f"\n[FAIL-FAST] Stopping at first failure")
                    should_stop = True
                    continue

            # Run LLM test (placeholder - would need LLM instance)
            if not config.unit_only:
                # Skip LLM tests for now as they require API setup
                pass

    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    # Group results by level
    level_stats = {}
    for result in results:
        if result.level not in level_stats:
            level_stats[result.level] = {"passed": 0, "failed": 0, "total": 0}
        level_stats[result.level]["total"] += 1
        if result.success:
            level_stats[result.level]["passed"] += 1
        else:
            level_stats[result.level]["failed"] += 1

    print(f"\nResults by Complexity Level:")
    print("-"*80)
    for level in sorted(level_stats.keys()):
        stats = level_stats[level]
        print(f"Level {level} ({level_names[level]}):")
        print(f"  {stats['passed']}/{stats['total']} passed ({stats['passed']/stats['total']*100:.0f}%)")

    # Overall stats
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.success)
    failed_tests = total_tests - passed_tests

    print(f"\nOverall:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"  Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

    # Performance
    total_time = sum(r.time_ms for r in results)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    print(f"\nPerformance:")
    print(f"  Total Time: {total_time:.0f}ms ({total_time/1000:.1f}s)")
    print(f"  Average Time: {avg_time:.2f}ms")

    # Failed tests
    if failed_tests > 0:
        print(f"\nFailed Tests ({failed_tests}):")
        print("-"*80)
        for result in results:
            if not result.success:
                print(f"  [X] {result.name}: {result.test_type}")
                error_preview = result.error[:80] + "..." if len(result.error) > 80 else result.error
                print(f"      {error_preview}")

    print(f"\n{'='*80}")
    if failed_tests == 0:
        print("*** ALL TESTS PASSED! ***")
        print("All nested Pydantic model patterns are working correctly.")
    else:
        print(f"WARNING: {failed_tests} test(s) failed.")
        print("Review the errors above.")
    print("="*80)

    return results, failed_tests


if __name__ == "__main__":
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
