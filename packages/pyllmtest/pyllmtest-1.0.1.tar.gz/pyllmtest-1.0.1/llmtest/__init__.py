"""
PyLLMTest - The Most Comprehensive LLM Testing Framework
=========================================================

A revolutionary testing framework for LLM applications with:
- Semantic assertions and snapshot testing
- Multi-provider support (OpenAI, Anthropic, Local models)
- Performance benchmarking and cost tracking
- RAG testing utilities
- Automatic test generation
- Beautiful reporting and CLI

Author: Your Name
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.1"
__author__ = "Rahul Malik"

from llmtest.core.test_runner import LLMTest, llm_test
from llmtest.core.assertions import expect, assert_semantic_match
from llmtest.core.snapshot import SnapshotManager
from llmtest.metrics.tracker import MetricsTracker
from llmtest.providers.base import BaseLLMProvider
from llmtest.providers.openai_provider import OpenAIProvider
from llmtest.providers.anthropic_provider import AnthropicProvider
from llmtest.rag.testing import RAGTester
from llmtest.optimization.prompt_optimizer import PromptOptimizer

__all__ = [
    # Core testing
    "LLMTest",
    "llm_test",
    "expect",
    "assert_semantic_match",
    
    # Snapshot testing
    "SnapshotManager",
    
    # Metrics and tracking
    "MetricsTracker",
    
    # Providers
    "BaseLLMProvider",
    "OpenAIProvider", 
    "AnthropicProvider",
    
    # RAG testing
    "RAGTester",
    
    # Optimization
    "PromptOptimizer",
]
