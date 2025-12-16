"""
Metrics Tracking System
=======================
Track tokens, costs, latency, and performance metrics.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import statistics
import json
from pathlib import Path

from llmtest.providers.base import LLMResponse


@dataclass
class MetricsSummary:
    """Summary of tracked metrics"""
    total_requests: int
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    by_model: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class MetricsTracker:
    """
    Track and analyze LLM usage metrics.
    
    Features:
    - Token usage tracking
    - Cost calculation
    - Latency percentiles
    - Per-model and per-provider stats
    - Export to JSON/CSV
    """
    
    def __init__(self):
        self.requests: List[LLMResponse] = []
        self.start_time = datetime.now()
    
    def track_request(self, response: LLMResponse):
        """
        Track a single request.
        
        Args:
            response: LLMResponse object
        """
        self.requests.append(response)
    
    def get_summary(self) -> MetricsSummary:
        """
        Get comprehensive metrics summary.
        
        Returns:
            MetricsSummary object
        """
        if not self.requests:
            return MetricsSummary(
                total_requests=0,
                total_tokens=0,
                total_prompt_tokens=0,
                total_completion_tokens=0,
                total_cost_usd=0.0,
                avg_latency_ms=0.0,
                min_latency_ms=0.0,
                max_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                start_time=self.start_time.isoformat(),
                end_time=datetime.now().isoformat()
            )
        
        # Calculate aggregate metrics
        total_tokens = sum(r.tokens_used for r in self.requests)
        total_prompt_tokens = sum(r.prompt_tokens for r in self.requests)
        total_completion_tokens = sum(r.completion_tokens for r in self.requests)
        total_cost = sum(r.cost_usd for r in self.requests)
        
        latencies = [r.latency_ms for r in self.requests]
        latencies.sort()
        
        # Calculate percentiles
        def percentile(data: List[float], p: float) -> float:
            if not data:
                return 0.0
            k = (len(data) - 1) * p
            f = int(k)
            c = f + 1
            if c >= len(data):
                return data[-1]
            d0 = data[f] * (c - k)
            d1 = data[c] * (k - f)
            return d0 + d1
        
        # Group by model
        by_model = {}
        for req in self.requests:
            if req.model not in by_model:
                by_model[req.model] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "avg_latency_ms": 0.0
                }
            by_model[req.model]["requests"] += 1
            by_model[req.model]["tokens"] += req.tokens_used
            by_model[req.model]["cost_usd"] += req.cost_usd
        
        # Calculate averages for each model
        for model in by_model:
            model_requests = [r for r in self.requests if r.model == model]
            by_model[model]["avg_latency_ms"] = statistics.mean(
                r.latency_ms for r in model_requests
            )
        
        # Group by provider
        by_provider = {}
        for req in self.requests:
            if req.provider not in by_provider:
                by_provider[req.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost_usd": 0.0,
                    "avg_latency_ms": 0.0
                }
            by_provider[req.provider]["requests"] += 1
            by_provider[req.provider]["tokens"] += req.tokens_used
            by_provider[req.provider]["cost_usd"] += req.cost_usd
        
        # Calculate averages for each provider
        for provider in by_provider:
            provider_requests = [r for r in self.requests if r.provider == provider]
            by_provider[provider]["avg_latency_ms"] = statistics.mean(
                r.latency_ms for r in provider_requests
            )
        
        return MetricsSummary(
            total_requests=len(self.requests),
            total_tokens=total_tokens,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_cost_usd=total_cost,
            avg_latency_ms=statistics.mean(latencies),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p50_latency_ms=percentile(latencies, 0.50),
            p95_latency_ms=percentile(latencies, 0.95),
            p99_latency_ms=percentile(latencies, 0.99),
            by_model=by_model,
            by_provider=by_provider,
            start_time=self.start_time.isoformat(),
            end_time=datetime.now().isoformat()
        )
    
    def print_summary(self):
        """Print formatted metrics summary"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("METRICS SUMMARY")
        print("="*60)
        print(f"Total Requests: {summary.total_requests}")
        print(f"Total Tokens: {summary.total_tokens:,}")
        print(f"  Prompt Tokens: {summary.total_prompt_tokens:,}")
        print(f"  Completion Tokens: {summary.total_completion_tokens:,}")
        print(f"Total Cost: ${summary.total_cost_usd:.4f}")
        print(f"\nLatency:")
        print(f"  Average: {summary.avg_latency_ms:.2f}ms")
        print(f"  Min: {summary.min_latency_ms:.2f}ms")
        print(f"  Max: {summary.max_latency_ms:.2f}ms")
        print(f"  P50: {summary.p50_latency_ms:.2f}ms")
        print(f"  P95: {summary.p95_latency_ms:.2f}ms")
        print(f"  P99: {summary.p99_latency_ms:.2f}ms")
        
        if summary.by_model:
            print(f"\nBy Model:")
            for model, stats in summary.by_model.items():
                print(f"  {model}:")
                print(f"    Requests: {stats['requests']}")
                print(f"    Tokens: {stats['tokens']:,}")
                print(f"    Cost: ${stats['cost_usd']:.4f}")
                print(f"    Avg Latency: {stats['avg_latency_ms']:.2f}ms")
        
        if summary.by_provider:
            print(f"\nBy Provider:")
            for provider, stats in summary.by_provider.items():
                print(f"  {provider}:")
                print(f"    Requests: {stats['requests']}")
                print(f"    Tokens: {stats['tokens']:,}")
                print(f"    Cost: ${stats['cost_usd']:.4f}")
                print(f"    Avg Latency: {stats['avg_latency_ms']:.2f}ms")
        
        print("="*60 + "\n")
    
    def export_json(self, filepath: str):
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to output file
        """
        summary = self.get_summary()
        
        with open(filepath, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)
        
        print(f"Metrics exported to {filepath}")
    
    def export_csv(self, filepath: str):
        """
        Export detailed request log to CSV.
        
        Args:
            filepath: Path to output file
        """
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "timestamp", "model", "provider", "tokens_used",
                "prompt_tokens", "completion_tokens", "cost_usd",
                "latency_ms"
            ])
            
            # Data rows
            for req in self.requests:
                writer.writerow([
                    req.timestamp.isoformat(),
                    req.model,
                    req.provider,
                    req.tokens_used,
                    req.prompt_tokens,
                    req.completion_tokens,
                    req.cost_usd,
                    req.latency_ms
                ])
        
        print(f"Request log exported to {filepath}")
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """
        Get cost breakdown by model and provider.
        
        Returns:
            Dictionary with cost breakdowns
        """
        by_model = {}
        by_provider = {}
        
        for req in self.requests:
            # By model
            if req.model not in by_model:
                by_model[req.model] = 0.0
            by_model[req.model] += req.cost_usd
            
            # By provider
            if req.provider not in by_provider:
                by_provider[req.provider] = 0.0
            by_provider[req.provider] += req.cost_usd
        
        return {
            "by_model": by_model,
            "by_provider": by_provider,
            "total": sum(by_model.values())
        }
    
    def get_slowest_requests(self, n: int = 10) -> List[LLMResponse]:
        """
        Get the N slowest requests.
        
        Args:
            n: Number of requests to return
            
        Returns:
            List of slowest LLMResponse objects
        """
        sorted_requests = sorted(
            self.requests,
            key=lambda r: r.latency_ms,
            reverse=True
        )
        return sorted_requests[:n]
    
    def get_most_expensive_requests(self, n: int = 10) -> List[LLMResponse]:
        """
        Get the N most expensive requests.
        
        Args:
            n: Number of requests to return
            
        Returns:
            List of most expensive LLMResponse objects
        """
        sorted_requests = sorted(
            self.requests,
            key=lambda r: r.cost_usd,
            reverse=True
        )
        return sorted_requests[:n]
    
    def clear(self):
        """Clear all tracked metrics"""
        self.requests.clear()
        self.start_time = datetime.now()
