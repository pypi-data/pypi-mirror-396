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

# Create Perplexity LLM instance
# Perplexity has built-in web search by default!
llm = LLM.create(
    provider=LLMProvider.PERPLEXITY,
    model_name="sonar"  # Options: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro
)

# Generate pydantic model with web search (built-in for Perplexity)
result = generate_pydantic_json_model(
    model_class=AINewsList,
    prompt="""Search the web and find the top 5 latest AI news stories from today.

""",
    llm_instance=llm,
    max_tokens=2000,
    full_response=True  # To also get web_sources
)

# Print results
if isinstance(result, str):
    print(f"Error: {result}")
else:
    print("=== AI News (via Perplexity) ===\n")
    for i, news in enumerate(result.model_object.news, 1):
        print(f"{i}. {news.title}")
        print(f"   Summary: {news.summary}\n")

    # Print actual web sources from API response
    if result.web_sources:
        print("=== Sources (from Perplexity search) ===")
        for source in result.web_sources:
            print(f"- {source.get('title', 'N/A')}")
            print(f"  URL: {source.get('url', 'N/A')}")
            print(f"  Date: {source.get('date', 'N/A')}\n")
    else:
        print("No web sources returned")
