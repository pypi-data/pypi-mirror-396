from pydantic import BaseModel
from typing import List
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm_addons import generate_pydantic_json_model

# Define Pydantic model for AI news
class AINewsItem(BaseModel):
    title: str
    summary: str

class AINewsList(BaseModel):
    news: List[AINewsItem]

# Create Anthropic LLM instance
llm = LLM.create(
    provider=LLMProvider.ANTHROPIC,
    model_name="claude-sonnet-4-5-20250514"
)

# Generate pydantic model with web search
result = generate_pydantic_json_model(
    model_class=AINewsList,
    prompt="""Search the web and find the top 5 latest AI news stories from today.

IMPORTANT: Return ONLY a single JSON object with a "news" array containing the stories.
Each story should have "title" and "summary" fields ONLY (no source field).

Example output format:
{"news": [{"title": "Story 1", "summary": "Brief summary"}, {"title": "Story 2", "summary": "Brief summary"}]}""",
    llm_instance=llm,
    max_tokens=2000,
    web_search=True,
    full_response=True  # To also get web_sources
)

# Print results
if isinstance(result, str):
    print(f"Error: {result}")
else:
    print("=== AI News (from Anthropic with Web Search) ===\n")
    for i, news in enumerate(result.model_object.news, 1):
        print(f"{i}. {news.title}")
        print(f"   Summary: {news.summary}\n")

    # Print actual web sources from API response
    if result.web_sources:
        print("=== Sources (from Anthropic web search) ===")
        for source in result.web_sources:
            print(f"- {source.get('title', 'N/A')}")
            print(f"  {source.get('url', 'N/A')}")
            if source.get('cited_text'):
                print(f"  Cited: {source.get('cited_text')[:100]}...")
            print()
