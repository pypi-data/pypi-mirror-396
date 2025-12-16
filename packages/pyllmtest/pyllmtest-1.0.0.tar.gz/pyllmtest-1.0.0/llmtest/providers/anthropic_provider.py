"""
Anthropic Provider Implementation
==================================
Complete integration with Anthropic's Claude API.
"""

import os
import time
from typing import Optional, AsyncIterator, Dict, Any

from llmtest.providers.base import BaseLLMProvider, LLMResponse, StreamChunk


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider with support for:
    - Claude 3 Opus, Sonnet, Haiku
    - Claude 3.5 Sonnet
    - Streaming
    - Token counting
    - Accurate cost calculation
    """
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus": {"prompt": 15.00, "completion": 75.00},
        "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
        "claude-3-sonnet": {"prompt": 3.00, "completion": 15.00},
        "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(api_key, model, timeout, max_retries, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key parameter.")
        
        # Lazy import to avoid dependency issues
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout)
            self.async_client = anthropic.AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Synchronous completion using Anthropic Claude"""
        start_time = time.time()
        
        if max_tokens is None:
            max_tokens = 4096
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            content = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            tokens_used = prompt_tokens + completion_tokens
            
            latency_ms = self._measure_latency(start_time)
            
            return self._create_response(
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=response,
                metadata={
                    "stop_reason": response.stop_reason,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic completion failed: {str(e)}")
    
    async def acomplete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Async completion using Anthropic Claude"""
        start_time = time.time()
        
        if max_tokens is None:
            max_tokens = 4096
        
        try:
            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            content = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            tokens_used = prompt_tokens + completion_tokens
            
            latency_ms = self._measure_latency(start_time)
            
            return self._create_response(
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=response,
                metadata={
                    "stop_reason": response.stop_reason,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic async completion failed: {str(e)}")
    
    async def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion chunks from Anthropic Claude"""
        
        if max_tokens is None:
            max_tokens = 4096
        
        try:
            full_content = ""
            tokens_so_far = 0
            
            async with self.async_client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    full_content += text
                    tokens_so_far = self.count_tokens(full_content)
                    
                    yield StreamChunk(
                        content=text,
                        is_final=False,
                        tokens_so_far=tokens_so_far,
                        metadata={"full_content": None}
                    )
                
                # Final chunk
                final_message = await stream.get_final_message()
                yield StreamChunk(
                    content="",
                    is_final=True,
                    tokens_so_far=tokens_so_far,
                    metadata={
                        "full_content": full_content,
                        "stop_reason": final_message.stop_reason
                    }
                )
                    
        except Exception as e:
            raise RuntimeError(f"Anthropic streaming failed: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens using Anthropic's token counting.
        Falls back to approximation if API call fails.
        """
        try:
            # Use Anthropic's token counting
            count = self.client.count_tokens(text)
            return count
        except:
            # Approximation: 1 token ≈ 3.5 characters for Claude
            return int(len(text) / 3.5)
    
    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost in USD based on current Anthropic pricing"""
        # Find matching pricing
        model_base = None
        for key in self.PRICING:
            if key in self.model:
                model_base = key
                break
        
        if not model_base:
            # Default to Sonnet pricing if unknown
            model_base = "claude-3-sonnet"
        
        pricing = self.PRICING[model_base]
        
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        
        return prompt_cost + completion_cost
