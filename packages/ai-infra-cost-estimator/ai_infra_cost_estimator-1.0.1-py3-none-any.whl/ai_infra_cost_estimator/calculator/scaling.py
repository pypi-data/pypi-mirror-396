"""
Scaling Analyzer Module

Analyzes scaling thresholds, breakpoints, and provides
recommendations for cost optimization.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ai_infra_cost_estimator.calculator.llm import LLMCostCalculator, LLMCostResult
from ai_infra_cost_estimator.calculator.infra import InfraCostCalculator, InfraCostResult


@dataclass
class ScalingBreakpoint:
    """Represents a scaling breakpoint."""
    requests_per_day: int
    pods_required: int
    monthly_llm_cost: float
    monthly_infra_cost: float
    monthly_total_cost: float
    cost_per_request: float
    description: str
    is_significant: bool = False


@dataclass
class Recommendation:
    """A cost optimization recommendation."""
    title: str
    description: str
    potential_savings: float
    implementation_effort: str  # low, medium, high
    priority: str  # critical, high, medium, low
    category: str  # caching, scaling, model, infra


@dataclass
class ScalingAnalysisResult:
    """Results from scaling analysis."""
    current_state: Dict
    breakpoints: List[ScalingBreakpoint]
    recommendations: List[Recommendation]
    cost_projection: Dict
    scaling_alerts: List[str]
    optimization_potential: float


class ScalingAnalyzer:
    """
    Analyzer for scaling thresholds and cost optimization.
    
    Identifies cost breakpoints, scaling triggers, and provides
    actionable recommendations.
    """
    
    def __init__(self, pricing_file: Optional[str] = None):
        """
        Initialize the scaling analyzer.
        
        Args:
            pricing_file: Path to the pricing JSON file.
        """
        self.llm_calculator = LLMCostCalculator(pricing_file)
        self.infra_calculator = InfraCostCalculator(pricing_file)
    
    def find_pod_scaling_breakpoints(
        self,
        base_requests_per_day: int,
        avg_latency_ms: float,
        concurrency_limit: int,
        max_multiplier: float = 5.0,
        steps: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Find request volumes where pod count increases.
        """
        breakpoints = []
        last_pods = 0
        
        for i in range(steps + 1):
            multiplier = 1 + (max_multiplier - 1) * (i / steps)
            requests = int(base_requests_per_day * multiplier)
            
            _, _, pods = self.infra_calculator.calculate_required_pods(
                requests_per_day=requests,
                avg_latency_ms=avg_latency_ms,
                concurrency_limit=concurrency_limit
            )
            
            if pods > last_pods:
                breakpoints.append((requests, pods))
                last_pods = pods
        
        return breakpoints
    
    def find_cost_doubling_points(
        self,
        base_requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        model: str,
        avg_latency_ms: float,
        concurrency_limit: int,
        cache_hit_ratio: float = 0.0,
        region: str = "us-east-1"
    ) -> List[Dict]:
        """Find request volumes where total cost doubles."""
        llm_result = self.llm_calculator.calculate(
            requests_per_day=base_requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            cache_hit_ratio=cache_hit_ratio
        )
        
        infra_result = self.infra_calculator.calculate(
            requests_per_day=base_requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit,
            region=region
        )
        
        base_cost = llm_result.monthly_total_cost + infra_result.total_monthly_cost
        
        doubling_points = []
        target_cost = base_cost * 2
        multiplier = 1.0
        
        while multiplier < 20.0:
            multiplier += 0.1
            requests = int(base_requests_per_day * multiplier)
            
            llm = self.llm_calculator.calculate(
                requests_per_day=requests,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=cache_hit_ratio
            )
            
            infra = self.infra_calculator.calculate(
                requests_per_day=requests,
                avg_latency_ms=avg_latency_ms,
                concurrency_limit=concurrency_limit,
                region=region
            )
            
            total_cost = llm.monthly_total_cost + infra.total_monthly_cost
            
            if total_cost >= target_cost:
                doubling_points.append({
                    "requests_per_day": requests,
                    "multiplier": round(multiplier, 1),
                    "monthly_cost": total_cost,
                    "cost_increase": total_cost - base_cost
                })
                target_cost = total_cost * 2
        
        return doubling_points
    
    def generate_recommendations(
        self,
        requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        model: str,
        cache_hit_ratio: float,
        avg_latency_ms: float,
        concurrency_limit: int,
        region: str = "us-east-1"
    ) -> List[Recommendation]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        current_llm = self.llm_calculator.calculate(
            requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            cache_hit_ratio=cache_hit_ratio
        )
        
        current_infra = self.infra_calculator.calculate(
            requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit,
            region=region
        )
        
        # 1. Cache optimization
        if cache_hit_ratio < 0.5:
            target_cache = min(cache_hit_ratio + 0.2, 0.8)
            improved_llm = self.llm_calculator.calculate(
                requests_per_day=requests_per_day,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=target_cache
            )
            savings = current_llm.monthly_total_cost - improved_llm.monthly_total_cost
            
            if savings > 10:
                recommendations.append(Recommendation(
                    title=f"Improve cache hit ratio to {int(target_cache*100)}%",
                    description=f"Implement semantic caching or response deduplication to increase cache hits from {int(cache_hit_ratio*100)}% to {int(target_cache*100)}%",
                    potential_savings=savings,
                    implementation_effort="medium",
                    priority="high" if savings > 100 else "medium",
                    category="caching"
                ))
        
        # 2. Model alternatives
        all_models = self.llm_calculator.compare_models(
            requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            cache_hit_ratio=cache_hit_ratio
        )
        
        cheaper_models = []
        for model_name, result in all_models.items():
            if model_name != model and result.monthly_total_cost < current_llm.monthly_total_cost * 0.7:
                cheaper_models.append((model_name, result))
        
        if cheaper_models:
            cheaper_models.sort(key=lambda x: x[1].monthly_total_cost)
            best_alt = cheaper_models[0]
            savings = current_llm.monthly_total_cost - best_alt[1].monthly_total_cost
            
            recommendations.append(Recommendation(
                title=f"Consider switching to {best_alt[0]}",
                description=f"Model {best_alt[0]} could provide similar functionality at ${best_alt[1].monthly_total_cost:.2f}/month vs ${current_llm.monthly_total_cost:.2f}/month. Evaluate quality trade-offs.",
                potential_savings=savings,
                implementation_effort="low",
                priority="high" if savings > 200 else "medium",
                category="model"
            ))
        
        # 3. Token optimization
        if avg_input_tokens > 500:
            reduced_tokens = int(avg_input_tokens * 0.7)
            optimized_llm = self.llm_calculator.calculate(
                requests_per_day=requests_per_day,
                avg_input_tokens=reduced_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=cache_hit_ratio
            )
            savings = current_llm.monthly_total_cost - optimized_llm.monthly_total_cost
            
            if savings > 50:
                recommendations.append(Recommendation(
                    title="Optimize prompt length",
                    description=f"Reduce average input tokens from {avg_input_tokens} to ~{reduced_tokens} through prompt compression or dynamic context selection.",
                    potential_savings=savings,
                    implementation_effort="medium",
                    priority="medium",
                    category="model"
                ))
        
        # 4. Region optimization
        region_costs = self.infra_calculator.compare_regions(
            requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms
        )
        
        cheapest_region = min(region_costs.items(), key=lambda x: x[1].total_monthly_cost)
        if cheapest_region[0] != region:
            savings = current_infra.total_monthly_cost - cheapest_region[1].total_monthly_cost
            if savings > 20:
                recommendations.append(Recommendation(
                    title=f"Consider {cheapest_region[0]} region",
                    description=f"Moving to {cheapest_region[0]} could save ${savings:.2f}/month on infrastructure.",
                    potential_savings=savings,
                    implementation_effort="medium",
                    priority="low",
                    category="infra"
                ))
        
        # 5. Scaling efficiency
        if current_infra.utilization_percent < 50:
            recommendations.append(Recommendation(
                title="Review scaling configuration",
                description=f"Current utilization is {current_infra.utilization_percent:.1f}%. Consider reducing headroom or using smaller instances during off-peak hours.",
                potential_savings=current_infra.total_monthly_cost * 0.2,
                implementation_effort="low",
                priority="medium",
                category="scaling"
            ))
        
        recommendations.sort(key=lambda x: x.potential_savings, reverse=True)
        return recommendations
    
    def analyze(
        self,
        requests_per_day: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        model: str,
        cache_hit_ratio: float = 0.0,
        avg_latency_ms: float = 500,
        concurrency_limit: int = 50,
        region: str = "us-east-1",
        instance_type: Optional[str] = None
    ) -> ScalingAnalysisResult:
        """Perform comprehensive scaling analysis."""
        llm_result = self.llm_calculator.calculate(
            requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            cache_hit_ratio=cache_hit_ratio
        )
        
        infra_result = self.infra_calculator.calculate(
            requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit,
            region=region,
            instance_type=instance_type
        )
        
        current_state = {
            "requests_per_day": requests_per_day,
            "monthly_llm_cost": llm_result.monthly_total_cost,
            "monthly_infra_cost": infra_result.total_monthly_cost,
            "monthly_total_cost": llm_result.monthly_total_cost + infra_result.total_monthly_cost,
            "cost_per_request": (llm_result.monthly_total_cost + infra_result.total_monthly_cost) / (requests_per_day * 30),
            "pods": infra_result.total_pods_with_headroom,
            "utilization": infra_result.utilization_percent
        }
        
        pod_breakpoints = self.find_pod_scaling_breakpoints(
            base_requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit
        )
        
        breakpoints = []
        for req, pods in pod_breakpoints:
            bp_llm = self.llm_calculator.calculate(
                requests_per_day=req,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=cache_hit_ratio
            )
            
            bp_infra = self.infra_calculator.calculate(
                requests_per_day=req,
                avg_latency_ms=avg_latency_ms,
                concurrency_limit=concurrency_limit,
                region=region,
                instance_type=instance_type
            )
            
            total_cost = bp_llm.monthly_total_cost + bp_infra.total_monthly_cost
            cost_per_req = total_cost / (req * 30) if req > 0 else 0
            is_significant = pods > infra_result.total_pods_with_headroom
            
            breakpoints.append(ScalingBreakpoint(
                requests_per_day=req,
                pods_required=pods,
                monthly_llm_cost=bp_llm.monthly_total_cost,
                monthly_infra_cost=bp_infra.total_monthly_cost,
                monthly_total_cost=total_cost,
                cost_per_request=cost_per_req,
                description=f"At {req:,} req/day → {pods} pod(s) needed",
                is_significant=is_significant
            ))
        
        recommendations = self.generate_recommendations(
            requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            cache_hit_ratio=cache_hit_ratio,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit,
            region=region
        )
        
        growth_rates = [1.5, 2.0, 3.0, 5.0]
        cost_projection = {}
        
        for rate in growth_rates:
            proj_requests = int(requests_per_day * rate)
            proj_llm = self.llm_calculator.calculate(
                requests_per_day=proj_requests,
                avg_input_tokens=avg_input_tokens,
                avg_output_tokens=avg_output_tokens,
                model=model,
                cache_hit_ratio=cache_hit_ratio
            )
            proj_infra = self.infra_calculator.calculate(
                requests_per_day=proj_requests,
                avg_latency_ms=avg_latency_ms,
                concurrency_limit=concurrency_limit,
                region=region,
                instance_type=instance_type
            )
            
            cost_projection[f"{rate}x"] = {
                "requests_per_day": proj_requests,
                "monthly_cost": proj_llm.monthly_total_cost + proj_infra.total_monthly_cost,
                "pods_required": proj_infra.total_pods_with_headroom
            }
        
        scaling_alerts = []
        
        next_breakpoint = None
        for bp in breakpoints:
            if bp.requests_per_day > requests_per_day and bp.is_significant:
                next_breakpoint = bp
                break
        
        if next_breakpoint:
            growth_headroom = (next_breakpoint.requests_per_day - requests_per_day) / requests_per_day * 100
            scaling_alerts.append(
                f"At {next_breakpoint.requests_per_day:,} req/day → scale to {next_breakpoint.pods_required} pods"
            )
            if growth_headroom < 50:
                scaling_alerts.append(
                    f"⚠️ Only {growth_headroom:.0f}% growth before next scaling event"
                )
        
        doubling_points = self.find_cost_doubling_points(
            base_requests_per_day=requests_per_day,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            model=model,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit,
            cache_hit_ratio=cache_hit_ratio,
            region=region
        )
        
        if doubling_points:
            first_double = doubling_points[0]
            scaling_alerts.append(
                f"At {first_double['requests_per_day']:,} req/day ({first_double['multiplier']}x) → cost doubles to ${first_double['monthly_cost']:,.0f}/month"
            )
        
        total_potential_savings = sum(r.potential_savings for r in recommendations)
        optimization_potential = (total_potential_savings / current_state["monthly_total_cost"] * 100) if current_state["monthly_total_cost"] > 0 else 0
        
        return ScalingAnalysisResult(
            current_state=current_state,
            breakpoints=breakpoints,
            recommendations=recommendations,
            cost_projection=cost_projection,
            scaling_alerts=scaling_alerts,
            optimization_potential=optimization_potential
        )
