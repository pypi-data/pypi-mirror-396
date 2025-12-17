from SimplerLLM.language.llm import LLM, LLMProvider

# Create Perplexity LLM instance
# Perplexity has built-in web search by default!
llm = LLM.create(
    provider=LLMProvider.PERPLEXITY,
    model_name="sonar"  # Options: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro
)

# Simple query - web search happens automatically
response = llm.generate_response(
    prompt="What are the latest AI news today?",
    max_tokens=1000,
    full_response=True  # Get web_sources with citations
)

print("=== Perplexity Response ===\n")
print(response.generated_text)

print("\n=== Web Sources ===")
if response.web_sources:
    for source in response.web_sources:
        print(f"- {source.get('title', 'N/A')}")
        print(f"  URL: {source.get('url', 'N/A')}")
        print(f"  Date: {source.get('date', 'N/A')}\n")
else:
    print("No web sources returned")

print(f"\n=== Usage ===")
print(f"Input tokens: {response.input_token_count}")
print(f"Output tokens: {response.output_token_count}")
print(f"Process time: {response.process_time:.2f}s")
