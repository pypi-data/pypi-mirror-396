"""
RAG Testing Utilities
=====================
Test retrieval-augmented generation systems.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class RetrievedDocument:
    """A document retrieved from RAG system"""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: Optional[str] = None


@dataclass
class RAGTestResult:
    """Result of RAG test"""
    query: str
    retrieved_docs: List[RetrievedDocument]
    generated_response: str
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    relevance_scores: List[float]
    avg_relevance: float
    context_used: bool
    hallucination_detected: bool
    metadata: Dict[str, Any]


class RAGTester:
    """
    Comprehensive RAG system testing.
    
    Tests:
    - Retrieval quality
    - Context relevance
    - Response accuracy
    - Hallucination detection
    - Latency and performance
    """
    
    def __init__(
        self,
        retrieval_fn: Callable[[str], List[RetrievedDocument]],
        generation_fn: Callable[[str, List[RetrievedDocument]], str],
        relevance_threshold: float = 0.7
    ):
        """
        Initialize RAG tester.
        
        Args:
            retrieval_fn: Function that takes query and returns retrieved docs
            generation_fn: Function that takes query and docs, returns response
            relevance_threshold: Minimum relevance score for retrieved docs
        """
        self.retrieval_fn = retrieval_fn
        self.generation_fn = generation_fn
        self.relevance_threshold = relevance_threshold
    
    def test_query(
        self,
        query: str,
        expected_sources: Optional[List[str]] = None,
        expected_facts: Optional[List[str]] = None
    ) -> RAGTestResult:
        """
        Test a single query through RAG pipeline.
        
        Args:
            query: User query
            expected_sources: Expected source documents
            expected_facts: Expected facts in response
            
        Returns:
            RAGTestResult object
        """
        # Retrieval phase
        retrieval_start = time.time()
        retrieved_docs = self.retrieval_fn(query)
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        # Generation phase
        generation_start = time.time()
        response = self.generation_fn(query, retrieved_docs)
        generation_time = (time.time() - generation_start) * 1000
        
        # Analyze results
        relevance_scores = [doc.score for doc in retrieved_docs]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
        # Check if context was used
        context_used = self._check_context_usage(response, retrieved_docs)
        
        # Check for hallucinations
        hallucination = self._detect_hallucination(response, retrieved_docs, expected_facts)
        
        return RAGTestResult(
            query=query,
            retrieved_docs=retrieved_docs,
            generated_response=response,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            total_time_ms=retrieval_time + generation_time,
            relevance_scores=relevance_scores,
            avg_relevance=avg_relevance,
            context_used=context_used,
            hallucination_detected=hallucination,
            metadata={
                "num_docs_retrieved": len(retrieved_docs),
                "expected_sources_match": self._check_sources(retrieved_docs, expected_sources) if expected_sources else None
            }
        )
    
    def _check_context_usage(
        self,
        response: str,
        docs: List[RetrievedDocument]
    ) -> bool:
        """Check if response uses retrieved context"""
        # Simple heuristic: check if any doc content appears in response
        response_lower = response.lower()
        
        for doc in docs:
            # Check if key phrases from doc appear in response
            doc_words = set(doc.content.lower().split())
            response_words = set(response_lower.split())
            
            # If >30% of doc words appear in response, context was used
            overlap = len(doc_words & response_words)
            if overlap / len(doc_words) > 0.3:
                return True
        
        return False
    
    def _detect_hallucination(
        self,
        response: str,
        docs: List[RetrievedDocument],
        expected_facts: Optional[List[str]]
    ) -> bool:
        """
        Detect potential hallucinations.
        
        Checks if response contains information not in retrieved docs.
        """
        # Combine all doc content
        all_context = " ".join(doc.content for doc in docs).lower()
        
        # Check expected facts
        if expected_facts:
            for fact in expected_facts:
                if fact.lower() not in response.lower():
                    # Expected fact missing - might indicate hallucination or poor response
                    return True
        
        # Check if response makes claims not in context
        # This is a simple heuristic - in production you'd use more sophisticated methods
        response_sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 20]
        
        suspicious_count = 0
        for sentence in response_sentences[:5]:  # Check first 5 sentences
            # If sentence contains numbers/specific claims not in context
            if any(char.isdigit() for char in sentence):
                # Check if these numbers appear in context
                words = sentence.split()
                number_words = [w for w in words if any(c.isdigit() for c in w)]
                
                for num_word in number_words:
                    if num_word not in all_context:
                        suspicious_count += 1
        
        # If multiple suspicious claims, flag as potential hallucination
        return suspicious_count >= 2
    
    def _check_sources(
        self,
        retrieved_docs: List[RetrievedDocument],
        expected_sources: List[str]
    ) -> float:
        """
        Check if expected sources were retrieved.
        
        Returns:
            Match percentage (0.0 to 1.0)
        """
        if not expected_sources:
            return 1.0
        
        retrieved_sources = {doc.source for doc in retrieved_docs if doc.source}
        expected_set = set(expected_sources)
        
        matches = len(retrieved_sources & expected_set)
        return matches / len(expected_set)
    
    def assert_retrieval_quality(
        self,
        result: RAGTestResult,
        min_docs: int = 1,
        min_relevance: Optional[float] = None
    ):
        """
        Assert retrieval quality meets requirements.
        
        Args:
            result: RAGTestResult to check
            min_docs: Minimum number of documents
            min_relevance: Minimum average relevance score
        """
        if len(result.retrieved_docs) < min_docs:
            raise AssertionError(
                f"Expected at least {min_docs} documents, got {len(result.retrieved_docs)}"
            )
        
        relevance_threshold = min_relevance or self.relevance_threshold
        if result.avg_relevance < relevance_threshold:
            raise AssertionError(
                f"Average relevance {result.avg_relevance:.2f} below threshold {relevance_threshold:.2f}"
            )
    
    def assert_no_hallucination(self, result: RAGTestResult):
        """Assert that no hallucination was detected"""
        if result.hallucination_detected:
            raise AssertionError(
                f"Potential hallucination detected in response: {result.generated_response[:200]}..."
            )
    
    def assert_context_used(self, result: RAGTestResult):
        """Assert that retrieved context was used in response"""
        if not result.context_used:
            raise AssertionError(
                "Response does not appear to use retrieved context"
            )
    
    def assert_performance(
        self,
        result: RAGTestResult,
        max_retrieval_ms: Optional[float] = None,
        max_generation_ms: Optional[float] = None,
        max_total_ms: Optional[float] = None
    ):
        """
        Assert performance meets requirements.
        
        Args:
            result: RAGTestResult to check
            max_retrieval_ms: Max retrieval time
            max_generation_ms: Max generation time
            max_total_ms: Max total time
        """
        if max_retrieval_ms and result.retrieval_time_ms > max_retrieval_ms:
            raise AssertionError(
                f"Retrieval time {result.retrieval_time_ms:.2f}ms exceeds {max_retrieval_ms}ms"
            )
        
        if max_generation_ms and result.generation_time_ms > max_generation_ms:
            raise AssertionError(
                f"Generation time {result.generation_time_ms:.2f}ms exceeds {max_generation_ms}ms"
            )
        
        if max_total_ms and result.total_time_ms > max_total_ms:
            raise AssertionError(
                f"Total time {result.total_time_ms:.2f}ms exceeds {max_total_ms}ms"
            )
    
    def benchmark_queries(
        self,
        queries: List[str],
        expected_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Benchmark multiple queries.
        
        Args:
            queries: List of queries to test
            expected_data: Optional list of expected data per query
            
        Returns:
            Benchmark results dictionary
        """
        results = []
        
        for i, query in enumerate(queries):
            expected = expected_data[i] if expected_data and i < len(expected_data) else {}
            
            result = self.test_query(
                query,
                expected_sources=expected.get("sources"),
                expected_facts=expected.get("facts")
            )
            results.append(result)
        
        # Calculate aggregate metrics
        return {
            "total_queries": len(queries),
            "avg_retrieval_time_ms": sum(r.retrieval_time_ms for r in results) / len(results),
            "avg_generation_time_ms": sum(r.generation_time_ms for r in results) / len(results),
            "avg_total_time_ms": sum(r.total_time_ms for r in results) / len(results),
            "avg_relevance": sum(r.avg_relevance for r in results) / len(results),
            "context_usage_rate": sum(r.context_used for r in results) / len(results),
            "hallucination_rate": sum(r.hallucination_detected for r in results) / len(results),
            "results": results
        }
