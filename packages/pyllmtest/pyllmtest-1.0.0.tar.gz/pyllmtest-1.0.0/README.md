# PyLLMTest 🚀

**The Most Comprehensive LLM Testing Framework for Python**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/pyllmtest.svg)](https://badge.fury.io/py/pyllmtest)

PyLLMTest is a revolutionary testing framework designed specifically for LLM applications. It provides everything you need to build, test, and optimize AI-powered applications with confidence.

## 🌟 Why PyLLMTest?

Testing LLM applications is **fundamentally different** from traditional software testing. PyLLMTest solves the unique challenges of LLM testing:

- ✅ **Semantic Assertions** - Test meaning, not exact strings
- ✅ **Snapshot Testing** - Detect regressions with semantic awareness
- ✅ **Multi-Provider Support** - OpenAI, Anthropic, and more
- ✅ **RAG Testing** - Comprehensive retrieval and generation testing
- ✅ **Cost Tracking** - Monitor token usage and costs
- ✅ **Prompt Optimization** - A/B test and optimize prompts
- ✅ **Performance Benchmarking** - Track latency and quality
- ✅ **Async Support** - Full async/await compatibility
- ✅ **Beautiful Reporting** - Rich test reports and metrics

## 📦 Installation

```bash
# Basic installation
pip install pyllmtest

# With OpenAI support
pip install pyllmtest[openai]

# With Anthropic support
pip install pyllmtest[anthropic]

# With all providers and features
pip install pyllmtest[all]
```

## 🚀 Quick Start

### Basic Test

```python
from pyllmtest import LLMTest, expect, OpenAIProvider

provider = OpenAIProvider(model="gpt-4-turbo")

@LLMTest(provider=provider)
def test_summarization(ctx):
    response = ctx.complete("Summarize: AI is transforming industries...")
    
    # Semantic assertions
    expect(response.content).to_be_shorter_than(100, unit="words")
    expect(response.content).to_contain("AI")
    expect(response.content).to_preserve_facts(["transform", "industries"])

# Run the test
result = test_summarization()
print(f"Test {'PASSED' if result.passed else 'FAILED'}")
```

### Snapshot Testing

```python
from pyllmtest import SnapshotManager

snapshot_mgr = SnapshotManager()

@LLMTest(provider=provider)
def test_with_snapshot(ctx):
    response = ctx.complete("What are the primary colors?")
    
    # Automatically detects semantic changes
    snapshot_mgr.assert_matches_snapshot(
        name="primary_colors",
        actual_content=response.content
    )
```

### Async Testing

```python
@LLMTest(provider=provider)
async def test_parallel_completions(ctx):
    tasks = [
        ctx.acomplete("Explain Python"),
        ctx.acomplete("Explain JavaScript"),
        ctx.acomplete("Explain Rust")
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for resp in responses:
        expect(resp.content).to_be_longer_than(50, unit="words")
```

## 📚 Core Features

### 1. Semantic Assertions

Unlike traditional assertions, PyLLMTest understands **meaning**:

```python
# Traditional (brittle)
assert "artificial intelligence" in response  # Fails if AI says "AI"

# PyLLMTest (semantic)
expect(response).to_match_semantic("artificial intelligence", threshold=0.9)
expect(response).to_preserve_facts(["machine learning", "neural networks"])
expect(response).not_to_hallucinate(source_text=original_document)
```

**Available Assertions:**
- `to_contain()` / `not_to_contain()` - Check for substrings
- `to_match_regex()` - Regex matching
- `to_be_shorter_than()` / `to_be_longer_than()` - Length checks
- `to_be_concise()` / `to_be_detailed()` - Quality checks
- `to_preserve_facts()` - Fact preservation
- `not_to_hallucinate()` - Hallucination detection
- `to_be_valid_json()` / `to_match_schema()` - Format validation
- `to_match_semantic()` - Semantic similarity

### 2. Snapshot Testing

Save "golden" outputs and detect regressions:

```python
snapshot_mgr = SnapshotManager(
    snapshot_dir=".snapshots",
    update_mode=False,  # Set to True to update snapshots
    semantic_threshold=0.9  # Allow 90% semantic similarity
)

# First run: saves snapshot
# Subsequent runs: compares with snapshot
snapshot_mgr.assert_matches_snapshot("test_name", actual_content)
```

Features:
- **Semantic comparison** - Not just exact matching
- **Version tracking** - Track snapshot history
- **Diff generation** - See what changed
- **Update mode** - Review and approve changes

### 3. Multi-Provider Support

Seamlessly switch between providers:

```python
from pyllmtest import OpenAIProvider, AnthropicProvider

# OpenAI
openai_provider = OpenAIProvider(
    model="gpt-4-turbo",
    api_key="your-key"  # or use OPENAI_API_KEY env var
)

# Anthropic
anthropic_provider = AnthropicProvider(
    model="claude-3-5-sonnet-20241022",
    api_key="your-key"  # or use ANTHROPIC_API_KEY env var
)

# Use in tests
@LLMTest(provider=openai_provider)
def test_openai(ctx):
    ...

@LLMTest(provider=anthropic_provider)
def test_anthropic(ctx):
    ...
```

### 4. Metrics Tracking

Track everything:

```python
from pyllmtest import MetricsTracker

metrics = MetricsTracker()

# Automatic tracking in tests
@LLMTest(provider=provider)
def test_with_metrics(ctx):
    response = ctx.complete("query")  # Automatically tracked

# Print comprehensive report
metrics.print_summary()

# Export to JSON/CSV
metrics.export_json("metrics.json")
metrics.export_csv("requests.csv")
```

**Tracked Metrics:**
- Total requests and tokens
- Prompt vs completion tokens
- Cost breakdown by model/provider
- Latency percentiles (p50, p95, p99)
- Per-model and per-provider stats

### 5. RAG Testing

Test retrieval-augmented generation:

```python
from pyllmtest import RAGTester, RetrievedDocument

def my_retrieval_fn(query: str):
    # Your retrieval logic
    return [
        RetrievedDocument(
            content="Document content",
            score=0.95,
            metadata={"source": "doc.txt"}
        )
    ]

def my_generation_fn(query: str, docs: list):
    # Your generation logic
    return "Generated response"

rag_tester = RAGTester(
    retrieval_fn=my_retrieval_fn,
    generation_fn=my_generation_fn
)

result = rag_tester.test_query(
    query="What is AI?",
    expected_facts=["artificial", "intelligence"]
)

# Assertions
rag_tester.assert_retrieval_quality(result, min_docs=3, min_relevance=0.8)
rag_tester.assert_context_used(result)
rag_tester.assert_no_hallucination(result)
rag_tester.assert_performance(result, max_total_ms=1000)
```

### 6. Prompt Optimization

A/B test and optimize prompts:

```python
from pyllmtest import PromptOptimizer, PromptVariant

optimizer = PromptOptimizer(provider=provider, quality_fn=my_quality_fn)

variants = [
    PromptVariant(
        id="detailed",
        template="Provide a detailed explanation of {topic}",
        description="Detailed prompt"
    ),
    PromptVariant(
        id="concise",
        template="Briefly explain {topic}",
        description="Concise prompt"
    )
]

test_inputs = [
    {"topic": "machine learning"},
    {"topic": "neural networks"}
]

# Compare prompts
results = optimizer.compare_prompts(variants, test_inputs)
optimizer.print_comparison(results)

# Find best prompt
best_id = optimizer.find_best_prompt(
    results,
    optimize_for="balanced",  # "quality", "cost", "latency", or "balanced"
    quality_threshold=0.8
)

print(f"Best prompt: {best_id}")
```

### 7. Test Suites

Organize tests into suites:

```python
@LLMTest(provider=provider, suite="nlp_tests", name="test_sentiment")
def test_sentiment(ctx):
    ...

@LLMTest(provider=provider, suite="nlp_tests", name="test_translation")
def test_translation(ctx):
    ...

# Run all tests
test_sentiment()
test_translation()

# Get suite summary
suite = LLMTest.get_suite("nlp_tests")
summary = suite.get_summary()

print(f"Pass rate: {summary['pass_rate']:.1f}%")
print(f"Total cost: ${summary['total_cost_usd']:.4f}")
```

## 🎯 Advanced Features

### Streaming Support

```python
@LLMTest(provider=provider)
async def test_streaming(ctx):
    full_content = ""
    
    async for chunk in provider.stream("Explain quantum computing"):
        full_content += chunk.content
        
        if chunk.is_final:
            expect(full_content).to_be_detailed()
```

### Custom Assertions

```python
def is_valid_email(text: str) -> bool:
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, text))

expect(response.content).to_satisfy(
    is_valid_email,
    message="Response must be a valid email"
)
```

### Semantic Deduplication

```python
from pyllmtest.utils.semantic import semantic_deduplication

texts = [
    "Machine learning is a subset of AI",
    "ML is part of artificial intelligence",  # Similar to above
    "Deep learning uses neural networks"
]

unique_texts = semantic_deduplication(texts, provider, threshold=0.95)
# Returns: ["Machine learning is a subset of AI", "Deep learning uses neural networks"]
```

### Semantic Clustering

```python
from pyllmtest.utils.semantic import cluster_texts

texts = [
    "Python is great for AI",
    "JavaScript is used for web dev",
    "TensorFlow is an ML framework",
    "React is a web framework"
]

clusters = cluster_texts(texts, provider, num_clusters=2)
# Groups similar texts together
```

## 📊 Reporting

### Console Reports

```python
# Automatic beautiful console output
metrics.print_summary()
```

Output:
```
============================================================
METRICS SUMMARY
============================================================
Total Requests: 10
Total Tokens: 5,420
  Prompt Tokens: 2,100
  Completion Tokens: 3,320
Total Cost: $0.0542

Latency:
  Average: 1,234.56ms
  Min: 890.12ms
  Max: 2,100.45ms
  P50: 1,200.00ms
  P95: 1,800.00ms
  P99: 2,000.00ms
============================================================
```

### Export Options

```python
# JSON export
metrics.export_json("report.json")

# CSV export (detailed request log)
metrics.export_csv("requests.csv")
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY=your-key

# Anthropic
export ANTHROPIC_API_KEY=your-key
```

### Provider Configuration

```python
provider = OpenAIProvider(
    model="gpt-4-turbo",
    timeout=60,
    max_retries=3,
    temperature=0.7
)
```

## 📖 Examples

Check out the `examples/` directory for:
- `comprehensive_example.py` - All features demonstrated
- `basic_testing.py` - Simple getting started
- `rag_testing.py` - RAG system testing
- `prompt_optimization.py` - Prompt A/B testing
- `async_testing.py` - Async patterns

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ for the AI community.

Special thanks to:
- OpenAI for their amazing APIs
- Anthropic for Claude
- The Python testing community

## 📞 Support

- 📧 Email: support@pyllmtest.dev
- 💬 Discord: [Join our community](https://discord.gg/pyllmtest)
- 📖 Docs: [docs.pyllmtest.dev](https://docs.pyllmtest.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/pyllmtest/issues)

## ⭐ Star History

If you find PyLLMTest useful, please consider giving it a star on GitHub!

---

**Made with 🚀 by developers, for developers**

*Making LLM testing as easy as it should be.*
