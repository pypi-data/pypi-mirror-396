"""
Comprehensive Test Suite for Pattern Extraction Helper Functions

This script tests the pattern_helpers.py module functions with various
pattern types to ensure regex extraction, validation, and normalization
work correctly.

Test Coverage:
1. Email pattern extraction
2. Phone pattern extraction
3. URL pattern extraction
4. Date pattern extraction
5. Custom regex pattern extraction
6. Email validation (valid and invalid cases)
7. Phone validation
8. URL validation
9. SSN validation
10. Credit card validation (with Luhn algorithm)
11. Email normalization
12. Phone normalization (to E164 format)
13. URL normalization
14. Date normalization (to ISO 8601)
15. Extract all vs single match

IMPORTANT: This script does NOT make any API calls. It tests helper
functions directly for fast validation.

Usage:
    python tests/test_pattern_helpers.py
"""

import time
from SimplerLLM.tools.pattern_helpers import (
    extract_pattern_from_text,
    get_predefined_pattern,
    validate_email,
    validate_phone,
    validate_url,
    validate_ssn,
    validate_credit_card,
    normalize_email,
    normalize_phone,
    normalize_url,
    normalize_date,
)


# ============================================================================
# Test Data - Sample texts with various patterns
# ============================================================================

SAMPLE_TEXTS = {
    "email_single": "Please contact us at support@example.com for assistance.",
    "email_multiple": "Reach out to john@company.com or mary@business.org for help.",
    "phone_single": "Call us at (555) 123-4567 during business hours.",
    "phone_multiple": "Contact: 555-123-4567 or 555.987.6543 for support.",
    "url_single": "Visit our website at https://www.example.com for more info.",
    "url_multiple": "Check https://docs.example.com and http://blog.example.com",
    "date_single": "The deadline is 2025-01-15 for all submissions.",
    "date_multiple": "Events on 01/15/2025 and 02/20/2025 are confirmed.",
    "ssn_single": "SSN: 123-45-6789 on file.",
    "credit_card": "Card number: 4532015112830366 expires 12/25.",
    "ipv4_single": "Server at 192.168.1.100 is online.",
    "custom_pattern": "Order codes: PROD-12345 and PROD-67890 are ready.",
}

VALIDATION_SAMPLES = {
    "valid_email": "user@example.com",
    "invalid_email_no_at": "userexample.com",
    "invalid_email_no_domain": "user@",
    "valid_phone": "(555) 123-4567",
    "valid_phone_dashes": "555-123-4567",
    "invalid_phone_short": "555-1234",
    "valid_url": "https://example.com",
    "invalid_url_no_protocol": "example.com",
    "valid_ssn": "123-45-6789",
    "invalid_ssn_666": "666-45-6789",
    "valid_credit_card_visa": "4532015112830366",  # Valid Visa with Luhn check
    "invalid_credit_card_luhn": "4532015112830367",  # Fails Luhn check
}

NORMALIZATION_SAMPLES = {
    "email_mixed_case": "  John.Doe@EXAMPLE.COM  ",
    "phone_formatted": "(555) 123-4567",
    "phone_dots": "555.123.4567",
    "url_no_protocol": "example.com/path",
    "url_mixed_case": "HTTPS://EXAMPLE.COM/Path",
    "date_us_format": "01/15/2025",
    "date_iso_format": "2025-01-15",
}


# ============================================================================
# Test Runner Class
# ============================================================================
class TestResult:
    """Store test results."""
    def __init__(self, name: str, success: bool, time_ms: float,
                 error: str = None, result_data: str = None):
        self.name = name
        self.success = success
        self.time_ms = time_ms
        self.error = error
        self.result_data = result_data


# ============================================================================
# TEST 1: Email Pattern Extraction
# ============================================================================
def test_email_extraction() -> TestResult:
    """Test extracting email from text."""
    start_time = time.time()

    try:
        pattern = get_predefined_pattern("email")
        matches = extract_pattern_from_text(
            SAMPLE_TEXTS["email_single"],
            pattern,
            extract_all=False
        )

        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        assert matches[0]['value'] == "support@example.com", \
            f"Expected 'support@example.com', got '{matches[0]['value']}'"
        assert matches[0]['position'] > 0, "Position should be greater than 0"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Pattern Extraction",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Extracted: {matches[0]['value']}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Pattern Extraction",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 2: Phone Pattern Extraction
