"""
Simple test script to verify LLM text generation works for all providers.
"""

from SimplerLLM.language.llm import LLM, LLMProvider


def test_provider(provider: LLMProvider, model_name: str, prompt: str):
    """Test a single LLM provider."""
    print(f"\n{'='*50}")
    print(f"Testing: {provider.name} ({model_name})")
    print('='*50)

    try:
        llm = LLM.create(provider=provider, model_name=model_name)

        response = llm.generate_response(
            prompt=prompt,
            max_tokens=100,
            full_response=True
        )

        print(f"Response: {response.generated_text}")
        print(f"Input tokens: {response.input_token_count}")
        print(f"Output tokens: {response.output_token_count}")
        print(f"Time: {response.process_time:.2f}s")
        print("Status: SUCCESS")
        return True

    except Exception as e:
        print(f"Error: {e}")
        print("Status: FAILED")
        return False


def main():
    print("SimplerLLM Provider Test Script")
    print("================================")

    test_prompt = "What is 2+2? Reply with just the number."

    providers = [
        (LLMProvider.OPENAI, "gpt-4o-mini"),
        (LLMProvider.ANTHROPIC, "claude-3-5-haiku-20241022"),
        (LLMProvider.GEMINI, "gemini-2.5-flash"),
        (LLMProvider.DEEPSEEK, "deepseek-chat"),
    ]

    results = {}

    for provider, model in providers:
        success = test_provider(provider, model, test_prompt)
        results[provider.name] = success

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print('='*50)
    for name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {name}: {status}")

    passed = sum(results.values())
    total = len(results)
    print(f"\nTotal: {passed}/{total} providers working")


if __name__ == "__main__":
    main()
