"""
Core Test Runner
================
The heart of PyLLMTest - provides decorators and test execution.
"""

import functools
import asyncio
import inspect
from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import traceback

from llmtest.providers.base import BaseLLMProvider, LLMResponse
from llmtest.metrics.tracker import MetricsTracker


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    llm_response: Optional[LLMResponse] = None
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestSuite:
    """Collection of test results"""
    name: str
    results: List[TestResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    passed: int = 0
    failed: int = 0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    
    def add_result(self, result: TestResult):
        """Add a test result and update stats"""
        self.results.append(result)
        self.total_duration_ms += result.duration_ms
        
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1
        
        if result.llm_response:
            self.total_cost_usd += result.llm_response.cost_usd
            self.total_tokens += result.llm_response.tokens_used
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test suite summary"""
        total = self.passed + self.failed
        return {
            "name": self.name,
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": (self.passed / total * 100) if total > 0 else 0,
            "total_duration_ms": self.total_duration_ms,
            "avg_duration_ms": self.total_duration_ms / total if total > 0 else 0,
            "total_cost_usd": self.total_cost_usd,
            "total_tokens": self.total_tokens,
        }


class TestContext:
    """
    Context object passed to test functions.
    Provides access to provider, metrics, and utilities.
    """
    
    def __init__(
        self,
        provider: BaseLLMProvider,
        metrics_tracker: Optional[MetricsTracker] = None
    ):
        self.provider = provider
        self.metrics = metrics_tracker or MetricsTracker()
        self.test_data: Dict[str, Any] = {}
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Complete with automatic metrics tracking"""
        response = self.provider.complete(prompt, **kwargs)
        self.metrics.track_request(response)
        return response
    
    async def acomplete(self, prompt: str, **kwargs) -> LLMResponse:
        """Async complete with automatic metrics tracking"""
        response = await self.provider.acomplete(prompt, **kwargs)
        self.metrics.track_request(response)
        return response


class LLMTest:
    """
    Main test decorator and runner.
    
    Usage:
        @LLMTest(provider=OpenAIProvider(), name="My Test")
        def test_summarization(ctx):
            response = ctx.complete("Summarize: ...")
            expect(response.content).to_be_concise()
    """
    
    _test_suites: Dict[str, TestSuite] = {}
    _current_suite: Optional[str] = None
    
    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        name: Optional[str] = None,
        suite: str = "default",
        timeout: int = 60,
        retries: int = 0,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        self.provider = provider
        self.name = name
        self.suite = suite
        self.timeout = timeout
        self.retries = retries
        self.tags = tags or []
        self.kwargs = kwargs
        
        # Ensure suite exists
        if suite not in LLMTest._test_suites:
            LLMTest._test_suites[suite] = TestSuite(name=suite)
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation"""
        test_name = self.name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._run_test(func, test_name, args, kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self._run_test_async(func, test_name, args, kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    def _run_test(
        self,
        func: Callable,
        test_name: str,
        args: tuple,
        kwargs: dict
    ) -> TestResult:
        """Execute a synchronous test"""
        import time
        start_time = time.time()
        
        result = TestResult(
            test_name=test_name,
            passed=False,
            duration_ms=0.0
        )
        
        try:
            # Create context
            ctx = TestContext(provider=self.provider)
            
            # Run test
            func(ctx, *args, **kwargs)
            
            result.passed = True
            result.metadata = {"tags": self.tags}
            
        except AssertionError as e:
            result.passed = False
            result.error = str(e)
            result.error_traceback = traceback.format_exc()
            
        except Exception as e:
            result.passed = False
            result.error = f"Unexpected error: {str(e)}"
            result.error_traceback = traceback.format_exc()
        
        finally:
            result.duration_ms = (time.time() - start_time) * 1000
            
            # Add to suite
            suite = LLMTest._test_suites[self.suite]
            suite.add_result(result)
        
        return result
    
    async def _run_test_async(
        self,
        func: Callable,
        test_name: str,
        args: tuple,
        kwargs: dict
    ) -> TestResult:
        """Execute an asynchronous test"""
        import time
        start_time = time.time()
        
        result = TestResult(
            test_name=test_name,
            passed=False,
            duration_ms=0.0
        )
        
        try:
            # Create context
            ctx = TestContext(provider=self.provider)
            
            # Run test
            await func(ctx, *args, **kwargs)
            
            result.passed = True
            result.metadata = {"tags": self.tags}
            
        except AssertionError as e:
            result.passed = False
            result.error = str(e)
            result.error_traceback = traceback.format_exc()
            
        except Exception as e:
            result.passed = False
            result.error = f"Unexpected error: {str(e)}"
            result.error_traceback = traceback.format_exc()
        
        finally:
            result.duration_ms = (time.time() - start_time) * 1000
            
            # Add to suite
            suite = LLMTest._test_suites[self.suite]
            suite.add_result(result)
        
        return result
    
    @classmethod
    def get_suite(cls, name: str = "default") -> TestSuite:
        """Get a test suite by name"""
        return cls._test_suites.get(name)
    
    @classmethod
    def get_all_suites(cls) -> Dict[str, TestSuite]:
        """Get all test suites"""
        return cls._test_suites
    
    @classmethod
    def clear_results(cls):
        """Clear all test results"""
        cls._test_suites.clear()


# Convenience function
def llm_test(
    provider: Optional[BaseLLMProvider] = None,
    **kwargs
) -> Callable:
    """
    Convenience decorator for LLM tests.
    
    Usage:
        @llm_test(provider=OpenAIProvider())
        def test_something(ctx):
            ...
    """
    return LLMTest(provider=provider, **kwargs)