# ============================================================================
def test_phone_extraction() -> TestResult:
    """Test extracting phone number from text."""
    start_time = time.time()

    try:
        pattern = get_predefined_pattern("phone")
        matches = extract_pattern_from_text(
            SAMPLE_TEXTS["phone_single"],
            pattern,
            extract_all=False
        )

        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        # Phone pattern captures the formatted version
        assert "555" in matches[0]['value'] and "123" in matches[0]['value'], \
            f"Phone should contain '555' and '123', got '{matches[0]['value']}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Pattern Extraction",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Extracted: {matches[0]['value']}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Pattern Extraction",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 3: URL Pattern Extraction
# ============================================================================
def test_url_extraction() -> TestResult:
    """Test extracting URL from text."""
    start_time = time.time()

    try:
        pattern = get_predefined_pattern("url")
        matches = extract_pattern_from_text(
            SAMPLE_TEXTS["url_single"],
            pattern,
            extract_all=False
        )

        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        assert "https://www.example.com" in matches[0]['value'], \
            f"Expected 'https://www.example.com', got '{matches[0]['value']}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Pattern Extraction",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Extracted: {matches[0]['value']}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Pattern Extraction",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 4: Date Pattern Extraction
# ============================================================================
def test_date_extraction() -> TestResult:
    """Test extracting date from text."""
    start_time = time.time()

    try:
        pattern = get_predefined_pattern("date")
        matches = extract_pattern_from_text(
            SAMPLE_TEXTS["date_single"],
            pattern,
            extract_all=False
        )

        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        assert "2025" in matches[0]['value'], \
            f"Date should contain '2025', got '{matches[0]['value']}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Date Pattern Extraction",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Extracted: {matches[0]['value']}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Date Pattern Extraction",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 5: Custom Regex Pattern
# ============================================================================
def test_custom_pattern() -> TestResult:
    """Test extracting custom regex pattern (product codes)."""
    start_time = time.time()

    try:
        # Custom pattern for PROD-XXXXX format
        custom_pattern = r"PROD-\d{5}"
        matches = extract_pattern_from_text(
            SAMPLE_TEXTS["custom_pattern"],
            custom_pattern,
            extract_all=False
        )

        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        assert matches[0]['value'] == "PROD-12345", \
            f"Expected 'PROD-12345', got '{matches[0]['value']}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Custom Regex Pattern",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Extracted: {matches[0]['value']}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Custom Regex Pattern",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 6: Email Validation (Valid and Invalid)
# ============================================================================
def test_email_validation() -> TestResult:
    """Test email validation function."""
    start_time = time.time()

    try:
        # Test valid email
        is_valid, msg = validate_email(VALIDATION_SAMPLES["valid_email"])
        assert is_valid == True, f"Valid email failed: {msg}"

        # Test invalid email (no @)
        is_valid, msg = validate_email(VALIDATION_SAMPLES["invalid_email_no_at"])
        assert is_valid == False, "Invalid email (no @) should fail"

        # Test invalid email (no domain)
        is_valid, msg = validate_email(VALIDATION_SAMPLES["invalid_email_no_domain"])
        assert is_valid == False, "Invalid email (no domain) should fail"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Validation",
            success=True,
            time_ms=elapsed_ms,
            result_data="Valid/Invalid cases handled correctly"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Validation",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 7: Phone Validation
# ============================================================================
def test_phone_validation() -> TestResult:
    """Test phone number validation function."""
    start_time = time.time()

    try:
        # Test valid phone (formatted)
        is_valid, msg = validate_phone(VALIDATION_SAMPLES["valid_phone"])
        assert is_valid == True, f"Valid phone failed: {msg}"

        # Test valid phone (dashes)
        is_valid, msg = validate_phone(VALIDATION_SAMPLES["valid_phone_dashes"])
        assert is_valid == True, f"Valid phone (dashes) failed: {msg}"

        # Test invalid phone (too short)
        is_valid, msg = validate_phone(VALIDATION_SAMPLES["invalid_phone_short"])
        assert is_valid == False, "Invalid phone (too short) should fail"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Validation",
            success=True,
            time_ms=elapsed_ms,
            result_data="Valid/Invalid cases handled correctly"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Validation",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 8: URL Validation
