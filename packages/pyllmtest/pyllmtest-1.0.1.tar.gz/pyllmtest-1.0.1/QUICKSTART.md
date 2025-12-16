# PyLLMTest Quick Start Guide 🚀

Get started with PyLLMTest in 5 minutes!

## Installation

```bash
pip install pyllmtest[all]
```

## Step 1: Set Up Your API Keys

```bash
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key
```

## Step 2: Write Your First Test

Create `test_basic.py`:

```python
from pyllmtest import LLMTest, expect, OpenAIProvider

# Initialize provider
provider = OpenAIProvider(model="gpt-3.5-turbo")

# Write a test
@LLMTest(provider=provider, name="test_hello_world")
def test_hello_world(ctx):
    """Test that LLM can greet properly"""
    response = ctx.complete("Say hello in a friendly way")
    
    # Assertions
    expect(response.content).to_contain("hello", case_sensitive=False)
    expect(response.content).to_be_shorter_than(50, unit="words")
    
    print(f"✓ Response: {response.content}")
    print(f"✓ Tokens: {response.tokens_used}")
    print(f"✓ Cost: ${response.cost_usd:.6f}")

# Run it!
if __name__ == "__main__":
    result = test_hello_world()
    print(f"\nTest Result: {'✓ PASSED' if result.passed else '✗ FAILED'}")
```

Run it:

```bash
python test_basic.py
```

## Step 3: Add Snapshot Testing

Update your test:

```python
from pyllmtest import LLMTest, expect, OpenAIProvider, SnapshotManager

provider = OpenAIProvider(model="gpt-3.5-turbo")
snapshots = SnapshotManager()

@LLMTest(provider=provider)
def test_with_snapshot(ctx):
    """Test with snapshot - detects regressions"""
    response = ctx.complete("List the planets in our solar system")
    
    # Save snapshot on first run, compare on subsequent runs
    snapshots.assert_matches_snapshot(
        name="planets_list",
        actual_content=response.content
    )
    
    # Also check facts
    expect(response.content).to_preserve_facts([
        "Mercury", "Venus", "Earth", "Mars"
    ])

if __name__ == "__main__":
    test_with_snapshot()
```

## Step 4: Track Metrics

```python
from pyllmtest import MetricsTracker, OpenAIProvider

provider = OpenAIProvider()
metrics = MetricsTracker()

# Make some requests
for query in ["What is AI?", "Explain ML", "Define NLP"]:
    response = provider.complete(query)
    metrics.track_request(response)

# See the summary
metrics.print_summary()

# Export reports
metrics.export_json("metrics.json")
```

## Step 5: Test RAG Systems

```python
from pyllmtest import RAGTester, RetrievedDocument, OpenAIProvider

provider = OpenAIProvider()

# Your retrieval function
def retrieve(query: str):
    # Mock - replace with your actual retrieval
    return [
        RetrievedDocument(
            content="Python is a programming language",
            score=0.95,
            metadata={"source": "doc1"}
        )
    ]

# Your generation function
def generate(query: str, docs: list):
    context = "\n".join(d.content for d in docs)
    prompt = f"Context: {context}\n\nQuestion: {query}"
    return provider.complete(prompt).content

# Test it
rag_tester = RAGTester(retrieve, generate)
result = rag_tester.test_query("What is Python?")

# Assertions
rag_tester.assert_retrieval_quality(result, min_docs=1)
rag_tester.assert_context_used(result)
rag_tester.assert_no_hallucination(result)

print(f"✓ RAG Test Passed!")
print(f"  Retrieval: {result.retrieval_time_ms:.0f}ms")
print(f"  Generation: {result.generation_time_ms:.0f}ms")
```

## Step 6: Optimize Prompts

```python
from pyllmtest import PromptOptimizer, PromptVariant, OpenAIProvider

provider = OpenAIProvider()
optimizer = PromptOptimizer(provider)

# Define variants
variants = [
    PromptVariant(
        id="v1",
        template="Explain {topic} in detail",
        description="Detailed version"
    ),
    PromptVariant(
        id="v2",
        template="Briefly explain {topic}",
        description="Brief version"
    ),
]

# Test inputs
inputs = [{"topic": "AI"}, {"topic": "ML"}]

# Compare
results = optimizer.compare_prompts(variants, inputs)
optimizer.print_comparison(results)

# Find best
best = optimizer.find_best_prompt(results, optimize_for="cost")
print(f"Best prompt: {best}")
```

## Next Steps

✨ **You're ready to build comprehensive LLM tests!**

### Learn More:
- Read the [full documentation](README.md)
- Check out [examples/](examples/)
- Join our [Discord community](https://discord.gg/pyllmtest)

### Common Patterns:

**Test Suites:**
```python
@LLMTest(provider=provider, suite="nlp", name="sentiment")
def test_sentiment(ctx):
    ...

@LLMTest(provider=provider, suite="nlp", name="translation")
def test_translation(ctx):
    ...

# Get suite stats
suite = LLMTest.get_suite("nlp")
print(suite.get_summary())
```

**Async Testing:**
```python
@LLMTest(provider=provider)
async def test_async(ctx):
    responses = await asyncio.gather(
        ctx.acomplete("query1"),
        ctx.acomplete("query2"),
    )
```

**Custom Quality Scoring:**
```python
def quality_fn(response: str) -> float:
    # Your scoring logic (0-1)
    return len(response.split()) / 100

optimizer = PromptOptimizer(provider, quality_fn=quality_fn)
```

### Tips:

💡 **Use semantic assertions** - They're more robust than exact matching

💡 **Enable snapshot testing** - Catches regressions early

💡 **Track metrics** - Monitor costs and performance

💡 **Optimize prompts** - A/B test to find the best

💡 **Test RAG systems** - Ensure retrieval quality

---

**Happy Testing! 🎉**

Questions? Open an issue or join our Discord!
