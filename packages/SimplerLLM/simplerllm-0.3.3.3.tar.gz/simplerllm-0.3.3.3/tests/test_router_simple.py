"""
Simple test script for demonstrating SimplerLLM's LLM Router feature.

This script showcases various routing capabilities:
1. Basic routing - select single best match
2. Top-K routing - get multiple best matches
3. Metadata filtering - route with constraints
4. Confidence thresholding - filter by confidence scores
5. Custom prompt templates - customize routing logic
"""

from SimplerLLM.language.llm_router import LLMRouter
from SimplerLLM.language.llm import LLM, LLMProvider


def print_separator(title):
    """Print a formatted separator for better output readability"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_basic_routing(llm_instance):
    """Test 1: Basic routing - selecting the best match"""
    print_separator("TEST 1: Basic Routing")

    # Create router instance
    router = LLMRouter(llm_instance=llm_instance, confidence_threshold=0.5)

    # Add choices
    choices = [
        ("Python Programming Tutorial", {"category": "programming", "difficulty": "beginner"}),
        ("Machine Learning Basics", {"category": "ai", "difficulty": "intermediate"}),
        ("Web Development with Django", {"category": "web", "difficulty": "intermediate"}),
        ("Advanced Deep Learning", {"category": "ai", "difficulty": "advanced"}),
        ("JavaScript for Beginners", {"category": "programming", "difficulty": "beginner"}),
    ]

    router.add_choices(choices)

    # Test routing
    user_query = "I want to learn AI and machine learning from scratch"
    print(f"User Query: {user_query}")
    print("\nAvailable Choices:")
    for i, (content, metadata) in enumerate(choices):
        print(f"  {i}. {content} - {metadata}")

    # Get best match
    result = router.route(user_query)

    if result:
        choice_content, metadata = router.get_choice(result.selected_index)
        print(f"\nSelected Choice: {choice_content}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Metadata: {metadata}")
    else:
        print("No match found above confidence threshold")


def test_top_k_routing(llm_instance):
    """Test 2: Top-K routing - get multiple best matches"""
    print_separator("TEST 2: Top-K Routing")

    # Create router
    router = LLMRouter(llm_instance=llm_instance, confidence_threshold=0.4)

    # Add product choices
    products = [
        ("Gaming Laptop - High Performance", {"type": "laptop", "price_range": "high", "use_case": "gaming"}),
        ("Business Laptop - Professional", {"type": "laptop", "price_range": "medium", "use_case": "business"}),
        ("Budget Laptop - Student Friendly", {"type": "laptop", "price_range": "low", "use_case": "student"}),
        ("Ultrabook - Portable and Light", {"type": "laptop", "price_range": "high", "use_case": "travel"}),
        ("Workstation - Content Creation", {"type": "laptop", "price_range": "high", "use_case": "creative"}),
        ("2-in-1 Laptop Tablet Hybrid", {"type": "laptop", "price_range": "medium", "use_case": "versatile"}),
    ]

    router.add_choices(products)

    user_query = "I need a powerful laptop for video editing and graphic design"
    print(f"User Query: {user_query}")
    print("\nGetting Top 3 Recommendations...")

    # Get top 3 matches
    top_results = router.route_top_k(user_query, k=3)

    if top_results:
        print(f"\nFound {len(top_results)} recommendations:\n")
        for i, result in enumerate(top_results, 1):
            choice_content, metadata = router.get_choice(result.selected_index)
            print(f"Recommendation #{i}:")
            print(f"  Product: {choice_content}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            print(f"  Reasoning: {result.reasoning}")
            print(f"  Metadata: {metadata}")
            print()
    else:
        print("No matches found above confidence threshold")


def test_metadata_filtering(llm_instance):
    """Test 3: Routing with metadata filtering"""
    print_separator("TEST 3: Metadata Filtering")

    # Create router
    router = LLMRouter(llm_instance=llm_instance, confidence_threshold=0.5)

    # Add tutorial choices with detailed metadata
    tutorials = [
        ("Python Basics Tutorial", {"language": "python", "difficulty": "beginner", "duration": "short"}),
        ("Advanced Python Patterns", {"language": "python", "difficulty": "advanced", "duration": "long"}),
        ("JavaScript Fundamentals", {"language": "javascript", "difficulty": "beginner", "duration": "medium"}),
        ("React Advanced Concepts", {"language": "javascript", "difficulty": "advanced", "duration": "long"}),
        ("Python Data Science Intro", {"language": "python", "difficulty": "intermediate", "duration": "medium"}),
        ("Python Web Scraping", {"language": "python", "difficulty": "intermediate", "duration": "short"}),
    ]

    router.add_choices(tutorials)

    user_query = "I want to learn web scraping"
    metadata_filter = {"language": "python", "difficulty": "intermediate"}

    print(f"User Query: {user_query}")
    print(f"Metadata Filter: {metadata_filter}")
    print("\nFiltered Choices:")

    # Show what choices match the filter
    filtered = [t for t in tutorials if all(t[1].get(k) == v for k, v in metadata_filter.items())]
    for content, metadata in filtered:
        print(f"  - {content}: {metadata}")

    # Route with metadata filter
    result = router.route_with_metadata(user_query, metadata_filter)

    if result:
        choice_content, metadata = router.get_choice(result.selected_index)
        print(f"\nSelected Tutorial: {choice_content}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Reasoning: {result.reasoning}")
    else:
        print("\nNo match found above confidence threshold")


def test_confidence_threshold(llm_instance):
    """Test 4: Different confidence thresholds"""
    print_separator("TEST 4: Confidence Threshold Testing")

    choices = [
        ("Italian Restaurant - Pizza & Pasta", {"cuisine": "italian", "price": "medium"}),
        ("Japanese Sushi Bar", {"cuisine": "japanese", "price": "high"}),
        ("Mexican Taco Place", {"cuisine": "mexican", "price": "low"}),
        ("French Fine Dining", {"cuisine": "french", "price": "high"}),
        ("American Burger Joint", {"cuisine": "american", "price": "low"}),
    ]

    user_query = "I want authentic Asian food experience"

    print(f"User Query: {user_query}\n")

    # Test with different thresholds
    thresholds = [0.3, 0.5, 0.7]

    for threshold in thresholds:
        print(f"Testing with confidence threshold: {threshold}")
        router = LLMRouter(llm_instance=llm_instance, confidence_threshold=threshold)
        router.add_choices(choices)

        result = router.route(user_query)

        if result:
            choice_content, _ = router.get_choice(result.selected_index)
            print(f"  ✓ Match Found: {choice_content}")
            print(f"  Confidence: {result.confidence_score:.2f}")
        else:
            print(f"  ✗ No match above threshold {threshold}")
        print()


def test_multiple_queries(llm_instance):
    """Test 5: Multiple queries against same router"""
    print_separator("TEST 5: Multiple Queries with Same Router")

    # Create router with content types
    router = LLMRouter(llm_instance=llm_instance, confidence_threshold=0.5)

    content_types = [
        ("Beginner Tutorial Article", {"type": "tutorial", "level": "beginner"}),
        ("Advanced Technical Guide", {"type": "guide", "level": "advanced"}),
        ("Quick Reference Cheatsheet", {"type": "reference", "level": "all"}),
        ("Video Course Series", {"type": "video", "level": "intermediate"}),
        ("Interactive Coding Challenge", {"type": "interactive", "level": "intermediate"}),
    ]

    router.add_choices(content_types)

    # Test multiple user queries
    queries = [
        "I'm completely new and need step-by-step instructions",
        "Show me a quick syntax reference",
        "I want hands-on practice problems",
    ]

    for query in queries:
        print(f"Query: {query}")
        result = router.route(query)

        if result:
            choice_content, _ = router.get_choice(result.selected_index)
            print(f"  → Recommended: {choice_content}")
            print(f"  → Confidence: {result.confidence_score:.2f}")
        else:
            print("  → No match found")
        print()


def main():
    """Main function to run all tests"""
    print("\n" + "🚀" * 40)
    print("SimplerLLM - LLM Router Feature Test Suite")
    print("🚀" * 40)

    # Initialize LLM (using gpt-4o-mini for cost efficiency)
    print("\nInitializing LLM instance...")
    try:
        llm_instance = LLM.create(provider=LLMProvider.OPENAI, model_name="gpt-4o-mini")
        print("✓ LLM instance created successfully")
    except Exception as e:
        print(f"✗ Failed to create LLM instance: {e}")
        print("\nMake sure you have set your OPENAI_API_KEY in your .env file")
        return

    # Run all tests
    try:
        test_basic_routing(llm_instance)
        test_top_k_routing(llm_instance)
        test_metadata_filtering(llm_instance)
        test_confidence_threshold(llm_instance)
        test_multiple_queries(llm_instance)

        print_separator("All Tests Completed Successfully! ✓")

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