# ============================================================================
def test_url_validation() -> TestResult:
    """Test URL validation function."""
    start_time = time.time()

    try:
        # Test valid URL
        is_valid, msg = validate_url(VALIDATION_SAMPLES["valid_url"])
        assert is_valid == True, f"Valid URL failed: {msg}"

        # Test invalid URL (no protocol)
        is_valid, msg = validate_url(VALIDATION_SAMPLES["invalid_url_no_protocol"])
        assert is_valid == False, "Invalid URL (no protocol) should fail"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Validation",
            success=True,
            time_ms=elapsed_ms,
            result_data="Valid/Invalid cases handled correctly"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Validation",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 9: SSN Validation
# ============================================================================
def test_ssn_validation() -> TestResult:
    """Test SSN validation function."""
    start_time = time.time()

    try:
        # Test valid SSN
        is_valid, msg = validate_ssn(VALIDATION_SAMPLES["valid_ssn"])
        assert is_valid == True, f"Valid SSN failed: {msg}"

        # Test invalid SSN (starts with 666)
        is_valid, msg = validate_ssn(VALIDATION_SAMPLES["invalid_ssn_666"])
        assert is_valid == False, "Invalid SSN (666) should fail"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="SSN Validation",
            success=True,
            time_ms=elapsed_ms,
            result_data="Valid/Invalid cases handled correctly"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="SSN Validation",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 10: Credit Card Validation (Luhn Algorithm)
# ============================================================================
def test_credit_card_validation() -> TestResult:
    """Test credit card validation with Luhn algorithm."""
    start_time = time.time()

    try:
        # Test valid credit card (passes Luhn check)
        is_valid, msg = validate_credit_card(VALIDATION_SAMPLES["valid_credit_card_visa"])
        assert is_valid == True, f"Valid credit card failed: {msg}"
        assert "Visa" in msg, "Should identify as Visa card"

        # Test invalid credit card (fails Luhn check)
        is_valid, msg = validate_credit_card(VALIDATION_SAMPLES["invalid_credit_card_luhn"])
        assert is_valid == False, "Invalid credit card (Luhn) should fail"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Credit Card Validation (Luhn)",
            success=True,
            time_ms=elapsed_ms,
            result_data="Valid/Invalid cases + Luhn check work correctly"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Credit Card Validation (Luhn)",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 11: Email Normalization
# ============================================================================
def test_email_normalization() -> TestResult:
    """Test email normalization (lowercase, trim)."""
    start_time = time.time()

    try:
        normalized = normalize_email(NORMALIZATION_SAMPLES["email_mixed_case"])
        assert normalized == "john.doe@example.com", \
            f"Expected 'john.doe@example.com', got '{normalized}'"
        assert normalized.islower(), "Email should be lowercase"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Normalization",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Normalized: {normalized}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Email Normalization",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 12: Phone Normalization (E164 Format)
# ============================================================================
def test_phone_normalization() -> TestResult:
    """Test phone normalization to E164 format."""
    start_time = time.time()

    try:
        # Test formatted phone
        normalized = normalize_phone(NORMALIZATION_SAMPLES["phone_formatted"], format='E164')
        assert normalized == "+15551234567", \
            f"Expected '+15551234567', got '{normalized}'"

        # Test phone with dots
        normalized_dots = normalize_phone(NORMALIZATION_SAMPLES["phone_dots"], format='E164')
        assert normalized_dots == "+15551234567", \
            f"Expected '+15551234567', got '{normalized_dots}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Normalization (E164)",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Normalized: {normalized}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Phone Normalization (E164)",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 13: URL Normalization
# ============================================================================
def test_url_normalization() -> TestResult:
    """Test URL normalization (add protocol, lowercase domain)."""
    start_time = time.time()

    try:
        # Test URL without protocol
        normalized = normalize_url(NORMALIZATION_SAMPLES["url_no_protocol"])
        assert normalized.startswith("https://"), "Should add https:// protocol"
        assert "example.com" in normalized.lower(), "Should contain example.com"

        # Test URL with mixed case
        normalized_case = normalize_url(NORMALIZATION_SAMPLES["url_mixed_case"])
        assert "example.com" in normalized_case.lower(), "Should contain example.com"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Normalization",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Normalized: {normalized}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="URL Normalization",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 14: Date Normalization (ISO 8601)
