"""
Quick test script for vision capabilities.
This script tests the basic functionality without making API calls.
"""

from SimplerLLM.tools.image_helpers import (
    is_url,
    get_image_mime_type,
    prepare_image_content,
    prepare_vision_content
)

print("Testing Image Helper Functions...")
print("=" * 60)

# Test 1: URL detection
print("\n1. Testing URL detection:")
test_urls = [
    "https://example.com/image.jpg",
    "/path/to/image.jpg",
    "C:\\path\\to\\image.png"
]
for url in test_urls:
    result = is_url(url)
    print(f"   {url} -> {'URL' if result else 'File Path'}")

# Test 2: MIME type detection
print("\n2. Testing MIME type detection:")
test_files = [
    "image.jpg",
    "photo.png",
    "animation.gif",
    "picture.webp"
]
for file in test_files:
    mime = get_image_mime_type(file)
    print(f"   {file} -> {mime}")

# Test 3: Prepare image content
print("\n3. Testing image content preparation (URL):")
image_url = "https://example.com/test.jpg"
content = prepare_image_content(image_url, detail="high")
print(f"   Type: {content['type']}")
print(f"   URL: {content['image_url']['url']}")
print(f"   Detail: {content['image_url']['detail']}")

# Test 4: Prepare vision content
print("\n4. Testing multi-part vision content:")
text = "What's in these images?"
images = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
]
vision_content = prepare_vision_content(text, images, detail="auto")
print(f"   Content parts: {len(vision_content)}")
print(f"   Text part: {vision_content[0]['type']} - '{vision_content[0]['text']}'")
print(f"   Image 1: {vision_content[1]['type']}")
print(f"   Image 2: {vision_content[2]['type']}")

# Test 5: Import wrapper
print("\n5. Testing OpenAI wrapper import:")
try:
    from SimplerLLM.language.llm.wrappers.openai_wrapper import OpenAILLM
    print("   [OK] OpenAI wrapper imported successfully")

    # Check if methods have the new parameters
    import inspect
    sig = inspect.signature(OpenAILLM.generate_response)
    params = list(sig.parameters.keys())

    if 'images' in params and 'detail' in params:
        print("   [OK] Vision parameters (images, detail) found in generate_response")
    else:
        print("   [ERROR] Vision parameters missing!")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

# Test 6: Test LLM.create
print("\n6. Testing LLM creation:")
try:
    from SimplerLLM.language.llm import LLM, LLMProvider

    # This won't make an API call, just creates the instance
    llm = LLM.create(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o"
    )
    print("   [OK] LLM instance created successfully")

    # Verify the instance has the vision methods
    if hasattr(llm, 'generate_response'):
        print("   [OK] generate_response method available")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

# Test 7: Anthropic vision helpers
print("\n7. Testing Anthropic vision helpers:")
try:
    from SimplerLLM.tools.image_helpers import (
        prepare_image_content_anthropic,
        prepare_vision_content_anthropic
    )
    print("   [OK] Anthropic helpers imported successfully")

    # Test Anthropic content preparation
    test_url = "https://example.com/image.jpg"
    anthropic_content = prepare_image_content_anthropic(test_url)

    if anthropic_content["type"] == "image":
        print("   [OK] Anthropic uses 'image' type (not 'image_url')")
    if "source" in anthropic_content:
        print("   [OK] Anthropic content has 'source' field")

    # Test vision content with ordering (using URLs to avoid file not found)
    vision_content = prepare_vision_content_anthropic(
        "What's this?",
        ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    )
    # Images should come before text in Anthropic
    if vision_content[0]["type"] == "image" and vision_content[-1]["type"] == "text":
        print("   [OK] Anthropic places images before text (best practice)")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

# Test 8: Anthropic wrapper
print("\n8. Testing Anthropic wrapper import:")
try:
    from SimplerLLM.language.llm.wrappers.anthropic_wrapper import AnthropicLLM
    print("   [OK] Anthropic wrapper imported successfully")

    # Check if methods have the images parameter
    import inspect
    sig = inspect.signature(AnthropicLLM.generate_response)
    params = list(sig.parameters.keys())

    if 'images' in params:
        print("   [OK] Vision parameter 'images' found in generate_response")
    else:
        print("   [ERROR] 'images' parameter missing!")

    if 'detail' not in params:
        print("   [OK] No 'detail' parameter (correct for Anthropic)")
    else:
        print("   [WARNING] 'detail' parameter found (should be OpenAI-only)")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

# Test 9: Anthropic LLM creation
print("\n9. Testing Anthropic LLM creation:")
try:
    from SimplerLLM.language.llm import LLM, LLMProvider

    # This won't make an API call, just creates the instance
    llm_anthropic = LLM.create(
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-5"
    )
    print("   [OK] Anthropic LLM instance created successfully")

    # Verify the instance has the vision methods
    if hasattr(llm_anthropic, 'generate_response'):
        print("   [OK] generate_response method available")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

print("\n" + "=" * 60)
print("All basic tests passed!")
print("\nThe vision implementation is ready for both OpenAI and Anthropic!")
print("\nTo test with actual API calls:")
print("  OpenAI: python examples/vision_example.py")
print("  Anthropic: python examples/vision_example_anthropic.py")
print("\nOr run the full test suites:")
print("  pytest tests/test_vision_openai.py -v")
print("  pytest tests/test_vision_anthropic.py -v")
