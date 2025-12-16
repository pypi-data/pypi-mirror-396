"""
Comprehensive Assertion Library
================================
Semantic assertions, fuzzy matching, and LLM-specific validators.
"""

import re
import difflib
from typing import Any, List, Optional, Callable, Union
from dataclasses import dataclass
import json


class AssertionError(Exception):
    """Custom assertion error with detailed context"""
    pass


@dataclass
class AssertionResult:
    """Result of an assertion"""
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    details: Optional[dict] = None


class Expectation:
    """
    Fluent assertion interface.
    
    Usage:
        expect(text).to_contain("important")
        expect(text).to_be_shorter_than(100)
        expect(text).to_match_semantic("This is about AI")
    """
    
    def __init__(self, actual: Any):
        self.actual = actual
        self._provider = None  # For semantic matching
    
    def set_provider(self, provider):
        """Set LLM provider for semantic matching"""
        self._provider = provider
        return self
    
    # ==================== String Assertions ====================
    
    def to_contain(self, substring: str, case_sensitive: bool = True) -> 'Expectation':
        """Assert that text contains substring"""
        text = str(self.actual)
        search_text = text if case_sensitive else text.lower()
        search_sub = substring if case_sensitive else substring.lower()
        
        if search_sub not in search_text:
            raise AssertionError(
                f"Expected text to contain '{substring}'\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    def not_to_contain(self, substring: str, case_sensitive: bool = True) -> 'Expectation':
        """Assert that text does NOT contain substring"""
        text = str(self.actual)
        search_text = text if case_sensitive else text.lower()
        search_sub = substring if case_sensitive else substring.lower()
        
        if search_sub in search_text:
            raise AssertionError(
                f"Expected text NOT to contain '{substring}'\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    def to_match_regex(self, pattern: str) -> 'Expectation':
        """Assert that text matches regex pattern"""
        text = str(self.actual)
        if not re.search(pattern, text):
            raise AssertionError(
                f"Expected text to match pattern: {pattern}\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    def to_start_with(self, prefix: str) -> 'Expectation':
        """Assert that text starts with prefix"""
        text = str(self.actual)
        if not text.startswith(prefix):
            raise AssertionError(
                f"Expected text to start with '{prefix}'\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    def to_end_with(self, suffix: str) -> 'Expectation':
        """Assert that text ends with suffix"""
        text = str(self.actual)
        if not text.endswith(suffix):
            raise AssertionError(
                f"Expected text to end with '{suffix}'\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    # ==================== Length Assertions ====================
    
    def to_be_shorter_than(self, max_length: int, unit: str = "chars") -> 'Expectation':
        """Assert that text is shorter than max_length"""
        text = str(self.actual)
        
        if unit == "chars":
            length = len(text)
        elif unit == "words":
            length = len(text.split())
        elif unit == "lines":
            length = len(text.split('\n'))
        else:
            raise ValueError(f"Unknown unit: {unit}")
        
        if length >= max_length:
            raise AssertionError(
                f"Expected text to be shorter than {max_length} {unit}\n"
                f"Actual length: {length} {unit}"
            )
        return self
    
    def to_be_longer_than(self, min_length: int, unit: str = "chars") -> 'Expectation':
        """Assert that text is longer than min_length"""
        text = str(self.actual)
        
        if unit == "chars":
            length = len(text)
        elif unit == "words":
            length = len(text.split())
        elif unit == "lines":
            length = len(text.split('\n'))
        else:
            raise ValueError(f"Unknown unit: {unit}")
        
        if length <= min_length:
            raise AssertionError(
                f"Expected text to be longer than {min_length} {unit}\n"
                f"Actual length: {length} {unit}"
            )
        return self
    
    def to_be_between(self, min_length: int, max_length: int, unit: str = "chars") -> 'Expectation':
        """Assert that text length is between min and max"""
        text = str(self.actual)
        
        if unit == "chars":
            length = len(text)
        elif unit == "words":
            length = len(text.split())
        elif unit == "lines":
            length = len(text.split('\n'))
        else:
            raise ValueError(f"Unknown unit: {unit}")
        
        if not (min_length <= length <= max_length):
            raise AssertionError(
                f"Expected text to be between {min_length} and {max_length} {unit}\n"
                f"Actual length: {length} {unit}"
            )
        return self
    
    # ==================== Content Quality Assertions ====================
    
    def to_be_concise(self, max_words: int = 100) -> 'Expectation':
        """Assert that response is concise"""
        text = str(self.actual)
        word_count = len(text.split())
        
        if word_count > max_words:
            raise AssertionError(
                f"Expected response to be concise (max {max_words} words)\n"
                f"Actual word count: {word_count}"
            )
        return self
    
    def to_be_detailed(self, min_words: int = 50) -> 'Expectation':
        """Assert that response is detailed"""
        text = str(self.actual)
        word_count = len(text.split())
        
        if word_count < min_words:
            raise AssertionError(
                f"Expected response to be detailed (min {min_words} words)\n"
                f"Actual word count: {word_count}"
            )
        return self
    
    def to_preserve_facts(self, facts: List[str], case_sensitive: bool = False) -> 'Expectation':
        """Assert that all key facts are preserved in the text"""
        text = str(self.actual)
        search_text = text if case_sensitive else text.lower()
        
        missing_facts = []
        for fact in facts:
            search_fact = fact if case_sensitive else fact.lower()
            if search_fact not in search_text:
                missing_facts.append(fact)
        
        if missing_facts:
            raise AssertionError(
                f"Expected text to preserve all facts\n"
                f"Missing facts: {missing_facts}\n"
                f"Actual text: {text[:200]}..."
            )
        return self
    
    def not_to_hallucinate(self, source_text: str, threshold: float = 0.3) -> 'Expectation':
        """
        Assert that response doesn't contain information not in source.
        Uses fuzzy matching to detect potential hallucinations.
        """
        response = str(self.actual)
        
        # Extract key claims from response (sentences)
        response_sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 20]
        
        hallucinations = []
        for sentence in response_sentences[:10]:  # Check first 10 sentences
            # Check if sentence has any similarity to source
            similarity = difflib.SequenceMatcher(None, sentence.lower(), source_text.lower()).ratio()
            
            if similarity < threshold:
                hallucinations.append(sentence)
        
        if hallucinations:
            raise AssertionError(
                f"Detected potential hallucinations (statements not in source):\n"
                f"{hallucinations[0][:100]}...\n"
                f"Total suspicious sentences: {len(hallucinations)}"
            )
        return self
    
    # ==================== Format Assertions ====================
    
    def to_be_valid_json(self) -> 'Expectation':
        """Assert that text is valid JSON"""
        text = str(self.actual)
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Expected valid JSON\nError: {str(e)}")
        return self
    
    def to_match_schema(self, schema: dict) -> 'Expectation':
        """Assert that JSON matches schema"""
        text = str(self.actual)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise AssertionError("Text is not valid JSON")
        
        # Simple schema validation (check required keys)
        if "required" in schema:
            missing_keys = [key for key in schema["required"] if key not in data]
            if missing_keys:
                raise AssertionError(
                    f"JSON missing required keys: {missing_keys}\n"
                    f"Actual keys: {list(data.keys())}"
                )
        
        return self
    
    def to_be_valid_markdown(self) -> 'Expectation':
        """Assert that text is valid markdown"""
        text = str(self.actual)
        
        # Check for basic markdown elements
        has_headers = bool(re.search(r'^#{1,6}\s', text, re.MULTILINE))
        has_lists = bool(re.search(r'^[\*\-\+]\s', text, re.MULTILINE))
        has_code = bool(re.search(r'```', text))
        
        if not (has_headers or has_lists or has_code):
            raise AssertionError("Expected valid markdown formatting")
        
        return self
    
    # ==================== Semantic Assertions ====================
    
    def to_match_semantic(
        self,
        expected_meaning: str,
        threshold: float = 0.8
    ) -> 'Expectation':
        """
        Assert that text semantically matches expected meaning.
        Requires embeddings provider.
        """
        if not self._provider:
            raise RuntimeError("Semantic matching requires an LLM provider with embeddings")
        
        try:
            from llmtest.utils.semantic import calculate_semantic_similarity
            
            similarity = calculate_semantic_similarity(
                str(self.actual),
                expected_meaning,
                self._provider
            )
            
            if similarity < threshold:
                raise AssertionError(
                    f"Semantic similarity too low: {similarity:.2f} < {threshold}\n"
                    f"Expected meaning: {expected_meaning}\n"
                    f"Actual text: {str(self.actual)[:200]}..."
                )
        except ImportError:
            raise RuntimeError("Semantic matching requires numpy/scipy")
        
        return self
    
    # ==================== Comparison Assertions ====================
    
    def to_equal(self, expected: Any) -> 'Expectation':
        """Assert equality"""
        if self.actual != expected:
            raise AssertionError(
                f"Expected: {expected}\n"
                f"Actual: {self.actual}"
            )
        return self
    
    def to_be_true(self) -> 'Expectation':
        """Assert that value is truthy"""
        if not self.actual:
            raise AssertionError(f"Expected truthy value, got: {self.actual}")
        return self
    
    def to_be_false(self) -> 'Expectation':
        """Assert that value is falsy"""
        if self.actual:
            raise AssertionError(f"Expected falsy value, got: {self.actual}")
        return self
    
    # ==================== Custom Assertions ====================
    
    def to_satisfy(self, predicate: Callable[[Any], bool], message: str = "") -> 'Expectation':
        """Assert that value satisfies custom predicate"""
        if not predicate(self.actual):
            raise AssertionError(
                message or f"Value does not satisfy predicate: {self.actual}"
            )
        return self


def expect(actual: Any) -> Expectation:
    """
    Create an expectation for fluent assertions.
    
    Usage:
        expect(response).to_contain("AI")
        expect(text).to_be_shorter_than(100, unit="words")
    """
    return Expectation(actual)


def assert_semantic_match(
    actual: str,
    expected: str,
    provider,
    threshold: float = 0.8
) -> bool:
    """
    Direct semantic matching assertion.
    
    Args:
        actual: Actual text
        expected: Expected semantic meaning
        provider: LLM provider with embeddings
        threshold: Minimum similarity score
        
    Returns:
        True if match, raises AssertionError otherwise
    """
    return expect(actual).set_provider(provider).to_match_semantic(expected, threshold)
