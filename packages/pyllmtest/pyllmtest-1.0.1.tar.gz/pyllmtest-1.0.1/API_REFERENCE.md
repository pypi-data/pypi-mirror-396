# PyLLMTest API Reference

Complete API documentation for PyLLMTest.

## Table of Contents

- [Core Testing](#core-testing)
- [Assertions](#assertions)
- [Providers](#providers)
- [Snapshot Testing](#snapshot-testing)
- [Metrics Tracking](#metrics-tracking)
- [RAG Testing](#rag-testing)
- [Prompt Optimization](#prompt-optimization)
- [Utilities](#utilities)

---

## Core Testing

### `LLMTest` Decorator

Main decorator for creating LLM tests.

```python
@LLMTest(
    provider: BaseLLMProvider,
    name: Optional[str] = None,
    suite: str = "default",
    timeout: int = 60,
    retries: int = 0,
    tags: Optional[List[str]] = None
)
def test_function(ctx: TestContext):
    ...
```

**Parameters:**
- `provider`: LLM provider instance
- `name`: Test name (defaults to function name)
- `suite`: Test suite name
- `timeout`: Timeout in seconds
- `retries`: Number of retries on failure
- `tags`: List of tags for organization

**Context Object (`ctx`):**
- `ctx.complete(prompt, **kwargs)`: Synchronous completion
- `ctx.acomplete(prompt, **kwargs)`: Async completion
- `ctx.metrics`: MetricsTracker instance
- `ctx.provider`: LLM provider
- `ctx.test_data`: Dict for storing test data

### `TestResult`

Result of a test execution.

**Attributes:**
- `test_name`: str
- `passed`: bool
- `duration_ms`: float
- `error`: Optional[str]
- `llm_response`: Optional[LLMResponse]
- `assertions`: List[Dict]
- `metadata`: Dict

### `TestSuite`

Collection of test results.

**Methods:**
- `add_result(result)`: Add test result
- `get_summary()`: Get summary dict

**Class Methods:**
- `LLMTest.get_suite(name)`: Get suite by name
- `LLMTest.get_all_suites()`: Get all suites
- `LLMTest.clear_results()`: Clear all results

---

## Assertions

### `expect(actual)`

Create expectation for fluent assertions.

### String Assertions

```python
expect(text).to_contain(substring, case_sensitive=True)
expect(text).not_to_contain(substring, case_sensitive=True)
expect(text).to_match_regex(pattern)
expect(text).to_start_with(prefix)
expect(text).to_end_with(suffix)
```

### Length Assertions

```python
expect(text).to_be_shorter_than(max_length, unit="chars")  # unit: chars|words|lines
expect(text).to_be_longer_than(min_length, unit="chars")
expect(text).to_be_between(min_length, max_length, unit="chars")
```

### Quality Assertions

```python
expect(text).to_be_concise(max_words=100)
expect(text).to_be_detailed(min_words=50)
expect(text).to_preserve_facts(facts: List[str], case_sensitive=False)
expect(text).not_to_hallucinate(source_text, threshold=0.3)
```

### Format Assertions

```python
expect(text).to_be_valid_json()
expect(text).to_match_schema(schema: dict)
expect(text).to_be_valid_markdown()
```

### Semantic Assertions

```python
expect(text).set_provider(provider).to_match_semantic(
    expected_meaning,
    threshold=0.8
)
```

### Comparison Assertions

```python
expect(value).to_equal(expected)
expect(value).to_be_true()
expect(value).to_be_false()
```

### Custom Assertions

```python
expect(value).to_satisfy(
    predicate: Callable[[Any], bool],
    message: str = ""
)
```

---

## Providers

### `OpenAIProvider`

OpenAI API provider.

```python
provider = OpenAIProvider(
    api_key: Optional[str] = None,  # or OPENAI_API_KEY env var
    model: str = "gpt-4-turbo",
    timeout: int = 60,
    max_retries: int = 3
)
```

**Methods:**
- `complete(prompt, temperature=0.7, max_tokens=None, **kwargs)`: Sync completion
- `acomplete(...)`: Async completion
- `stream(...)`: Streaming completion
- `count_tokens(text)`: Count tokens
- `calculate_cost(prompt_tokens, completion_tokens)`: Calculate cost
- `get_embedding(text, model="text-embedding-3-small")`: Get embeddings

### `AnthropicProvider`

Anthropic Claude API provider.

```python
provider = AnthropicProvider(
    api_key: Optional[str] = None,  # or ANTHROPIC_API_KEY env var
    model: str = "claude-3-5-sonnet-20241022",
    timeout: int = 60,
    max_retries: int = 3
)
```

**Methods:** Same as OpenAIProvider

### `LLMResponse`

Standard response from any provider.

**Attributes:**
- `content`: str - Response content
- `model`: str - Model used
- `provider`: str - Provider name
- `tokens_used`: int - Total tokens
- `prompt_tokens`: int
- `completion_tokens`: int
- `latency_ms`: float
- `cost_usd`: float
- `timestamp`: datetime
- `metadata`: Dict
- `raw_response`: Any

---

## Snapshot Testing

### `SnapshotManager`

Manage snapshot storage and comparison.

```python
manager = SnapshotManager(
    snapshot_dir: str = ".snapshots",
    update_mode: bool = False,
    semantic_threshold: float = 0.9
)
```

**Methods:**

```python
# Save snapshot
snapshot = manager.save_snapshot(name, content, metadata=None)

# Load snapshot
snapshot = manager.load_snapshot(name)

# Compare with snapshot
result = manager.compare(name, actual_content, metadata=None)

# Assert matches
manager.assert_matches_snapshot(name, actual_content, metadata=None)

# Management
snapshots = manager.list_snapshots()
manager.delete_snapshot(name)
count = manager.clear_all()
```

**Comparison Result:**
```python
{
    "matched": bool,
    "snapshot_exists": bool,
    "exact_match": bool,
    "similarity": float,
    "diff": str,  # if not matched
    "message": str
}
```

---

## Metrics Tracking

### `MetricsTracker`

Track and analyze LLM usage metrics.

```python
tracker = MetricsTracker()
```

**Methods:**

```python
# Track request
tracker.track_request(response: LLMResponse)

# Get summary
summary = tracker.get_summary()

# Print formatted summary
tracker.print_summary()

# Export
tracker.export_json(filepath)
tracker.export_csv(filepath)

# Analysis
breakdown = tracker.get_cost_breakdown()
slowest = tracker.get_slowest_requests(n=10)
expensive = tracker.get_most_expensive_requests(n=10)

# Clear
tracker.clear()
```

**MetricsSummary Attributes:**
- `total_requests`: int
- `total_tokens`: int
- `total_cost_usd`: float
- `avg_latency_ms`: float
- `p50_latency_ms`: float
- `p95_latency_ms`: float
- `p99_latency_ms`: float
- `by_model`: Dict
- `by_provider`: Dict

---

## RAG Testing

### `RAGTester`

Test retrieval-augmented generation systems.

```python
tester = RAGTester(
    retrieval_fn: Callable[[str], List[RetrievedDocument]],
    generation_fn: Callable[[str, List[RetrievedDocument]], str],
    relevance_threshold: float = 0.7
)
```

**Methods:**

```python
# Test query
result = tester.test_query(
    query: str,
    expected_sources: Optional[List[str]] = None,
    expected_facts: Optional[List[str]] = None
)

# Assertions
tester.assert_retrieval_quality(result, min_docs=1, min_relevance=None)
tester.assert_no_hallucination(result)
tester.assert_context_used(result)
tester.assert_performance(
    result,
    max_retrieval_ms=None,
    max_generation_ms=None,
    max_total_ms=None
)

# Benchmark
results = tester.benchmark_queries(queries, expected_data=None)
```

### `RetrievedDocument`

Document returned from retrieval.

```python
doc = RetrievedDocument(
    content: str,
    score: float,
    metadata: Dict[str, Any],
    source: Optional[str] = None
)
```

### `RAGTestResult`

Result of RAG test.

**Attributes:**
- `query`: str
- `retrieved_docs`: List[RetrievedDocument]
- `generated_response`: str
- `retrieval_time_ms`: float
- `generation_time_ms`: float
- `total_time_ms`: float
- `avg_relevance`: float
- `context_used`: bool
- `hallucination_detected`: bool

---

## Prompt Optimization

### `PromptOptimizer`

Optimize prompts through A/B testing.

```python
optimizer = PromptOptimizer(
    provider: BaseLLMProvider,
    quality_fn: Optional[Callable[[str], float]] = None
)
```

**Methods:**

```python
# Compare prompts
results = optimizer.compare_prompts(
    variants: List[PromptVariant],
    test_inputs: List[Dict[str, Any]],
    temperature: float = 0.7,
    runs_per_input: int = 1
)

# Find best
best_id = optimizer.find_best_prompt(
    results,
    optimize_for: str = "quality",  # quality|cost|latency|balanced
    quality_threshold: Optional[float] = None
)

# Print comparison
optimizer.print_comparison(results)

# Auto-optimize
optimization = optimizer.optimize_for_cost(
    base_prompt,
    test_inputs,
    min_quality=0.8
)

# Generate variants
variants = optimizer.generate_variants(
    base_prompt,
    num_variants=3,
    style="diverse"  # diverse|concise|detailed
)
```

### `PromptVariant`

A prompt variant for testing.

```python
variant = PromptVariant(
    id: str,
    template: str,
    description: str,
    metadata: Dict[str, Any] = {}
)
```

### `PromptTestResult`

Result of testing a prompt variant.

**Attributes:**
- `variant_id`: str
- `responses`: List[LLMResponse]
- `avg_tokens`: float
- `avg_cost`: float
- `avg_latency_ms`: float
- `quality_score`: Optional[float]
- `pass_rate`: Optional[float]

---

## Utilities

### Semantic Utilities

```python
from pyllmtest.utils.semantic import (
    calculate_semantic_similarity,
    find_most_similar,
    semantic_deduplication,
    cluster_texts
)

# Calculate similarity
similarity = calculate_semantic_similarity(text1, text2, provider)

# Find similar texts
matches = find_most_similar(query, candidates, provider, top_k=5)

# Remove duplicates
unique = semantic_deduplication(texts, provider, threshold=0.95)

# Cluster texts
clusters = cluster_texts(texts, provider, num_clusters=3)
```

---

## Error Handling

All assertions raise `AssertionError` with detailed messages:

```python
try:
    expect(response).to_contain("keyword")
except AssertionError as e:
    print(f"Assertion failed: {e}")
```

Provider errors raise `RuntimeError`:

```python
try:
    response = provider.complete("prompt")
except RuntimeError as e:
    print(f"Provider error: {e}")
```

---

## Best Practices

### 1. Use Context Manager Pattern

```python
@LLMTest(provider=provider)
def test_something(ctx):
    # ctx automatically tracks metrics
    response = ctx.complete("query")
```

### 2. Organize Tests in Suites

```python
@LLMTest(provider=provider, suite="nlp")
def test_sentiment(ctx):
    ...

@LLMTest(provider=provider, suite="nlp")
def test_entity(ctx):
    ...
```

### 3. Use Snapshots for Regression Testing

```python
snapshots = SnapshotManager(update_mode=False)

@LLMTest(provider=provider)
def test_output(ctx):
    response = ctx.complete("query")
    snapshots.assert_matches_snapshot("test_name", response.content)
```

### 4. Track All Metrics

```python
metrics = MetricsTracker()

# Tests automatically track when using ctx
@LLMTest(provider=provider)
def test(ctx):
    response = ctx.complete("query")  # Auto-tracked

# Manual tracking
metrics.track_request(response)
```

### 5. Use Semantic Assertions

```python
# Instead of exact matching
expect(response).to_contain("machine learning")

# Use semantic matching
expect(response).set_provider(provider).to_match_semantic(
    "discusses machine learning concepts",
    threshold=0.8
)
```

---

## Environment Variables

```bash
# Required for OpenAI
export OPENAI_API_KEY=your-key

# Required for Anthropic
export ANTHROPIC_API_KEY=your-key
```

---

## Examples

See the `examples/` directory for:
- `comprehensive_example.py` - All features
- `basic_testing.py` - Getting started
- `rag_testing.py` - RAG patterns
- `prompt_optimization.py` - Optimization
- `async_testing.py` - Async patterns

---

For more information, see the [README](README.md) and [Quick Start Guide](QUICKSTART.md).
