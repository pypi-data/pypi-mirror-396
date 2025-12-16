"""
Prompt Optimization System
===========================
A/B test prompts, optimize for quality and cost.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import statistics

from llmtest.providers.base import BaseLLMProvider, LLMResponse


@dataclass
class PromptVariant:
    """A prompt variant for testing"""
    id: str
    template: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptTestResult:
    """Result of testing a prompt variant"""
    variant_id: str
    responses: List[LLMResponse]
    avg_tokens: float
    avg_cost: float
    avg_latency_ms: float
    quality_score: Optional[float] = None
    pass_rate: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptOptimizer:
    """
    Optimize prompts through A/B testing and analysis.
    
    Features:
    - A/B test multiple prompt variants
    - Quality scoring
    - Cost optimization
    - Automatic best prompt selection
    """
    
    def __init__(
        self,
        provider: BaseLLMProvider,
        quality_fn: Optional[Callable[[str], float]] = None
    ):
        """
        Initialize prompt optimizer.
        
        Args:
            provider: LLM provider for testing
            quality_fn: Optional function to score response quality (0-1)
        """
        self.provider = provider
        self.quality_fn = quality_fn
    
    def compare_prompts(
        self,
        variants: List[PromptVariant],
        test_inputs: List[Dict[str, Any]],
        temperature: float = 0.7,
        runs_per_input: int = 1
    ) -> Dict[str, PromptTestResult]:
        """
        Compare multiple prompt variants.
        
        Args:
            variants: List of prompt variants to test
            test_inputs: List of test input data
            temperature: Sampling temperature
            runs_per_input: Number of times to run each input
            
        Returns:
            Dictionary mapping variant_id to PromptTestResult
        """
        results = {}
        
        for variant in variants:
            print(f"Testing variant: {variant.id}")
            responses = []
            
            for input_data in test_inputs:
                for _ in range(runs_per_input):
                    # Format prompt with input data
                    prompt = variant.template.format(**input_data)
                    
                    # Get response
                    response = self.provider.complete(
                        prompt,
                        temperature=temperature
                    )
                    responses.append(response)
            
            # Calculate metrics
            avg_tokens = statistics.mean(r.tokens_used for r in responses)
            avg_cost = statistics.mean(r.cost_usd for r in responses)
            avg_latency = statistics.mean(r.latency_ms for r in responses)
            
            # Calculate quality if function provided
            quality_score = None
            if self.quality_fn:
                quality_scores = [self.quality_fn(r.content) for r in responses]
                quality_score = statistics.mean(quality_scores)
            
            results[variant.id] = PromptTestResult(
                variant_id=variant.id,
                responses=responses,
                avg_tokens=avg_tokens,
                avg_cost=avg_cost,
                avg_latency_ms=avg_latency,
                quality_score=quality_score,
                metadata=variant.metadata
            )
        
        return results
    
    def find_best_prompt(
        self,
        results: Dict[str, PromptTestResult],
        optimize_for: str = "quality",
        quality_threshold: Optional[float] = None
    ) -> str:
        """
        Find the best prompt based on optimization criteria.
        
        Args:
            results: Results from compare_prompts
            optimize_for: "quality", "cost", "latency", or "balanced"
            quality_threshold: Minimum quality score (if optimizing for cost/latency)
            
        Returns:
            Variant ID of best prompt
        """
        if not results:
            raise ValueError("No results to analyze")
        
        if optimize_for == "quality":
            # Find highest quality
            best = max(
                results.items(),
                key=lambda x: x[1].quality_score if x[1].quality_score else 0
            )
            return best[0]
        
        elif optimize_for == "cost":
            # Find lowest cost, optionally above quality threshold
            filtered = results
            if quality_threshold:
                filtered = {
                    k: v for k, v in results.items()
                    if v.quality_score and v.quality_score >= quality_threshold
                }
            
            if not filtered:
                raise ValueError("No variants meet quality threshold")
            
            best = min(filtered.items(), key=lambda x: x[1].avg_cost)
            return best[0]
        
        elif optimize_for == "latency":
            # Find lowest latency, optionally above quality threshold
            filtered = results
            if quality_threshold:
                filtered = {
                    k: v for k, v in results.items()
                    if v.quality_score and v.quality_score >= quality_threshold
                }
            
            if not filtered:
                raise ValueError("No variants meet quality threshold")
            
            best = min(filtered.items(), key=lambda x: x[1].avg_latency_ms)
            return best[0]
        
        elif optimize_for == "balanced":
            # Balance quality, cost, and latency
            def score_variant(result: PromptTestResult) -> float:
                quality = result.quality_score or 0.5
                # Normalize cost and latency (lower is better)
                cost_score = 1.0 / (1.0 + result.avg_cost * 100)  # Scale cost
                latency_score = 1.0 / (1.0 + result.avg_latency_ms / 1000)  # Scale latency
                
                # Weighted average (quality matters most)
                return 0.5 * quality + 0.3 * cost_score + 0.2 * latency_score
            
            best = max(results.items(), key=lambda x: score_variant(x[1]))
            return best[0]
        
        else:
            raise ValueError(f"Unknown optimization criterion: {optimize_for}")
    
    def print_comparison(self, results: Dict[str, PromptTestResult]):
        """Print formatted comparison of prompt variants"""
        print("\n" + "="*80)
        print("PROMPT COMPARISON")
        print("="*80)
        
        for variant_id, result in results.items():
            print(f"\nVariant: {variant_id}")
            print(f"  Avg Tokens: {result.avg_tokens:.1f}")
            print(f"  Avg Cost: ${result.avg_cost:.6f}")
            print(f"  Avg Latency: {result.avg_latency_ms:.2f}ms")
            if result.quality_score:
                print(f"  Quality Score: {result.quality_score:.2%}")
            if result.pass_rate:
                print(f"  Pass Rate: {result.pass_rate:.2%}")
        
        print("="*80 + "\n")
    
    def optimize_for_cost(
        self,
        base_prompt: str,
        test_inputs: List[Dict[str, Any]],
        min_quality: float = 0.8
    ) -> Dict[str, Any]:
        """
        Automatically generate and test cost-optimized variants.
        
        Tries:
        - Shorter prompts
        - More efficient phrasing
        - Removing redundancy
        
        Args:
            base_prompt: Original prompt
            test_inputs: Test input data
            min_quality: Minimum acceptable quality
            
        Returns:
            Dictionary with optimization results
        """
        variants = [
            PromptVariant(
                id="original",
                template=base_prompt,
                description="Original prompt"
            ),
            PromptVariant(
                id="concise",
                template=self._make_concise(base_prompt),
                description="Concise version"
            ),
            PromptVariant(
                id="direct",
                template=self._make_direct(base_prompt),
                description="More direct phrasing"
            )
        ]
        
        results = self.compare_prompts(variants, test_inputs)
        
        try:
            best_id = self.find_best_prompt(
                results,
                optimize_for="cost",
                quality_threshold=min_quality
            )
            
            best_result = results[best_id]
            original_result = results["original"]
            
            cost_savings = (
                (original_result.avg_cost - best_result.avg_cost) / original_result.avg_cost * 100
            )
            
            return {
                "best_variant_id": best_id,
                "best_prompt": next(v.template for v in variants if v.id == best_id),
                "cost_savings_percent": cost_savings,
                "original_cost": original_result.avg_cost,
                "optimized_cost": best_result.avg_cost,
                "quality_maintained": best_result.quality_score >= min_quality if best_result.quality_score else None,
                "all_results": results
            }
        
        except ValueError as e:
            return {
                "error": str(e),
                "message": "Could not find variant meeting quality threshold",
                "all_results": results
            }
    
    def _make_concise(self, prompt: str) -> str:
        """Make prompt more concise"""
        # Remove common filler phrases
        fillers = [
            "please",
            "kindly",
            "I would like you to",
            "I want you to",
            "Could you",
            "Can you"
        ]
        
        result = prompt
        for filler in fillers:
            result = result.replace(filler, "").replace(filler.capitalize(), "")
        
        # Remove extra whitespace
        result = " ".join(result.split())
        
        return result
    
    def _make_direct(self, prompt: str) -> str:
        """Make prompt more direct"""
        # Replace verbose phrases with direct commands
        replacements = {
            "I would like you to ": "",
            "Please ": "",
            "Could you please ": "",
            "Can you ": "",
            "I need you to ": "",
        }
        
        result = prompt
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result.strip()
    
    def generate_variants(
        self,
        base_prompt: str,
        num_variants: int = 3,
        style: str = "diverse"
    ) -> List[PromptVariant]:
        """
        Automatically generate prompt variants.
        
        Args:
            base_prompt: Original prompt
            num_variants: Number of variants to generate
            style: "diverse", "concise", or "detailed"
            
        Returns:
            List of PromptVariant objects
        """
        variants = [
            PromptVariant(
                id="original",
                template=base_prompt,
                description="Original prompt"
            )
        ]
        
        if style == "diverse" or style == "concise":
            variants.append(PromptVariant(
                id="concise",
                template=self._make_concise(base_prompt),
                description="Concise version"
            ))
        
        if style == "diverse" or style == "detailed":
            variants.append(PromptVariant(
                id="detailed",
                template=base_prompt + "\n\nProvide detailed explanation.",
                description="More detailed version"
            ))
        
        if len(variants) < num_variants:
            variants.append(PromptVariant(
                id="direct",
                template=self._make_direct(base_prompt),
                description="Direct version"
            ))
        
        return variants[:num_variants]
