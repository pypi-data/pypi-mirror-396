"""
Tests for AI Infra Cost Estimator

Run with: python -m pytest tests/ -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator.llm import LLMCostCalculator, LLMCostResult
from calculator.infra import InfraCostCalculator, InfraCostResult
from calculator.scaling import ScalingAnalyzer, ScalingAnalysisResult


class TestLLMCostCalculator:
    """Tests for LLM cost calculations."""
    
    @pytest.fixture
    def calculator(self):
        return LLMCostCalculator()
    
    def test_basic_calculation(self, calculator):
        """Test basic LLM cost calculation."""
        result = calculator.calculate(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.0
        )
        
        assert isinstance(result, LLMCostResult)
        assert result.monthly_total_cost > 0
        assert result.cost_per_request > 0
        assert result.model == "gpt-4o-mini"
        assert result.provider == "openai"
    
    def test_cache_reduces_cost(self, calculator):
        """Test that caching reduces costs."""
        no_cache = calculator.calculate(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.0
        )
        
        with_cache = calculator.calculate(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.5
        )
        
        assert with_cache.monthly_total_cost < no_cache.monthly_total_cost
        assert with_cache.cost_saved_by_cache > 0
    
    def test_invalid_model_raises_error(self, calculator):
        """Test that invalid model raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model"):
            calculator.calculate(
                requests_per_day=10000,
                avg_input_tokens=800,
                avg_output_tokens=400,
                model="invalid-model",
                cache_hit_ratio=0.0
            )
    
    def test_invalid_cache_ratio_raises_error(self, calculator):
        """Test that invalid cache ratio raises ValueError."""
        with pytest.raises(ValueError, match="cache_hit_ratio"):
            calculator.calculate(
                requests_per_day=10000,
                avg_input_tokens=800,
                avg_output_tokens=400,
                model="gpt-4o-mini",
                cache_hit_ratio=1.5
            )
    
    def test_compare_models(self, calculator):
        """Test model comparison."""
        results = calculator.compare_models(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            models=["gpt-4o-mini", "gpt-3.5-turbo"]
        )
        
        assert len(results) == 2
        assert "gpt-4o-mini" in results
        assert "gpt-3.5-turbo" in results
    
    def test_get_available_models(self, calculator):
        """Test getting available models."""
        models = calculator.get_available_models()
        
        assert len(models) > 0
        assert "gpt-4o-mini" in models
        assert "claude-3-haiku" in models


class TestInfraCostCalculator:
    """Tests for infrastructure cost calculations."""
    
    @pytest.fixture
    def calculator(self):
        return InfraCostCalculator()
    
    def test_basic_calculation(self, calculator):
        """Test basic infra cost calculation."""
        result = calculator.calculate(
            requests_per_day=10000,
            avg_latency_ms=500,
            concurrency_limit=50,
            region="us-east-1"
        )
        
        assert isinstance(result, InfraCostResult)
        assert result.total_monthly_cost > 0
        assert result.required_pods >= 1
        assert result.region == "us-east-1"
    
    def test_more_requests_need_more_pods(self, calculator):
        """Test that more requests require more pods."""
        low_traffic = calculator.calculate(
            requests_per_day=1000,
            avg_latency_ms=500,
            concurrency_limit=50,
            region="us-east-1"
        )
        
        high_traffic = calculator.calculate(
            requests_per_day=100000,
            avg_latency_ms=500,
            concurrency_limit=50,
            region="us-east-1"
        )
        
        assert high_traffic.required_pods >= low_traffic.required_pods
    
    def test_region_multiplier(self, calculator):
        """Test that region affects pricing."""
        us_result = calculator.calculate(
            requests_per_day=10000,
            region="us-east-1"
        )
        
        tokyo_result = calculator.calculate(
            requests_per_day=10000,
            region="ap-northeast-1"
        )
        
        # Tokyo has 1.2x multiplier
        assert tokyo_result.total_monthly_cost > us_result.total_monthly_cost
    
    def test_get_available_regions(self, calculator):
        """Test getting available regions."""
        regions = calculator.get_available_regions()
        
        assert len(regions) > 0
        assert "us-east-1" in regions
        assert "eu-west-1" in regions
    
    def test_get_available_instance_types(self, calculator):
        """Test getting available instance types."""
        instances = calculator.get_available_instance_types()
        
        assert len(instances) > 0
        assert "small" in instances
        assert "medium" in instances


class TestScalingAnalyzer:
    """Tests for scaling analysis."""
    
    @pytest.fixture
    def analyzer(self):
        return ScalingAnalyzer()
    
    def test_basic_analysis(self, analyzer):
        """Test basic scaling analysis."""
        result = analyzer.analyze(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.2,
            avg_latency_ms=500,
            concurrency_limit=50,
            region="us-east-1"
        )
        
        assert isinstance(result, ScalingAnalysisResult)
        assert result.current_state is not None
        assert "monthly_total_cost" in result.current_state
    
    def test_breakpoints_generated(self, analyzer):
        """Test that scaling breakpoints are generated."""
        result = analyzer.analyze(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.2
        )
        
        assert len(result.breakpoints) > 0
    
    def test_recommendations_generated(self, analyzer):
        """Test that recommendations are generated."""
        result = analyzer.analyze(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.1  # Low cache to trigger recommendation
        )
        
        # Should have at least cache improvement recommendation
        assert len(result.recommendations) > 0
    
    def test_cost_projections(self, analyzer):
        """Test cost projections at different growth rates."""
        result = analyzer.analyze(
            requests_per_day=10000,
            avg_input_tokens=800,
            avg_output_tokens=400,
            model="gpt-4o-mini",
            cache_hit_ratio=0.2
        )
        
        assert "1.5x" in result.cost_projection
        assert "2.0x" in result.cost_projection
        assert "3.0x" in result.cost_projection
        assert "5.0x" in result.cost_projection
        
        # Cost should increase with growth
        assert result.cost_projection["5.0x"]["monthly_cost"] > result.cost_projection["1.5x"]["monthly_cost"]


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_full_estimation_workflow(self):
        """Test complete estimation workflow."""
        # Initialize all components
        llm_calc = LLMCostCalculator()
        infra_calc = InfraCostCalculator()
        analyzer = ScalingAnalyzer()
        
        config = {
            "requests_per_day": 10000,
            "avg_input_tokens": 800,
            "avg_output_tokens": 400,
            "model": "gpt-4o-mini",
            "cache_hit_ratio": 0.2,
            "avg_latency_ms": 500,
            "concurrency_limit": 50,
            "region": "us-east-1"
        }
        
        # Calculate LLM costs
        llm_result = llm_calc.calculate(
            requests_per_day=config["requests_per_day"],
            avg_input_tokens=config["avg_input_tokens"],
            avg_output_tokens=config["avg_output_tokens"],
            model=config["model"],
            cache_hit_ratio=config["cache_hit_ratio"]
        )
        
        # Calculate infra costs
        infra_result = infra_calc.calculate(
            requests_per_day=config["requests_per_day"],
            avg_latency_ms=config["avg_latency_ms"],
            concurrency_limit=config["concurrency_limit"],
            region=config["region"]
        )
        
        # Run analysis
        analysis = analyzer.analyze(**config)
        
        # Verify results are consistent
        total_cost = llm_result.monthly_total_cost + infra_result.total_monthly_cost
        assert abs(total_cost - analysis.current_state["monthly_total_cost"]) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