# ============================================================================
def test_date_normalization() -> TestResult:
    """Test date normalization to ISO 8601 format."""
    start_time = time.time()

    try:
        # Test US format date
        normalized = normalize_date(NORMALIZATION_SAMPLES["date_us_format"], format='ISO8601')
        assert normalized == "2025-01-15", \
            f"Expected '2025-01-15', got '{normalized}'"

        # Test ISO format date (should remain the same)
        normalized_iso = normalize_date(NORMALIZATION_SAMPLES["date_iso_format"], format='ISO8601')
        assert normalized_iso == "2025-01-15", \
            f"Expected '2025-01-15', got '{normalized_iso}'"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Date Normalization (ISO 8601)",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Normalized: {normalized}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Date Normalization (ISO 8601)",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# TEST 15: Extract All vs Single Match
# ============================================================================
def test_extract_all_vs_single() -> TestResult:
    """Test extracting all matches vs single match."""
    start_time = time.time()

    try:
        pattern = get_predefined_pattern("email")

        # Extract single match
        single = extract_pattern_from_text(
            SAMPLE_TEXTS["email_multiple"],
            pattern,
            extract_all=False
        )
        assert len(single) == 1, f"Single extract should return 1 match, got {len(single)}"

        # Extract all matches
        all_matches = extract_pattern_from_text(
            SAMPLE_TEXTS["email_multiple"],
            pattern,
            extract_all=True
        )
        assert len(all_matches) >= 2, f"Should extract 2+ emails, got {len(all_matches)}"

        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Extract All vs Single Match",
            success=True,
            time_ms=elapsed_ms,
            result_data=f"Single: 1, All: {len(all_matches)}"
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return TestResult(
            name="Extract All vs Single Match",
            success=False,
            time_ms=elapsed_ms,
            error=str(e)
        )


# ============================================================================
# Main Test Runner
# ============================================================================
def run_all_tests():
    """Run all test cases and display results."""
    print("=" * 80)
    print("PATTERN EXTRACTION HELPER FUNCTIONS TESTS")
    print("=" * 80)
    print()

    # Define all tests
    tests = [
        ("1. Email Pattern Extraction", test_email_extraction),
        ("2. Phone Pattern Extraction", test_phone_extraction),
        ("3. URL Pattern Extraction", test_url_extraction),
        ("4. Date Pattern Extraction", test_date_extraction),
        ("5. Custom Regex Pattern", test_custom_pattern),
        ("6. Email Validation", test_email_validation),
        ("7. Phone Validation", test_phone_validation),
        ("8. URL Validation", test_url_validation),
        ("9. SSN Validation", test_ssn_validation),
        ("10. Credit Card Validation (Luhn)", test_credit_card_validation),
        ("11. Email Normalization", test_email_normalization),
        ("12. Phone Normalization (E164)", test_phone_normalization),
        ("13. URL Normalization", test_url_normalization),
        ("14. Date Normalization (ISO 8601)", test_date_normalization),
        ("15. Extract All vs Single Match", test_extract_all_vs_single),
    ]

    results = []

    # Run each test
    for test_name, test_func in tests:
        print(f"Testing: {test_name}")
        print("-" * 80)

        result = test_func()
        results.append(result)

        if result.success:
            print(f"[PASS] ({result.time_ms:.2f}ms)")
            if result.result_data:
                print(f"Result: {result.result_data}")
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
                error_preview = result.error[:100] + "..." if len(result.error) > 100 else result.error
                print(f"    Error: {error_preview}")
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
    print(f"  Total Time: {total_time:.2f}ms ({total_time/1000:.3f}s)")
    print(f"  Average Time per Test: {avg_time:.2f}ms")
    print(f"  Fastest Test: {min(results, key=lambda r: r.time_ms).name} ({min(r.time_ms for r in results):.2f}ms)")
    print(f"  Slowest Test: {max(results, key=lambda r: r.time_ms).name} ({max(r.time_ms for r in results):.2f}ms)")

    print("\n" + "=" * 80)

    if failed == 0:
        print("*** ALL TESTS PASSED! ***")
        print("The pattern extraction helper functions work correctly for all tested patterns.")
    else:
        print(f"WARNING: {failed} test(s) failed. Please review the errors above.")

    print("=" * 80)

    return results


if __name__ == "__main__":
    results = run_all_tests()

    # Exit with error code if any tests failed
    import sys
    failed_count = sum(1 for r in results if not r.success)
    sys.exit(1 if failed_count > 0 else 0)
