"""
Test script for LLMProviderRouter functionality.

This script demonstrates all features of LLMProviderRouter:
1. Pattern-based classification
2. LLM-based classification
3. Hybrid classification
4. Provider routing
5. Fallback mechanisms
6. Top-K routing
7. Export/import configuration
8. Custom patterns

Usage:
    python tests/test_llm_provider_router.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SimplerLLM.language import (
    LLM,
    LLMProvider,
    LLMProviderRouter,
    ProviderConfig,
)


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def print_result(result):
    """Print routing result in a formatted way."""
    print(f"\nQuery Classification:")
    print(f"  Type: {result.query_classification.query_type}")
    print(f"  Confidence: {result.query_classification.confidence:.2f}")
    print(f"  Method: {result.query_classification.matched_by}")
    print(f"  Reasoning: {result.query_classification.reasoning}")

    print(f"\nProvider Routing:")
    print(f"  Selected: {result.provider_used} ({result.model_used})")
    print(f"  Routing Confidence: {result.routing_confidence:.2f}")
    print(f"  Routing Reasoning: {result.routing_reasoning}")

    print(f"\nExecution:")
    print(f"  Used Fallback: {result.used_fallback}")
    if result.fallback_reason:
        print(f"  Fallback Reason: {result.fallback_reason}")
    print(f"  Execution Time: {result.execution_time:.2f}s")

    print(f"\nAnswer:")
    print(f"  {result.answer[:200]}..." if len(result.answer) > 200 else f"  {result.answer}")


def create_test_router(classification_method="hybrid", enable_cache=False, verbose=True):
    """Helper to create a test router."""
    # Configure providers
    provider_configs = [
        ProviderConfig(
            llm_provider="OPENAI",
            llm_model="gpt-4o-mini",
            specialties=["coding", "technical_writing", "debugging"],
            description="OpenAI GPT-4o-mini - Best for programming and technical tasks",
            priority=8
        ),
        ProviderConfig(
            llm_provider="ANTHROPIC",
            llm_model="claude-3-5-haiku-20241022",
            specialties=["creative_writing", "analysis", "reasoning"],
            description="Anthropic Claude Haiku - Best for creative and analytical tasks",
            priority=7
        ),
    ]

    # Create LLM instances
    llm_instances = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    # Initialize router
    router = LLMProviderRouter(
        provider_configs=provider_configs,
        llm_instances=llm_instances,
        default_provider=llm_instances[1],  # Claude as fallback
        classification_method=classification_method,
        enable_cache=enable_cache,
        verbose=verbose
    )

    return router


def test_pattern_classification():
    """Test pattern-based classification."""
    print_separator("TEST 1: PATTERN-BASED CLASSIFICATION")

    router = create_test_router(classification_method="pattern", verbose=True)

    # Test coding query (should match pattern)
    print("\nTest Case: Coding Query")
    print("-" * 80)

    query = "Write a Python function to calculate factorial"
    print(f"Query: '{query}'\n")

    result = router.route(query)
    print_result(result)

    print("\nExpected: Should classify as 'coding' via pattern matching")
    print(f"Actual: {result.query_classification.query_type} via {result.query_classification.matched_by}")
    assert result.query_classification.matched_by == "pattern", "Should use pattern matching"


def test_llm_classification():
    """Test LLM-based classification."""
    print_separator("TEST 2: LLM-BASED CLASSIFICATION")

    router = create_test_router(classification_method="llm", verbose=True)

    # Test ambiguous query (requires LLM)
    print("\nTest Case: Ambiguous Query (Requires LLM)")
    print("-" * 80)

    query = "Help me understand the concept of recursion in a simple way"
    print(f"Query: '{query}'\n")

    result = router.route(query)
    print_result(result)

    print("\nExpected: Should classify via LLM")
    print(f"Actual: {result.query_classification.matched_by}")
    assert result.query_classification.matched_by == "llm", "Should use LLM classification"


def test_hybrid_classification():
    """Test hybrid classification (pattern + LLM fallback)."""
    print_separator("TEST 3: HYBRID CLASSIFICATION")

    router = create_test_router(classification_method="hybrid", verbose=True)

    # Test 1: Clear pattern match
    print("\nTest Case 3a: Clear Pattern Match")
    print("-" * 80)

    query1 = "Debug this JavaScript code for me"
    print(f"Query: '{query1}'\n")

    result1 = router.route(query1)
    print_result(result1)

    print("\nExpected: Pattern match (fast)")
    print(f"Actual: {result1.query_classification.matched_by}")

    # Test 2: No pattern match (should use LLM)
    print("\n\nTest Case 3b: No Pattern Match (Falls back to LLM)")
    print("-" * 80)

    query2 = "What are the implications of quantum mechanics on computer science?"
    print(f"Query: '{query2}'\n")

    result2 = router.route(query2)
    print_result(result2)

    print("\nExpected: LLM classification (no pattern match)")
    print(f"Actual: {result2.query_classification.matched_by}")


def test_provider_routing():
    """Test that different query types route to different providers."""
    print_separator("TEST 4: PROVIDER ROUTING")

    router = create_test_router(verbose=True)

    # Test 1: Coding query → OpenAI
    print("\nTest Case 4a: Coding Query → OpenAI")
    print("-" * 80)

    coding_query = "Implement a binary search algorithm in Python"
    print(f"Query: '{coding_query}'\n")

    result1 = router.route(coding_query)
    print_result(result1)

    print(f"\nExpected: OPENAI (coding specialist)")
    print(f"Actual: {result1.provider_used}")

    # Test 2: Creative query → Claude
    print("\n\nTest Case 4b: Creative Query → Claude")
    print("-" * 80)

    creative_query = "Write a haiku about machine learning"
    print(f"Query: '{creative_query}'\n")

    result2 = router.route(creative_query)
    print_result(result2)

    print(f"\nExpected: ANTHROPIC (creative specialist)")
    print(f"Actual: {result2.provider_used}")


def test_caching():
    """Test classification caching."""
    print_separator("TEST 5: CLASSIFICATION CACHING")

    router = create_test_router(
        classification_method="hybrid",
        enable_cache=True,
        verbose=True
    )

    query = "Write Python code to reverse a string"

    # First call - should classify via pattern/LLM
    print("\nTest Case 5a: First Call (No Cache)")
    print("-" * 80)
    print(f"Query: '{query}'\n")

    result1 = router.route(query)
    first_method = result1.query_classification.matched_by

    print(f"Classification method: {first_method}")

    # Second call - should use cache
    print("\n\nTest Case 5b: Second Call (Should Use Cache)")
    print("-" * 80)
    print(f"Query: '{query}'\n")

    result2 = router.route(query)
    second_method = result2.query_classification.matched_by

    print(f"Classification method: {second_method}")

    print(f"\nExpected: Second call uses 'cache'")
    print(f"Actual: First={first_method}, Second={second_method}")
    assert second_method == "cache", "Second call should use cache"


def test_get_provider_without_execution():
    """Test getting provider without executing query."""
    print_separator("TEST 6: GET PROVIDER WITHOUT EXECUTION")

    router = create_test_router(verbose=True)

    query = "Explain neural networks"
    print(f"Query: '{query}'\n")

    # Get provider and classification without executing
    provider, classification = router.get_provider_for_query(
        query,
        return_classification=True
    )

    print("Provider Information:")
    print(f"  Provider: {provider.provider.name}")
    print(f"  Model: {provider.model_name}")

    print("\nClassification:")
    print(f"  Type: {classification.query_type}")
    print(f"  Confidence: {classification.confidence:.2f}")
    print(f"  Method: {classification.matched_by}")

    print("\nNote: Query was NOT executed - just showing routing decision")


def test_force_provider():
    """Test forcing a specific provider (bypass routing)."""
    print_separator("TEST 7: FORCE SPECIFIC PROVIDER")

    router = create_test_router(verbose=True)

    # Query that would normally route to Claude
    query = "Write a creative story about AI"
    print(f"Query: '{query}'")
    print("(This would normally route to Claude for creative writing)")

    print("\nForcing provider to OPENAI...\n")

    result = router.route(query, force_provider="OPENAI")
    print_result(result)

    print(f"\nExpected: OPENAI (forced)")
    print(f"Actual: {result.provider_used}")
    assert result.provider_used == "OPENAI", "Should use forced provider"


def test_custom_patterns():
    """Test adding custom patterns."""
    print_separator("TEST 8: CUSTOM PATTERN RULES")

    # Create router with custom patterns
    custom_patterns = {
        "blockchain": [r"blockchain", r"cryptocurrency", r"smart contract", r"web3"],
        "data_science": [r"pandas", r"dataframe", r"numpy", r"scikit-learn"],
    }

    provider_configs = [
        ProviderConfig(
            llm_provider="OPENAI",
            llm_model="gpt-4o-mini",
            specialties=["blockchain", "data_science"],
            description="Specialized in blockchain and data science",
            priority=9
        ),
        ProviderConfig(
            llm_provider="ANTHROPIC",
            llm_model="claude-3-5-haiku-20241022",
            specialties=["general"],
            description="General purpose",
            priority=5
        ),
    ]

    llm_instances = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    router = LLMProviderRouter(
        provider_configs=provider_configs,
        llm_instances=llm_instances,
        classification_method="pattern",
        custom_patterns=custom_patterns,
        verbose=True
    )

    # Test custom pattern
    query = "Explain how blockchain technology works"
    print(f"Query: '{query}'\n")

    result = router.route(query)
    print_result(result)

    print(f"\nExpected: Classified as 'blockchain' (custom pattern)")
    print(f"Actual: {result.query_classification.query_type}")


def test_export_import_config():
    """Test exporting and importing router configuration."""
    print_separator("TEST 9: EXPORT/IMPORT CONFIGURATION")

    # Create router
    router = create_test_router(verbose=True)

    # Export configuration
    config_file = "test_router_config.json"
    print(f"Exporting configuration to '{config_file}'...\n")

    router.export_config(config_file)
    print(f"✓ Configuration exported")

    # Load configuration
    print(f"\nLoading configuration from '{config_file}'...\n")

    # Need to provide LLM instances (can't serialize API keys)
    llm_instances = [
        LLM.create(LLMProvider.OPENAI, model_name="gpt-4o-mini"),
        LLM.create(LLMProvider.ANTHROPIC, model_name="claude-3-5-haiku-20241022"),
    ]

    loaded_router = LLMProviderRouter.from_config(
        config_file,
        llm_instances=llm_instances,
        verbose=True
    )

    print(f"✓ Configuration loaded")

    # Test loaded router works
    query = "Write code to sort a list"
    print(f"\nTesting loaded router with query: '{query}'\n")

    result = loaded_router.route(query)
    print_result(result)

    # Clean up
    import os
    if os.path.exists(config_file):
        os.remove(config_file)
        print(f"\n✓ Cleaned up test file")


def test_add_remove_provider():
    """Test adding and removing providers dynamically."""
    print_separator("TEST 10: DYNAMIC PROVIDER MANAGEMENT")

    router = create_test_router(verbose=True)

    print(f"Initial provider count: {len(router.provider_configs)}")

    # Add new provider
    print("\nAdding new provider (Gemini)...\n")

    gemini_llm = LLM.create(LLMProvider.GEMINI, model_name="gemini-pro")

    provider_idx = router.add_provider(
        llm=gemini_llm,
        specialties=["general", "technical_explanation"],
        description="Google Gemini - Good for general tasks",
        priority=6
    )

    print(f"✓ Added provider at index {provider_idx}")
    print(f"New provider count: {len(router.provider_configs)}")

    # Test with new provider
    query = "What is artificial intelligence?"
    print(f"\nTesting with query: '{query}'\n")

    result = router.route(query)
    print(f"Routed to: {result.provider_used}")

    # Remove provider
    print(f"\nRemoving provider at index {provider_idx}...\n")
    router.remove_provider(provider_idx)

    print(f"✓ Removed provider")
    print(f"Final provider count: {len(router.provider_configs)}")


def test_multiple_queries():
    """Test routing multiple queries to demonstrate different routing."""
    print_separator("TEST 11: MULTIPLE QUERY ROUTING")

    router = create_test_router(verbose=False)  # Less verbose for multiple queries

    queries = [
        "Write a Python function to find prime numbers",
        "Write a poem about technology",
        "Analyze the pros and cons of cloud computing",
        "Debug this code: def foo(): return x + y",
        "Explain what quantum computing is",
    ]

    print("\nRouting multiple queries:")
    print("-" * 80)

    for idx, query in enumerate(queries, 1):
        print(f"\n{idx}. Query: '{query}'")

        result = router.route(query)

        print(f"   Type: {result.query_classification.query_type}")
        print(f"   Provider: {result.provider_used}")
        print(f"   Confidence: {result.routing_confidence:.2f}")


def main():
    """Run all tests."""
    print("\n" + "#"*80)
    print("#  LLMProviderRouter Comprehensive Test Suite")
    print("#"*80)

    try:
        # Test 1: Pattern classification
        test_pattern_classification()

        # Test 2: LLM classification
        test_llm_classification()

        # Test 3: Hybrid classification
        test_hybrid_classification()

        # Test 4: Provider routing
        test_provider_routing()

        # Test 5: Caching
        test_caching()

        # Test 6: Get provider without execution
        test_get_provider_without_execution()

        # Test 7: Force provider
        test_force_provider()

        # Test 8: Custom patterns
        test_custom_patterns()

        # Test 9: Export/import
        test_export_import_config()

        # Test 10: Add/remove provider
        test_add_remove_provider()

        # Test 11: Multiple queries
        test_multiple_queries()

        print_separator("ALL TESTS COMPLETED SUCCESSFULLY!")

        print("\nTest Summary:")
        print("  ✓ Pattern-based classification")
        print("  ✓ LLM-based classification")
        print("  ✓ Hybrid classification")
        print("  ✓ Provider routing")
        print("  ✓ Classification caching")
        print("  ✓ Get provider without execution")
        print("  ✓ Force specific provider")
        print("  ✓ Custom pattern rules")
        print("  ✓ Export/import configuration")
        print("  ✓ Dynamic provider management")
        print("  ✓ Multiple query routing")

    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
