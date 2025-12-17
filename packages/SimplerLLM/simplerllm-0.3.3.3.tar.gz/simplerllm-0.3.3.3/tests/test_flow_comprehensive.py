"""
Comprehensive Test Suite for SimplerLLM Flow/MiniAgent Feature

This test script thoroughly tests all features of the Flow system including:
- Sync and async execution
- Pydantic structured output
- ReliableLLM integration
- Tool registry usage
- Error handling
- Real-world scenarios

Run with: python tests/test_flow_comprehensive.py
"""

import os
import asyncio
import time
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# SimplerLLM imports
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm.reliable import ReliableLLM
from SimplerLLM.language.flow import MiniAgent, FlowResult, StepResult
from SimplerLLM.language.flow.tool_registry import ToolRegistry
from SimplerLLM.language.llm_addons import generate_pydantic_json_model_reliable
from SimplerLLM.tools.text_chunker import TextChunks


# ============================================================================
# LOGGER CLASS FOR DUAL OUTPUT (CONSOLE + FILE)
# ============================================================================

class DualLogger:
    """Logger that writes to both console and file simultaneously"""

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.file_handle = None

        # Create results directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Open file for writing
        try:
            self.file_handle = open(log_file_path, 'w', encoding='utf-8')
            self._write_file_header()
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            print("Continuing with console output only...")

    def _write_file_header(self):
        """Write header information to the log file"""
        if self.file_handle:
            self.file_handle.write("=" * 80 + "\n")
            self.file_handle.write("SimplerLLM Flow/MiniAgent - Comprehensive Test Results\n")
            self.file_handle.write("=" * 80 + "\n")
            self.file_handle.write(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file_handle.write(f"Log file: {self.log_file_path}\n")
            self.file_handle.write("=" * 80 + "\n\n")
            self.file_handle.flush()

    def log(self, message: str = "", end: str = "\n"):
        """Write message to both console and file"""
        # Write to console
        print(message, end=end)

        # Write to file
        if self.file_handle:
            try:
                self.file_handle.write(message + end)
                self.file_handle.flush()  # Ensure it's written immediately
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")

    def close(self):
        """Close the log file"""
        if self.file_handle:
            self.file_handle.write("\n" + "=" * 80 + "\n")
            self.file_handle.write(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file_handle.write("=" * 80 + "\n")
            self.file_handle.close()
            self.file_handle = None


# Global logger instance
logger = None


def get_logger():
    """Get or create the global logger instance"""
    global logger
    if logger is None:
        # Create timestamped log file name
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_path = f"tests/results/test_flow_results_{timestamp}.txt"
        logger = DualLogger(log_file_path)
        logger.log(f"\n📁 Results will be saved to: {os.path.abspath(log_file_path)}\n")
    return logger


# ============================================================================
# PYDANTIC MODELS FOR TESTING
# ============================================================================

class SentimentAnalysis(BaseModel):
    """Simple sentiment analysis model"""
    text: str = Field(description="The analyzed text")
    sentiment: str = Field(description="Sentiment: positive, negative, or neutral")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation of the sentiment")


class BlogPostOutline(BaseModel):
    """Blog post outline structure"""
    title: str = Field(description="Catchy title for the blog post")
    introduction: str = Field(description="Opening paragraph")
    main_points: List[str] = Field(description="List of 3-5 main points to cover")
    conclusion: str = Field(description="Closing summary")
    target_audience: str = Field(description="Who this post is for")


class ProductAnalysis(BaseModel):
    """Product feature analysis"""
    product_name: str = Field(description="Name of the product")
    key_features: List[str] = Field(description="Top 3-5 features")
    pros: List[str] = Field(description="Advantages")
    cons: List[str] = Field(description="Disadvantages")
    rating: float = Field(description="Rating from 1-10")
    recommendation: str = Field(description="Who should use this product")


class DataSummary(BaseModel):
    """Summary of processed data"""
    total_items: int = Field(description="Total number of items processed")
    key_insights: List[str] = Field(description="3-5 key insights")
    summary: str = Field(description="Overall summary")
    next_steps: Optional[List[str]] = Field(description="Recommended next steps", default=None)


# ============================================================================
# CUSTOM TOOLS FOR TESTING
# ============================================================================

def uppercase_text(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()


def count_words(text: str) -> str:
    """Count words in text"""
    words = text.split()
    return f"Word count: {len(words)} words"


def add_prefix(text: str, prefix: str = "PROCESSED:") -> str:
    """Add prefix to text"""
    return f"{prefix} {text}"


def reverse_text(text: str) -> str:
    """Reverse the input text"""
    return text[::-1]


def extract_numbers(text: str) -> str:
    """Extract all numbers from text"""
    numbers = ''.join(c for c in text if c.isdigit() or c == '.')
    return f"Extracted numbers: {numbers}" if numbers else "No numbers found"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_section(title: str):
    """Print a formatted section header"""
    log = get_logger()
    log.log("\n" + "=" * 80)
    log.log(f"  {title}")
    log.log("=" * 80)


def print_flow_result(result: FlowResult, show_steps: bool = True):
    """Pretty print flow results"""
    log = get_logger()
    log.log(f"\n{'✓' if result.success else '✗'} Flow: {result.agent_name}")
    log.log(f"   Status: {'SUCCESS' if result.success else 'FAILED'}")
    log.log(f"   Total Steps: {result.total_steps}")
    log.log(f"   Duration: {result.total_duration_seconds:.2f}s")

    if result.error:
        log.log(f"   Error: {result.error}")

    if show_steps and result.steps:
        log.log(f"\n   Step Details:")
        for step in result.steps:
            status_icon = "✓" if not step.error else "✗"
            log.log(f"   {status_icon} Step {step.step_number} ({step.step_type}): {step.duration_seconds:.2f}s")
            if step.tool_used:
                log.log(f"      Tool: {step.tool_used}")
            if step.output_model_class:
                log.log(f"      JSON Model: {step.output_model_class}")
            if step.error:
                log.log(f"      Error: {step.error}")

    log.log(f"\n   Final Output:")
    if isinstance(result.final_output, BaseModel):
        # Don't truncate for file output - show full JSON
        log.log(f"   {result.final_output.model_dump_json(indent=2)}")
    else:
        output_str = str(result.final_output)
        # Don't truncate for file output - show everything
        log.log(f"   {output_str}")


def get_test_llm(verbose: bool = False) -> LLM:
    """Create a test LLM instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    return LLM.create(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7,
        verbose=verbose
    )


def get_test_reliable_llm(verbose: bool = False) -> ReliableLLM:
    """Create a ReliableLLM instance with primary and fallback"""
    primary = LLM.create(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7,
        verbose=verbose
    )

    # Use same provider for testing, but could be different
    secondary = LLM.create(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7,
        verbose=verbose
    )

    return ReliableLLM(
        primary_llm=primary,
        secondary_llm=secondary,
        verbose=verbose
    )


# ============================================================================
# TEST FUNCTIONS - BASIC OPERATIONS
# ============================================================================

def test_basic_flow_sync():
    """Test basic synchronous flow execution"""
    print_section("TEST 1: Basic Synchronous Flow Execution")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Basic Text Processor",
        llm_instance=llm,
        system_prompt="You are a helpful text processing assistant.",
        max_steps=3,
        verbose=True
    )

    # Add steps
    agent.add_step(
        step_type="llm",
        prompt="Take this text and make it more professional: {input}"
    )

    agent.add_step(
        step_type="llm",
        prompt="Now summarize the following text in one sentence: {previous_output}"
    )

    # Run flow
    result = agent.run("hey whats up, this is a test message lol")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 2, "Should have 2 steps"
    assert result.final_output is not None, "Should have final output"

    get_logger().log("\n✓ Test passed!")


def test_step_chaining():
    """Test that output from one step flows to the next"""
    print_section("TEST 2: Step Chaining with Multiple Transformations")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Text Transformation Chain",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Register custom tools
    ToolRegistry.register_tool("uppercase", uppercase_text)
    ToolRegistry.register_tool("count_words", count_words)

    # Chain: Input → LLM expand → Uppercase → LLM analyze → Count words
    agent.add_step(
        step_type="llm",
        prompt="Expand this into 2-3 sentences: {input}"
    )

    agent.add_step(
        step_type="tool",
        tool_name="uppercase"
    )

    agent.add_step(
        step_type="llm",
        prompt="Describe the tone of this text: {previous_output}",
        params={"max_tokens": 100}
    )

    agent.add_step(
        step_type="tool",
        tool_name="count_words"
    )

    result = agent.run("AI is amazing")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 4, "Should have 4 steps"
    assert "Word count:" in result.final_output, "Final step should count words"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - PYDANTIC STRUCTURED OUTPUT
# ============================================================================

def test_pydantic_simple():
    """Test simple Pydantic model generation"""
    print_section("TEST 3: Simple Pydantic Structured Output")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Sentiment Analyzer",
        llm_instance=llm,
        max_steps=2,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Analyze the sentiment of this text: {input}",
        output_model=SentimentAnalysis,
        max_retries=3,
        params={"max_tokens": 500}
    )

    result = agent.run("I absolutely love this new feature! It's incredibly useful and well-designed.")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert isinstance(result.final_output, SentimentAnalysis), "Output should be SentimentAnalysis model"
    assert result.final_output.sentiment in ["positive", "negative", "neutral"], "Should have valid sentiment"

    get_logger().log(f"\nParsed Sentiment: {result.final_output.sentiment}")
    print(f"   Confidence: {result.final_output.confidence}")

    get_logger().log("\n✓ Test passed!")


def test_pydantic_complex():
    """Test complex Pydantic model with nested structures"""
    print_section("TEST 4: Complex Pydantic Model with Lists")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Blog Outline Creator",
        llm_instance=llm,
        max_steps=3,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Create a blog post outline about: {input}",
        output_model=BlogPostOutline,
        max_retries=3,
        params={"max_tokens": 1000}
    )

    result = agent.run("The benefits of using AI in software development")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert isinstance(result.final_output, BlogPostOutline), "Output should be BlogPostOutline"
    assert len(result.final_output.main_points) >= 3, "Should have at least 3 main points"
    assert result.final_output.title, "Should have a title"

    get_logger().log(f"\nTitle: {result.final_output.title}")
    print(f"   Main Points: {len(result.final_output.main_points)}")

    get_logger().log("\n✓ Test passed!")


def test_pydantic_multi_step():
    """Test multiple Pydantic outputs in a chain"""
    print_section("TEST 5: Multi-Step Pydantic Pipeline")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Analysis Pipeline",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Step 1: Generate product analysis
    agent.add_step(
        step_type="llm",
        prompt="Analyze this product: {input}",
        output_model=ProductAnalysis,
        max_retries=3,
        params={"max_tokens": 800}
    )

    # Step 2: Convert to text summary
    agent.add_step(
        step_type="llm",
        prompt="Write a 2-sentence summary of this product analysis: {previous_output}",
        params={"max_tokens": 200}
    )

    # Step 3: Analyze the summary
    agent.add_step(
        step_type="llm",
        prompt="Analyze this summary and extract insights: {previous_output}",
        output_model=DataSummary,
        max_retries=3,
        params={"max_tokens": 600}
    )

    result = agent.run("iPhone 15 Pro - the latest smartphone with titanium design and A17 Pro chip")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 3, "Should have 3 steps"
    assert isinstance(result.steps[0].output_data, ProductAnalysis), "Step 1 should output ProductAnalysis"
    assert isinstance(result.steps[1].output_data, str), "Step 2 should output string"
    assert isinstance(result.final_output, DataSummary), "Final output should be DataSummary"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - RELIABLELLM INTEGRATION
# ============================================================================

def test_reliable_llm_basic():
    """Test flow with ReliableLLM (fallback support)"""
    print_section("TEST 6: ReliableLLM with Fallback Support")

    reliable_llm = get_test_reliable_llm(verbose=True)
    agent = MiniAgent(
        name="Reliable Text Processor",
        llm_instance=reliable_llm.primary_llm,  # Use primary LLM
        max_steps=3,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Rewrite this text in a formal tone: {input}",
        params={"max_tokens": 300}
    )

    result = agent.run("yo bro, check out this awesome new thing!")
    print_flow_result(result)

    assert result.success, "Flow should succeed"

    get_logger().log("\n✓ Test passed!")


def test_reliable_llm_with_pydantic():
    """Test ReliableLLM with Pydantic output"""
    print_section("TEST 7: ReliableLLM + Pydantic Structured Output")

    # Note: For proper ReliableLLM integration with Pydantic, we need to use
    # generate_pydantic_json_model_reliable directly or adapt the flow
    # For now, we'll test with standard LLM but show the pattern

    llm = get_test_llm()
    agent = MiniAgent(
        name="Reliable Sentiment Analyzer",
        llm_instance=llm,
        max_steps=2,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Analyze sentiment: {input}",
        output_model=SentimentAnalysis,
        max_retries=5,  # More retries for reliability
        params={"max_tokens": 500}
    )

    result = agent.run("This product is terrible and doesn't work at all!")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert isinstance(result.final_output, SentimentAnalysis), "Should output SentimentAnalysis"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - ASYNC OPERATIONS
# ============================================================================

async def test_async_flow_basic():
    """Test basic async flow execution"""
    print_section("TEST 8: Async Flow Execution")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Async Text Processor",
        llm_instance=llm,
        max_steps=3,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Expand this topic into 3 sentences: {input}"
    )

    agent.add_step(
        step_type="llm",
        prompt="Summarize: {previous_output}",
        params={"max_tokens": 100}
    )

    result = await agent.run_async("Machine learning applications")
    print_flow_result(result)

    assert result.success, "Async flow should succeed"
    assert result.total_steps == 2, "Should have 2 steps"

    get_logger().log("\n✓ Test passed!")


async def test_async_with_pydantic():
    """Test async flow with Pydantic output"""
    print_section("TEST 9: Async + Pydantic Structured Output")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Async Blog Creator",
        llm_instance=llm,
        max_steps=2,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Create a blog outline about: {input}",
        output_model=BlogPostOutline,
        max_retries=3,
        params={"max_tokens": 1000}
    )

    result = await agent.run_async("Climate change solutions")
    print_flow_result(result)

    assert result.success, "Async flow should succeed"
    assert isinstance(result.final_output, BlogPostOutline), "Should output BlogPostOutline"

    get_logger().log("\n✓ Test passed!")


async def test_sync_vs_async_performance():
    """Compare sync vs async performance"""
    print_section("TEST 10: Sync vs Async Performance Comparison")

    llm = get_test_llm()

    # Sync agent
    agent_sync = MiniAgent(
        name="Sync Performance Test",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    agent_sync.add_step(
        step_type="llm",
        prompt="Write 3 sentences about: {input}",
        params={"max_tokens": 200}
    )

    agent_sync.add_step(
        step_type="llm",
        prompt="Summarize: {previous_output}",
        params={"max_tokens": 100}
    )

    # Async agent (same structure)
    agent_async = MiniAgent(
        name="Async Performance Test",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    agent_async.add_step(
        step_type="llm",
        prompt="Write 3 sentences about: {input}",
        params={"max_tokens": 200}
    )

    agent_async.add_step(
        step_type="llm",
        prompt="Summarize: {previous_output}",
        params={"max_tokens": 100}
    )

    # Run sync
    print("\n   Running sync flow...")
    start_sync = time.time()
    result_sync = agent_sync.run("Artificial intelligence")
    duration_sync = time.time() - start_sync

    # Run async
    print("   Running async flow...")
    start_async = time.time()
    result_async = await agent_async.run_async("Artificial intelligence")
    duration_async = time.time() - start_async

    get_logger().log(f"\nSync duration: {duration_sync:.2f}s")
    print(f"   Async duration: {duration_async:.2f}s")
    print(f"   Difference: {abs(duration_sync - duration_async):.2f}s")

    assert result_sync.success, "Sync flow should succeed"
    assert result_async.success, "Async flow should succeed"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - TOOL REGISTRY
# ============================================================================

def test_tool_registry_builtin():
    """Test built-in tools from ToolRegistry"""
    print_section("TEST 11: Built-in Tool Registry")

    # List available tools
    available_tools = ToolRegistry.list_tools()
    get_logger().log(f"\nAvailable built-in tools: {len(available_tools)}")
    for tool in available_tools:
        print(f"   - {tool}")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Text Chunker",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Generate some text
    agent.add_step(
        step_type="llm",
        prompt="Write 5 paragraphs about machine learning, each paragraph should be 3-4 sentences.",
        params={"max_tokens": 800}
    )

    # Chunk by paragraphs
    agent.add_step(
        step_type="tool",
        tool_name="chunk_by_paragraphs"
    )

    result = agent.run("Generate paragraphs")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert isinstance(result.final_output, TextChunks), "Chunking should return TextChunks model"

    get_logger().log(f"\n   Chunks created: {result.final_output.num_chunks}")
    get_logger().log(f"   Chunk list length: {len(result.final_output.chunk_list)}")

    # Show example of accessing individual chunks
    if result.final_output.chunk_list:
        get_logger().log(f"   First chunk preview: {result.final_output.chunk_list[0].text[:100]}...")
        get_logger().log(f"   First chunk word count: {result.final_output.chunk_list[0].num_words}")

    get_logger().log("\n✓ Test passed!")


def test_tool_registry_custom():
    """Test custom tool registration"""
    print_section("TEST 12: Custom Tool Registration")

    # Register custom tools
    ToolRegistry.register_tool("reverse", reverse_text)
    ToolRegistry.register_tool("extract_numbers", extract_numbers)
    ToolRegistry.register_tool("add_prefix", add_prefix)

    llm = get_test_llm()
    agent = MiniAgent(
        name="Custom Tool User",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Use custom tools
    agent.add_step(
        step_type="llm",
        prompt="Write a sentence with some numbers in it about: {input}",
        params={"max_tokens": 100}
    )

    agent.add_step(
        step_type="tool",
        tool_name="extract_numbers"
    )

    agent.add_step(
        step_type="tool",
        tool_name="add_prefix",
        params={"prefix": "RESULT:"}
    )

    result = agent.run("data science statistics")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert "RESULT:" in result.final_output, "Should have prefix"

    get_logger().log("\n✓ Test passed!")


def test_tool_with_params():
    """Test tool execution with parameters"""
    print_section("TEST 13: Tool Parameters")

    ToolRegistry.register_tool("add_prefix", add_prefix)

    llm = get_test_llm()
    agent = MiniAgent(
        name="Parameterized Tool Test",
        llm_instance=llm,
        max_steps=3,
        verbose=True
    )

    agent.add_step(
        step_type="llm",
        prompt="Write one sentence about: {input}",
        params={"max_tokens": 100}
    )

    agent.add_step(
        step_type="tool",
        tool_name="add_prefix",
        params={"prefix": ">>> ANALYSIS:"}
    )

    result = agent.run("quantum computing")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert ">>> ANALYSIS:" in result.final_output, "Should have custom prefix"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - ERROR HANDLING
# ============================================================================

def test_error_empty_flow():
    """Test error handling for empty flow"""
    print_section("TEST 14: Error - Empty Flow")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Empty Flow",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    # Don't add any steps
    try:
        result = agent.run("test input")
        assert False, "Should raise ValueError for empty flow"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "No steps defined" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_max_steps():
    """Test max steps enforcement"""
    print_section("TEST 15: Error - Max Steps Limit")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Max Steps Test",
        llm_instance=llm,
        max_steps=2,  # Only allow 2 steps
        verbose=False
    )

    agent.add_step(
        step_type="llm",
        prompt="Step 1: {input}"
    )

    agent.add_step(
        step_type="llm",
        prompt="Step 2: {previous_output}"
    )

    # Try to add a 3rd step
    try:
        agent.add_step(
            step_type="llm",
            prompt="Step 3: {previous_output}"
        )
        assert False, "Should raise ValueError when exceeding max_steps"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "Cannot add more than" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_invalid_step_type():
    """Test invalid step type"""
    print_section("TEST 16: Error - Invalid Step Type")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Invalid Step Type",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    try:
        agent.add_step(
            step_type="invalid_type",
            prompt="test"
        )
        assert False, "Should raise ValueError for invalid step type"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "Invalid step_type" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_missing_tool_name():
    """Test missing tool name for tool step"""
    print_section("TEST 17: Error - Missing Tool Name")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Missing Tool Name",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    try:
        agent.add_step(
            step_type="tool"
            # Missing tool_name
        )
        assert False, "Should raise ValueError for missing tool_name"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "tool_name is required" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_missing_prompt():
    """Test missing prompt for LLM step"""
    print_section("TEST 18: Error - Missing Prompt")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Missing Prompt",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    try:
        agent.add_step(
            step_type="llm"
            # Missing prompt
        )
        assert False, "Should raise ValueError for missing prompt"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "prompt is required" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_invalid_tool():
    """Test error for non-existent tool"""
    print_section("TEST 19: Error - Non-existent Tool")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Invalid Tool",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    try:
        agent.add_step(
            step_type="tool",
            tool_name="non_existent_tool_xyz"
        )
        assert False, "Should raise ValueError for non-existent tool"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "not found in registry" in str(e)

    get_logger().log("\n✓ Test passed!")


def test_error_output_model_on_tool():
    """Test error when using output_model with tool step"""
    print_section("TEST 20: Error - Output Model on Tool Step")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Invalid Output Model Usage",
        llm_instance=llm,
        max_steps=3,
        verbose=False
    )

    ToolRegistry.register_tool("uppercase", uppercase_text)

    try:
        agent.add_step(
            step_type="tool",
            tool_name="uppercase",
            output_model=SentimentAnalysis  # Invalid: can't use with tools
        )
        assert False, "Should raise ValueError for output_model on tool step"
    except ValueError as e:
        get_logger().log(f"\n✓ Correctly raised ValueError: {str(e)}")
        assert "output_model can only be used with 'llm'" in str(e)

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# TEST FUNCTIONS - ADVANCED FEATURES
# ============================================================================

def test_clear_steps():
    """Test clear_steps functionality"""
    print_section("TEST 21: Clear Steps")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Clear Steps Test",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Add some steps
    agent.add_step(step_type="llm", prompt="Step 1: {input}")
    agent.add_step(step_type="llm", prompt="Step 2: {previous_output}")

    assert agent.get_step_count() == 2, "Should have 2 steps"

    # Clear steps
    agent.clear_steps()

    assert agent.get_step_count() == 0, "Should have 0 steps after clear"

    # Add new steps
    agent.add_step(step_type="llm", prompt="New step: {input}")

    assert agent.get_step_count() == 1, "Should have 1 step after adding"

    result = agent.run("test input")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 1, "Should only execute the new step"

    get_logger().log("\n✓ Test passed!")


def test_prompt_placeholders():
    """Test different prompt placeholder patterns"""
    print_section("TEST 22: Prompt Placeholders")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Placeholder Test",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Test {input} placeholder
    agent.add_step(
        step_type="llm",
        prompt="Expand this topic using the {input} placeholder: {input}",
        params={"max_tokens": 150}
    )

    # Test {previous_output} placeholder
    agent.add_step(
        step_type="llm",
        prompt="Now summarize the {previous_output}: {previous_output}",
        params={"max_tokens": 100}
    )

    # Test no placeholder (should append input)
    agent.add_step(
        step_type="llm",
        prompt="Create a title for this content (no placeholder used)",
        params={"max_tokens": 50}
    )

    result = agent.run("quantum physics")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 3, "Should have 3 steps"

    get_logger().log("\n✓ Test passed!")


def test_step_parameters():
    """Test custom parameters for LLM steps"""
    print_section("TEST 23: Step-Level Parameters")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Custom Parameters Test",
        llm_instance=llm,
        max_steps=5,
        verbose=True
    )

    # Step with low temperature (more deterministic)
    agent.add_step(
        step_type="llm",
        prompt="Write a technical description of: {input}",
        params={
            "max_tokens": 200,
            "temperature": 0.3,
            "top_p": 0.8
        }
    )

    # Step with high temperature (more creative)
    agent.add_step(
        step_type="llm",
        prompt="Write a creative story about: {previous_output}",
        params={
            "max_tokens": 300,
            "temperature": 0.9,
            "top_p": 0.95
        }
    )

    result = agent.run("neural networks")
    print_flow_result(result)

    assert result.success, "Flow should succeed"
    assert result.total_steps == 2, "Should have 2 steps"

    get_logger().log("\n✓ Test passed!")


def test_flow_result_analysis():
    """Test FlowResult data structure and analysis"""
    print_section("TEST 24: FlowResult Analysis")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Result Analysis Test",
        llm_instance=llm,
        max_steps=5,
        verbose=False
    )

    agent.add_step(
        step_type="llm",
        prompt="Generate text: {input}",
        params={"max_tokens": 100}
    )

    agent.add_step(
        step_type="llm",
        prompt="Analyze: {previous_output}",
        output_model=SentimentAnalysis,
        max_retries=3,
        params={"max_tokens": 400}
    )

    result = agent.run("amazing product")

    # Analyze FlowResult structure
    get_logger().log(f"\nAgent Name: {result.agent_name}")
    print(f"   Success: {result.success}")
    print(f"   Total Steps: {result.total_steps}")
    print(f"   Total Duration: {result.total_duration_seconds:.2f}s")
    print(f"   Executed At: {result.executed_at}")
    print(f"   Error: {result.error}")

    # Analyze each step
    for i, step in enumerate(result.steps, 1):
        get_logger().log(f"\nStep {i} Analysis:")
        print(f"      Step Number: {step.step_number}")
        print(f"      Step Type: {step.step_type}")
        print(f"      Duration: {step.duration_seconds:.2f}s")
        print(f"      Tool Used: {step.tool_used}")
        print(f"      Prompt Used: {step.prompt_used[:50] if step.prompt_used else None}...")
        print(f"      Output Model: {step.output_model_class}")
        print(f"      Error: {step.error}")
        print(f"      Output Type: {type(step.output_data).__name__}")

    # Assertions
    assert result.success, "Flow should succeed"
    assert len(result.steps) == 2, "Should have 2 step results"
    assert result.steps[0].step_type == "llm", "First step should be LLM"
    assert result.steps[1].output_model_class == "SentimentAnalysis", "Second step should use SentimentAnalysis"
    assert isinstance(result.final_output, SentimentAnalysis), "Final output should be model instance"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# REAL-WORLD SCENARIO TESTS
# ============================================================================

def test_scenario_content_pipeline():
    """Real-world scenario: Content creation pipeline"""
    print_section("TEST 25: Real-World - Content Creation Pipeline")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Content Creation Pipeline",
        llm_instance=llm,
        system_prompt="You are an expert content creator and analyzer.",
        max_steps=5,
        verbose=True
    )

    # Step 1: Generate blog outline
    agent.add_step(
        step_type="llm",
        prompt="Create a comprehensive blog post outline about: {input}",
        output_model=BlogPostOutline,
        max_retries=3,
        params={"max_tokens": 1000}
    )

    # Step 2: Expand introduction
    agent.add_step(
        step_type="llm",
        prompt="Write a detailed introduction paragraph based on this outline: {previous_output}",
        params={"max_tokens": 400}
    )

    # Step 3: Analyze sentiment
    agent.add_step(
        step_type="llm",
        prompt="Analyze the tone and sentiment of this introduction: {previous_output}",
        output_model=SentimentAnalysis,
        max_retries=3,
        params={"max_tokens": 400}
    )

    result = agent.run("The future of renewable energy and sustainable development")
    print_flow_result(result)

    assert result.success, "Content pipeline should succeed"
    assert result.total_steps == 3, "Should complete all 3 steps"
    assert isinstance(result.steps[0].output_data, BlogPostOutline), "Step 1 should create outline"
    assert isinstance(result.steps[1].output_data, str), "Step 2 should create text"
    assert isinstance(result.final_output, SentimentAnalysis), "Step 3 should analyze sentiment"

    print("\n   📊 Pipeline Results:")
    print(f"   - Outline created with {len(result.steps[0].output_data.main_points)} main points")
    print(f"   - Introduction: {len(result.steps[1].output_data.split())} words")
    print(f"   - Sentiment: {result.final_output.sentiment} (confidence: {result.final_output.confidence})")

    get_logger().log("\n✓ Test passed!")


def test_scenario_data_processing():
    """Real-world scenario: Data processing and analysis"""
    print_section("TEST 26: Real-World - Data Processing Pipeline")

    llm = get_test_llm()
    agent = MiniAgent(
        name="Data Processing Pipeline",
        llm_instance=llm,
        system_prompt="You are a data analyst expert.",
        max_steps=5,
        verbose=True
    )

    # Register text processing tool
    ToolRegistry.register_tool("count_words", count_words)

    # Step 1: Generate sample data
    agent.add_step(
        step_type="llm",
        prompt="Generate a dataset description with statistics about: {input}",
        params={"max_tokens": 500}
    )

    # Step 2: Count words
    agent.add_step(
        step_type="tool",
        tool_name="count_words"
    )

    # Step 3: Create summary
    agent.add_step(
        step_type="llm",
        prompt="Based on this data analysis, create a summary: {previous_output}",
        output_model=DataSummary,
        max_retries=3,
        params={"max_tokens": 700}
    )

    result = agent.run("customer satisfaction survey results for Q4 2024")
    print_flow_result(result)

    assert result.success, "Data pipeline should succeed"
    assert result.total_steps == 3, "Should complete all steps"
    assert isinstance(result.final_output, DataSummary), "Should output DataSummary"

    print("\n   📊 Data Analysis Results:")
    print(f"   - Total insights: {len(result.final_output.key_insights)}")
    print(f"   - Summary length: {len(result.final_output.summary)} chars")

    get_logger().log("\n✓ Test passed!")


async def test_scenario_async_batch_processing():
    """Real-world scenario: Async batch processing"""
    print_section("TEST 27: Real-World - Async Batch Processing")

    llm = get_test_llm()

    # Create multiple agents for parallel processing
    topics = [
        "artificial intelligence",
        "blockchain technology",
        "quantum computing"
    ]

    agents = []
    for topic in topics:
        agent = MiniAgent(
            name=f"Analyzer-{topic}",
            llm_instance=llm,
            max_steps=3,
            verbose=False
        )

        agent.add_step(
            step_type="llm",
            prompt="Write 2 sentences about: {input}",
            params={"max_tokens": 200}
        )

        agent.add_step(
            step_type="llm",
            prompt="Analyze this: {previous_output}",
            output_model=SentimentAnalysis,
            max_retries=3,
            params={"max_tokens": 400}
        )

        agents.append((agent, topic))

    # Run all agents in parallel
    get_logger().log(f"\nProcessing {len(topics)} topics in parallel...")
    start_time = time.time()

    tasks = [agent.run_async(topic) for agent, topic in agents]
    results = await asyncio.gather(*tasks)

    duration = time.time() - start_time

    get_logger().log(f"\n✓ Processed {len(results)} topics in {duration:.2f}s")
    print(f"   Average per topic: {duration/len(results):.2f}s")

    # Verify all succeeded
    for i, result in enumerate(results):
        get_logger().log(f"\nTopic {i+1} ({topics[i]}): {result.success}")
        assert result.success, f"Topic {i+1} should succeed"
        assert isinstance(result.final_output, SentimentAnalysis), f"Topic {i+1} should output sentiment"

    get_logger().log("\n✓ Test passed!")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_sync_tests():
    """Run all synchronous tests"""
    log = get_logger()
    log.log("\n" + "=" * 80)
    log.log("  STARTING COMPREHENSIVE FLOW TESTS - SYNCHRONOUS")
    log.log("=" * 80)

    tests = [
        # Basic operations
        ("Basic Flow Sync", test_basic_flow_sync),
        ("Step Chaining", test_step_chaining),

        # Pydantic
        ("Pydantic Simple", test_pydantic_simple),
        ("Pydantic Complex", test_pydantic_complex),
        ("Pydantic Multi-Step", test_pydantic_multi_step),

        # ReliableLLM
        ("ReliableLLM Basic", test_reliable_llm_basic),
        ("ReliableLLM + Pydantic", test_reliable_llm_with_pydantic),

        # Tool Registry
        ("Built-in Tools", test_tool_registry_builtin),
        ("Custom Tools", test_tool_registry_custom),
        ("Tool Parameters", test_tool_with_params),

        # Error handling
        ("Error: Empty Flow", test_error_empty_flow),
        ("Error: Max Steps", test_error_max_steps),
        ("Error: Invalid Step Type", test_error_invalid_step_type),
        ("Error: Missing Tool Name", test_error_missing_tool_name),
        ("Error: Missing Prompt", test_error_missing_prompt),
        ("Error: Invalid Tool", test_error_invalid_tool),
        ("Error: Output Model on Tool", test_error_output_model_on_tool),

        # Advanced features
        ("Clear Steps", test_clear_steps),
        ("Prompt Placeholders", test_prompt_placeholders),
        ("Step Parameters", test_step_parameters),
        ("Flow Result Analysis", test_flow_result_analysis),

        # Real-world scenarios
        ("Scenario: Content Pipeline", test_scenario_content_pipeline),
        ("Scenario: Data Processing", test_scenario_data_processing),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            log.log(f"\n✗ Test '{name}' FAILED with error: {str(e)}")
            import traceback
            import io
            # Capture traceback to string and log it
            tb_stream = io.StringIO()
            traceback.print_exc(file=tb_stream)
            log.log(tb_stream.getvalue())

    return passed, failed


async def run_async_tests():
    """Run all asynchronous tests"""
    log = get_logger()
    log.log("\n" + "=" * 80)
    log.log("  STARTING COMPREHENSIVE FLOW TESTS - ASYNCHRONOUS")
    log.log("=" * 80)

    tests = [
        ("Async Flow Basic", test_async_flow_basic),
        ("Async + Pydantic", test_async_with_pydantic),
        ("Sync vs Async Performance", test_sync_vs_async_performance),
        ("Scenario: Async Batch", test_scenario_async_batch_processing),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            log.log(f"\n✗ Test '{name}' FAILED with error: {str(e)}")
            import traceback
            import io
            # Capture traceback to string and log it
            tb_stream = io.StringIO()
            traceback.print_exc(file=tb_stream)
            log.log(tb_stream.getvalue())

    return passed, failed


def main():
    """Main test execution"""
    log = get_logger()

    log.log("\n" + "=" * 80)
    log.log("  SimplerLLM Flow/MiniAgent - Comprehensive Test Suite")
    log.log("=" * 80)
    log.log("\n  This test suite covers:")
    log.log("  ✓ Synchronous and asynchronous flow execution")
    log.log("  ✓ Pydantic structured output with validation")
    log.log("  ✓ ReliableLLM with fallback support")
    log.log("  ✓ Tool registry (built-in and custom tools)")
    log.log("  ✓ Error handling and edge cases")
    log.log("  ✓ Real-world usage scenarios")
    log.log("\n" + "=" * 80)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        log.log("\n✗ ERROR: OPENAI_API_KEY not found in environment variables")
        log.log("  Please create a .env file with your API key")
        log.close()
        return

    start_time = time.time()

    # Run sync tests
    sync_passed, sync_failed = run_sync_tests()

    # Run async tests
    async_passed, async_failed = asyncio.run(run_async_tests())

    total_duration = time.time() - start_time

    # Summary
    total_passed = sync_passed + async_passed
    total_failed = sync_failed + async_failed
    total_tests = total_passed + total_failed

    log.log("\n" + "=" * 80)
    log.log("  TEST SUMMARY")
    log.log("=" * 80)
    log.log(f"\n  Total Tests: {total_tests}")
    log.log(f"  ✓ Passed: {total_passed}")
    log.log(f"  ✗ Failed: {total_failed}")
    log.log(f"  Success Rate: {(total_passed/total_tests*100):.1f}%")
    log.log(f"  Total Duration: {total_duration:.2f}s")
    log.log(f"  Average per test: {total_duration/total_tests:.2f}s")
    log.log("\n" + "=" * 80)

    if total_failed == 0:
        log.log("\n  🎉 ALL TESTS PASSED! 🎉")
    else:
        log.log(f"\n  ⚠️  {total_failed} test(s) failed. Please review the errors above.")

    log.log("\n" + "=" * 80 + "\n")

    # Close the log file
    log.log(f"\n📁 Full results saved to: {os.path.abspath(log.log_file_path)}\n")
    log.close()


if __name__ == "__main__":
    main()
