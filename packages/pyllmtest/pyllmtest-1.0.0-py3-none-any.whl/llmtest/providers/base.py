"""
Base LLM Provider Abstract Class
=================================
All LLM providers must inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class LLMResponse:
    """Standard response format from any LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: datetime
    metadata: Dict[str, Any]
    raw_response: Any


@dataclass
class StreamChunk:
    """Chunk from streaming response"""
    content: str
    is_final: bool
    tokens_so_far: int
    metadata: Dict[str, Any]


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    Provides standardized interface for:
    - Synchronous and asynchronous completions
    - Streaming responses
    - Token counting and cost calculation
    - Error handling and retries
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "default",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.kwargs = kwargs
        
    @abstractmethod
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Synchronous completion.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific arguments
            
        Returns:
            LLMResponse object
        """
        pass
    
    @abstractmethod
    async def acomplete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Async version of complete()"""
        pass
    
    @abstractmethod
    def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream completion chunks.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific arguments
            
        Yields:
            StreamChunk objects
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost in USD.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Cost in USD
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.__class__.__name__.replace("Provider", "")
    
    def _measure_latency(self, start_time: float) -> float:
        """Calculate latency in milliseconds"""
        return (time.time() - start_time) * 1000
    
    def _create_response(
        self,
        content: str,
        tokens_used: int,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        raw_response: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Helper to create standardized LLMResponse"""
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.get_provider_name(),
            tokens_used=tokens_used,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            cost_usd=self.calculate_cost(prompt_tokens, completion_tokens),
            timestamp=datetime.now(),
            metadata=metadata or {},
            raw_response=raw_response
        )
