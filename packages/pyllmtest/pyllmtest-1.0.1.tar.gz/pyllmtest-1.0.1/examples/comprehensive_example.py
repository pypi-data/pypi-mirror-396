"""
Comprehensive PyLLMTest Example
================================
Demonstrates all major features of the framework.
"""

import asyncio
from llmtest import (
    LLMTest,
    expect,
    OpenAIProvider,
    AnthropicProvider,
    SnapshotManager,
    MetricsTracker,
    RAGTester,
    PromptOptimizer,
    PromptVariant,
    RetrievedDocument
)


# =============================================================================
# Example 1: Basic Testing with Assertions
# =============================================================================

def example_basic_testing():
    """Basic test with assertions"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Testing")
    print("="*60)
    
    provider = OpenAIProvider(model="gpt-3.5-turbo")
    
    @LLMTest(provider=provider, name="test_summarization")
    def test_summarization(ctx):
        # Test summarization
        long_text = """
        Artificial Intelligence has revolutionized many industries in recent years.
        Machine learning models can now perform tasks that were previously thought
        to require human intelligence. Deep learning has enabled breakthroughs in
        computer vision, natural language processing, and robotics.
        """
        
        response = ctx.complete(f"Summarize this in one sentence: {long_text}")
        
        # Assertions
        expect(response.content).to_be_shorter_than(50, unit="words")
        expect(response.content).to_contain("AI", case_sensitive=False)
        expect(response.content).to_preserve_facts(["intelligence", "learning"])
    
    # Run test
    result = test_summarization()
    print(f"Test Result: {'✓ PASSED' if result.passed else '✗ FAILED'}")
    if result.error:
        print(f"Error: {result.error}")


# =============================================================================
# Example 2: Snapshot Testing
# =============================================================================

def example_snapshot_testing():
    """Snapshot testing for regression detection"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Snapshot Testing")
    print("="*60)
    
    provider = OpenAIProvider(model="gpt-3.5-turbo")
    snapshot_mgr = SnapshotManager(snapshot_dir=".test_snapshots")
    
    @LLMTest(provider=provider)
    def test_with_snapshot(ctx):
        response = ctx.complete("What are the three primary colors?")
        
        # Save/compare with snapshot
        snapshot_mgr.assert_matches_snapshot(
            name="primary_colors_response",
            actual_content=response.content
        )
    
    result = test_with_snapshot()
    print(f"Snapshot Test: {'✓ MATCHED' if result.passed else '✗ MISMATCH'}")


# =============================================================================
# Example 3: Async Testing
# =============================================================================

async def example_async_testing():
    """Async test execution"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Async Testing")
    print("="*60)
    
    provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
    
    @LLMTest(provider=provider)
    async def test_async_completion(ctx):
        # Multiple async completions
        tasks = [
            ctx.acomplete("What is Python?"),
            ctx.acomplete("What is JavaScript?"),
            ctx.acomplete("What is Rust?")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for resp in responses:
            expect(resp.content).to_be_longer_than(20, unit="words")
    
    result = await test_async_completion()
    print(f"Async Test: {'✓ PASSED' if result.passed else '✗ FAILED'}")


# =============================================================================
# Example 4: Metrics Tracking
# =============================================================================

def example_metrics_tracking():
    """Track and analyze metrics"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Metrics Tracking")
    print("="*60)
    
    provider = OpenAIProvider(model="gpt-4-turbo")
    metrics = MetricsTracker()
    
    # Simulate multiple requests
    queries = [
        "Explain quantum computing",
        "What is machine learning?",
        "How do neural networks work?"
    ]
    
    for query in queries:
        response = provider.complete(query, max_tokens=100)
        metrics.track_request(response)
    
    # Print metrics summary
    metrics.print_summary()
    
    # Export metrics
    metrics.export_json("metrics_report.json")


# =============================================================================
# Example 5: RAG Testing
# =============================================================================

