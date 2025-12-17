"""
LLM Cost Calculator Module

Calculates the cost of LLM API calls based on token usage,
model pricing, and caching strategies.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import importlib.resources


@dataclass
class LLMCostResult:
    """Results from LLM cost calculation."""
    daily_input_tokens: float
    daily_output_tokens: float
    daily_total_tokens: float
    monthly_input_tokens: float
    monthly_output_tokens: float
    monthly_total_tokens: float
    daily_input_cost: float
    daily_output_cost: float
    daily_total_cost: float
    monthly_input_cost: float
    monthly_output_cost: float
    monthly_total_cost: float
    cost_per_request: float
    tokens_saved_by_cache: float
    cost_saved_by_cache: float
    model: str
    provider: str


class LLMCostCalculator:
    """
    Calculator for LLM API costs.
    
    Supports multiple providers and models with configurable
    caching strategies for cost optimization.
    """
    
    def __init__(self, pricing_file: Optional[str] = None):
        """
        Initialize the LLM cost calculator.
        
        Args:
            pricing_file: Path to the pricing JSON file. 
                         Defaults to bundled pricing/models.json
        """
        if pricing_file is None:
            # Use package resources to find bundled pricing file
            try:
                import ai_infra_cost_estimator.pricing as pricing_pkg
                pricing_file = os.path.join(
                    os.path.dirname(pricing_pkg.__file__), 
                    'models.json'
                )
            except (ImportError, AttributeError):
                # Fallback for development
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                pricing_file = os.path.join(base_dir, 'pricing', 'models.json')
        
        self.pricing_data = self._load_pricing(pricing_file)
        self.models = self.pricing_data.get('models', {})
    
    def _load_pricing(self, pricing_file: str) -> Dict:
        """Load pricing data from JSON file."""
        try:
            with open(pricing_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Pricing file not found: {pricing_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in pricing file: {pricing_file}")
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Return all available models with their pricing."""
        return self.models
    
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        """
        Get input and output pricing for a model.
        
        Args:
            model: Model name (e.g., 'gpt-4o-mini')
            
        Returns:
            Tuple of (input_price_per_1k, output_price_per_1k)
        """
        if model not in self.models:
            available = ', '.join(self.models.keys())
            raise ValueError(f"Unknown model: {model}. Available: {available}")
        
        model_data = self.models[model]
        return model_data['input_per_1k'], model_data['output_per_1k']
    
    def calculate(
        self,
        requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        model: str,
        cache_hit_ratio: float = 0.0
    ) -> LLMCostResult:
        """
        Calculate LLM costs based on usage parameters.
        
        Args:
            requests_per_day: Number of API requests per day
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per request
            model: Model name (e.g., 'gpt-4o-mini')
            cache_hit_ratio: Ratio of requests served from cache (0.0 to 1.0)
            
        Returns:
            LLMCostResult with detailed cost breakdown
        """
        # Validate inputs
        if requests_per_day < 0:
            raise ValueError("requests_per_day must be non-negative")
        if avg_input_tokens < 0 or avg_output_tokens < 0:
            raise ValueError("Token counts must be non-negative")
        if not 0 <= cache_hit_ratio <= 1:
            raise ValueError("cache_hit_ratio must be between 0 and 1")
        
        # Get model pricing
        input_price, output_price = self.get_model_pricing(model)
        model_data = self.models[model]
        provider = model_data.get('provider', 'unknown')
        
        # Calculate effective requests (after cache)
        effective_requests = requests_per_day * (1 - cache_hit_ratio)
        
        # Calculate daily tokens
        daily_input_tokens = effective_requests * avg_input_tokens
        daily_output_tokens = effective_requests * avg_output_tokens
        daily_total_tokens = daily_input_tokens + daily_output_tokens
        
        # Calculate monthly tokens (30 days)
        monthly_input_tokens = daily_input_tokens * 30
        monthly_output_tokens = daily_output_tokens * 30
        monthly_total_tokens = daily_total_tokens * 30
        
        # Calculate daily costs
        daily_input_cost = (daily_input_tokens / 1000) * input_price
        daily_output_cost = (daily_output_tokens / 1000) * output_price
        daily_total_cost = daily_input_cost + daily_output_cost
        
        # Calculate monthly costs
        monthly_input_cost = daily_input_cost * 30
        monthly_output_cost = daily_output_cost * 30
        monthly_total_cost = daily_total_cost * 30
        
        # Calculate cost per request
        cost_per_request = daily_total_cost / requests_per_day if requests_per_day > 0 else 0
        
        # Calculate cache savings
        tokens_without_cache = requests_per_day * (avg_input_tokens + avg_output_tokens)
        tokens_saved = (tokens_without_cache - daily_total_tokens) * 30
        
        cost_without_cache = (
            (requests_per_day * avg_input_tokens / 1000 * input_price) +
            (requests_per_day * avg_output_tokens / 1000 * output_price)
        ) * 30
        cost_saved = cost_without_cache - monthly_total_cost
        
        return LLMCostResult(
            daily_input_tokens=daily_input_tokens,
            daily_output_tokens=daily_output_tokens,
            daily_total_tokens=daily_total_tokens,
            monthly_input_tokens=monthly_input_tokens,
            monthly_output_tokens=monthly_output_tokens,
            monthly_total_tokens=monthly_total_tokens,
            daily_input_cost=daily_input_cost,
            daily_output_cost=daily_output_cost,
            daily_total_cost=daily_total_cost,
            monthly_input_cost=monthly_input_cost,
            monthly_output_cost=monthly_output_cost,
            monthly_total_cost=monthly_total_cost,
            cost_per_request=cost_per_request,
            tokens_saved_by_cache=tokens_saved,
            cost_saved_by_cache=cost_saved,
            model=model,
            provider=provider
        )
    
    def compare_models(
        self,
        requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        cache_hit_ratio: float = 0.0,
        models: Optional[list] = None
    ) -> Dict[str, LLMCostResult]:
        """
        Compare costs across multiple models.
        
        Args:
            requests_per_day: Number of API requests per day
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per request
            cache_hit_ratio: Ratio of requests served from cache
            models: List of models to compare. Defaults to all available.
            
        Returns:
            Dictionary mapping model names to their cost results
        """
        if models is None:
            models = list(self.models.keys())
        
        results = {}
        for model in models:
            if model in self.models:
                results[model] = self.calculate(
                    requests_per_day=requests_per_day,
                    avg_input_tokens=avg_input_tokens,
                    avg_output_tokens=avg_output_tokens,
                    model=model,
                    cache_hit_ratio=cache_hit_ratio
                )
        
        return results
    
    def estimate_cache_savings(
        self,
        requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        model: str,
        cache_hit_ratios: list = None
    ) -> Dict[float, float]:
        """
        Estimate savings at different cache hit ratios.
        
        Args:
            requests_per_day: Number of API requests per day
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per request
            model: Model name
            cache_hit_ratios: List of cache hit ratios to evaluate
            
        Returns:
            Dictionary mapping cache hit ratio to monthly savings
        """
        if cache_hit_ratios is None:
            cache_hit_ratios = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        
        baseline = self.calculate(
            requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            cache_hit_ratio=0.0
        )
        
        savings = {}
        for ratio in cache_hit_ratios:
            result = self.calculate(
                requests_per_day=requests_per_day,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=ratio
            )
            savings[ratio] = baseline.monthly_total_cost - result.monthly_total_cost
        
        return savings
