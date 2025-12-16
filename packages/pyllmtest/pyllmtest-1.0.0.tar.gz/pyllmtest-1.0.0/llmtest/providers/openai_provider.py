"""
OpenAI Provider Implementation
===============================
Complete integration with OpenAI's API including GPT-4, GPT-3.5, and embeddings.
"""

import os
import time
from typing import Optional, AsyncIterator, Dict, Any
import asyncio

from llmtest.providers.base import BaseLLMProvider, LLMResponse, StreamChunk


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider with support for:
    - GPT-4, GPT-4-turbo, GPT-3.5-turbo
    - Streaming
    - Token counting with tiktoken
    - Accurate cost calculation
    """
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4": {"prompt": 30.00, "completion": 60.00},
        "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
        "gpt-4-turbo-preview": {"prompt": 10.00, "completion": 30.00},
        "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
        "gpt-3.5-turbo-16k": {"prompt": 3.00, "completion": 4.00},
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(api_key, model, timeout, max_retries, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        # Lazy import to avoid dependency issues
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key, timeout=self.timeout)
            self.async_client = openai.AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        # For token counting
        try:
            import tiktoken
            self.tiktoken = tiktoken
            self.encoder = tiktoken.encoding_for_model(self.model)
        except ImportError:
            print("Warning: tiktoken not installed. Token counting will be approximate.")
            self.tiktoken = None
            self.encoder = None
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Synchronous completion using OpenAI"""
        start_time = time.time()
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            tokens_used = response.usage.total_tokens
            
            latency_ms = self._measure_latency(start_time)
            
            return self._create_response(
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=response,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI completion failed: {str(e)}")
    
    async def acomplete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Async completion using OpenAI"""
        start_time = time.time()
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            tokens_used = response.usage.total_tokens
            
            latency_ms = self._measure_latency(start_time)
            
            return self._create_response(
                content=content,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=response,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI async completion failed: {str(e)}")
    
    async def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion chunks from OpenAI"""
        messages = [{"role": "user", "content": prompt}]
        
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            full_content = ""
            tokens_so_far = 0
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    tokens_so_far = self.count_tokens(full_content)
                    
                    is_final = chunk.choices[0].finish_reason is not None
                    
                    yield StreamChunk(
                        content=content,
                        is_final=is_final,
                        tokens_so_far=tokens_so_far,
                        metadata={
                            "finish_reason": chunk.choices[0].finish_reason,
                            "full_content": full_content if is_final else None
                        }
                    )
                    
        except Exception as e:
            raise RuntimeError(f"OpenAI streaming failed: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4
    
    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost in USD based on current OpenAI pricing"""
        # Find matching pricing
        model_base = self.model.split("-")[0:2]  # e.g., ["gpt", "4"]
        model_key = "-".join(model_base)
        
        pricing = None
        for key in self.PRICING:
            if model_key in key:
                pricing = self.PRICING[key]
                break
        
        if not pricing:
            # Default to GPT-4 pricing if unknown
            pricing = self.PRICING["gpt-4"]
        
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> list:
        """
        Get embedding vector for text.
        
        Args:
            text: Input text
            model: Embedding model to use
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"OpenAI embedding failed: {str(e)}")