def example_rag_testing():
    """Test RAG system"""
    print("\n" + "="*60)
    print("EXAMPLE 5: RAG Testing")
    print("="*60)
    
    # Mock retrieval function
    def mock_retrieval(query: str):
        # In real scenario, this would query a vector database
        return [
            RetrievedDocument(
                content="Python is a high-level programming language.",
                score=0.95,
                metadata={"source": "doc1.txt"},
                source="doc1.txt"
            ),
            RetrievedDocument(
                content="Python supports multiple programming paradigms.",
                score=0.87,
                metadata={"source": "doc2.txt"},
                source="doc2.txt"
            )
        ]
    
    # Mock generation function
    def mock_generation(query: str, docs: list):
        provider = OpenAIProvider()
        context = "\n".join(doc.content for doc in docs)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        response = provider.complete(prompt)
        return response.content
    
    # Create RAG tester
    rag_tester = RAGTester(
        retrieval_fn=mock_retrieval,
        generation_fn=mock_generation
    )
    
    # Test a query
    result = rag_tester.test_query(
        query="What is Python?",
        expected_facts=["programming", "language"]
    )
    
    print(f"Retrieval Time: {result.retrieval_time_ms:.2f}ms")
    print(f"Generation Time: {result.generation_time_ms:.2f}ms")
    print(f"Avg Relevance: {result.avg_relevance:.2f}")
    print(f"Context Used: {result.context_used}")
    print(f"Hallucination: {result.hallucination_detected}")
    
    # Run assertions
    rag_tester.assert_retrieval_quality(result, min_docs=2, min_relevance=0.8)
    rag_tester.assert_context_used(result)
    rag_tester.assert_no_hallucination(result)


# =============================================================================
# Example 6: Prompt Optimization
# =============================================================================

def example_prompt_optimization():
    """Optimize prompts for cost and quality"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Prompt Optimization")
    print("="*60)
    
    provider = OpenAIProvider(model="gpt-3.5-turbo")
    
    # Define quality function
    def quality_fn(response: str) -> float:
        # Simple quality metric: check if response is detailed enough
        word_count = len(response.split())
        if word_count < 20:
            return 0.3
        elif word_count < 50:
            return 0.7
        else:
            return 1.0
    
    optimizer = PromptOptimizer(provider=provider, quality_fn=quality_fn)
    
    # Define variants to test
    variants = [
        PromptVariant(
            id="verbose",
            template="Please provide a detailed explanation of {topic}. Include examples.",
            description="Verbose prompt"
        ),
        PromptVariant(
            id="concise",
            template="Explain {topic} briefly.",
            description="Concise prompt"
        ),
        PromptVariant(
            id="balanced",
            template="Explain {topic} with examples.",
            description="Balanced prompt"
        )
    ]
    
    # Test inputs
    test_inputs = [
        {"topic": "machine learning"},
        {"topic": "neural networks"},
        {"topic": "deep learning"}
    ]
    
    # Compare prompts
    results = optimizer.compare_prompts(variants, test_inputs)
    
    # Print comparison
    optimizer.print_comparison(results)
    
    # Find best prompt
    best_id = optimizer.find_best_prompt(results, optimize_for="balanced")
    print(f"Best Prompt: {best_id}")


# =============================================================================
# Example 7: Test Suites and Reporting
# =============================================================================

def example_test_suites():
    """Organize tests in suites"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Test Suites")
    print("="*60)
    
    provider = OpenAIProvider(model="gpt-3.5-turbo")
    
    # Define multiple tests in a suite
    @LLMTest(provider=provider, suite="nlp_tests", name="test_sentiment")
    def test_sentiment(ctx):
        response = ctx.complete("Analyze sentiment: I love this product!")
        expect(response.content).to_contain("positive", case_sensitive=False)
    
    @LLMTest(provider=provider, suite="nlp_tests", name="test_entity_extraction")
    def test_entity_extraction(ctx):
        response = ctx.complete("Extract entities: Apple released iPhone 15 in Cupertino")
        expect(response.content).to_preserve_facts(["Apple", "iPhone"])
    
    @LLMTest(provider=provider, suite="nlp_tests", name="test_translation")
    def test_translation(ctx):
        response = ctx.complete("Translate to Spanish: Hello, how are you?")
        expect(response.content).to_contain("Hola", case_sensitive=False)
    
    # Run all tests
    test_sentiment()
    test_entity_extraction()
    test_translation()
    
    # Get suite summary
    suite = LLMTest.get_suite("nlp_tests")
    summary = suite.get_summary()
    
    print(f"\nSuite: {summary['name']}")
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"Total Cost: ${summary['total_cost_usd']:.4f}")


# =============================================================================
# Main Execution
# =============================================================================

def run_all_examples():
    """Run all examples"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PyLLMTest - Comprehensive Examples".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    try:
        # Run examples
        example_basic_testing()
        example_snapshot_testing()
        example_metrics_tracking()
        example_rag_testing()
        example_prompt_optimization()
        example_test_suites()
        
        # Run async example
        print("\n" + "="*60)
        print("Running async example...")
        asyncio.run(example_async_testing())
        
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█" + "  All Examples Completed!".center(58) + "█")
        print("█" + " "*58 + "█")
        print("█"*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
