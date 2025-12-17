"""
JSON Report Generator Module

Generates structured JSON reports for cost analysis results.
Suitable for automation, API responses, and data processing.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any

from ai_infra_cost_estimator.calculator.llm import LLMCostResult
from ai_infra_cost_estimator.calculator.infra import InfraCostResult
from ai_infra_cost_estimator.calculator.scaling import ScalingAnalysisResult, Recommendation, ScalingBreakpoint


class JSONReportGenerator:
    """
    Generates JSON formatted reports for cost analysis.
    
    Creates structured, machine-readable reports suitable for
    API responses, automation, and data processing pipelines.
    """
    
    def __init__(self, indent: int = 2):
        """
        Initialize the JSON report generator.
        
        Args:
            indent: JSON indentation level for pretty printing
        """
        self.indent = indent
    
    def _serialize_llm_result(self, result: LLMCostResult) -> Dict:
        """Serialize LLMCostResult to dictionary."""
        return {
            "model": result.model,
            "provider": result.provider,
            "tokens": {
                "daily": {
                    "input": result.daily_input_tokens,
                    "output": result.daily_output_tokens,
                    "total": result.daily_total_tokens
                },
                "monthly": {
                    "input": result.monthly_input_tokens,
                    "output": result.monthly_output_tokens,
                    "total": result.monthly_total_tokens
                }
            },
            "costs": {
                "daily": {
                    "input": round(result.daily_input_cost, 4),
                    "output": round(result.daily_output_cost, 4),
                    "total": round(result.daily_total_cost, 4)
                },
                "monthly": {
                    "input": round(result.monthly_input_cost, 2),
                    "output": round(result.monthly_output_cost, 2),
                    "total": round(result.monthly_total_cost, 2)
                },
                "per_request": round(result.cost_per_request, 6)
            },
            "cache_savings": {
                "tokens_saved": result.tokens_saved_by_cache,
                "cost_saved": round(result.cost_saved_by_cache, 2)
            }
        }
    
    def _serialize_infra_result(self, result: InfraCostResult) -> Dict:
        """Serialize InfraCostResult to dictionary."""
        return {
            "instance_type": result.instance_type,
            "region": result.region,
            "region_multiplier": result.region_multiplier,
            "capacity": {
                "requests_per_second": round(result.requests_per_second, 4),
                "required_concurrency": round(result.required_concurrency, 2),
                "utilization_percent": round(result.utilization_percent, 2)
            },
            "pods": {
                "required": result.required_pods,
                "headroom": result.headroom_pods,
                "total": result.total_pods_with_headroom
            },
            "costs": {
                "per_pod_hour": round(result.cost_per_pod_hour, 4),
                "per_pod_month": round(result.cost_per_pod_month, 2),
                "total_monthly": round(result.total_monthly_cost, 2),
                "total_yearly": round(result.total_yearly_cost, 2)
            },
            "breakdown": result.breakdown
        }
    
    def _serialize_recommendation(self, rec: Recommendation) -> Dict:
        """Serialize Recommendation to dictionary."""
        return {
            "title": rec.title,
            "description": rec.description,
            "potential_savings": round(rec.potential_savings, 2),
            "implementation_effort": rec.implementation_effort,
            "priority": rec.priority,
            "category": rec.category
        }
    
    def _serialize_breakpoint(self, bp: ScalingBreakpoint) -> Dict:
        """Serialize ScalingBreakpoint to dictionary."""
        return {
            "requests_per_day": bp.requests_per_day,
            "pods_required": bp.pods_required,
            "costs": {
                "llm": round(bp.monthly_llm_cost, 2),
                "infra": round(bp.monthly_infra_cost, 2),
                "total": round(bp.monthly_total_cost, 2),
                "per_request": round(bp.cost_per_request, 6)
            },
            "description": bp.description,
            "is_significant": bp.is_significant
        }
    
    def _serialize_analysis(self, analysis: ScalingAnalysisResult) -> Dict:
        """Serialize ScalingAnalysisResult to dictionary."""
        return {
            "current_state": {
                "requests_per_day": analysis.current_state["requests_per_day"],
                "costs": {
                    "llm": round(analysis.current_state["monthly_llm_cost"], 2),
                    "infra": round(analysis.current_state["monthly_infra_cost"], 2),
                    "total": round(analysis.current_state["monthly_total_cost"], 2),
                    "per_request": round(analysis.current_state["cost_per_request"], 6)
                },
                "pods": analysis.current_state["pods"],
                "utilization": round(analysis.current_state["utilization"], 2)
            },
            "breakpoints": [
                self._serialize_breakpoint(bp) 
                for bp in analysis.breakpoints 
                if bp.is_significant
            ][:10],  # Limit to 10 significant breakpoints
            "recommendations": [
                self._serialize_recommendation(rec) 
                for rec in analysis.recommendations
            ],
            "cost_projections": analysis.cost_projection,
            "scaling_alerts": analysis.scaling_alerts,
            "optimization_potential_percent": round(analysis.optimization_potential, 2)
        }
    
    def generate_report(
        self,
        config: Dict,
        llm_result: LLMCostResult,
        infra_result: InfraCostResult,
        analysis: ScalingAnalysisResult
    ) -> Dict:
        """
        Generate a complete JSON report structure.
        
        Args:
            config: Configuration parameters
            llm_result: LLM cost calculation results
            infra_result: Infrastructure cost calculation results
            analysis: Scaling analysis results
            
        Returns:
            Dictionary containing the complete report
        """
        total_monthly = llm_result.monthly_total_cost + infra_result.total_monthly_cost
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "currency": "USD"
            },
            "configuration": {
                "model": config.get("model"),
                "region": config.get("region"),
                "requests_per_day": config.get("requests_per_day"),
                "avg_input_tokens": config.get("avg_input_tokens"),
                "avg_output_tokens": config.get("avg_output_tokens"),
                "cache_hit_ratio": config.get("cache_hit_ratio"),
                "concurrency_limit": config.get("concurrency_limit"),
                "avg_latency_ms": config.get("avg_latency_ms")
            },
            "summary": {
                "monthly_total": round(total_monthly, 2),
                "yearly_total": round(total_monthly * 12, 2),
                "llm_cost": round(llm_result.monthly_total_cost, 2),
                "infra_cost": round(infra_result.total_monthly_cost, 2),
                "cost_per_request": round(
                    (llm_result.cost_per_request + 
                     infra_result.total_monthly_cost / (config.get("requests_per_day", 1) * 30)),
                    6
                ),
                "total_pods": infra_result.total_pods_with_headroom,
                "optimization_potential_percent": round(analysis.optimization_potential, 2)
            },
            "llm": self._serialize_llm_result(llm_result),
            "infrastructure": self._serialize_infra_result(infra_result),
            "analysis": self._serialize_analysis(analysis)
        }
        
        return report
    
    def to_json_string(self, report: Dict) -> str:
        """
        Convert report dictionary to JSON string.
        
        Args:
            report: Report dictionary
            
        Returns:
            Formatted JSON string
        """
        return json.dumps(report, indent=self.indent)
    
    def save_report(self, report: Dict, filepath: str):
        """
        Save report to a JSON file.
        
        Args:
            report: Report dictionary
            filepath: Path to save the file
        """
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=self.indent)
    
    def generate_compact_summary(
        self,
        llm_result: LLMCostResult,
        infra_result: InfraCostResult
    ) -> Dict:
        """
        Generate a compact summary for quick access.
        
        Args:
            llm_result: LLM cost calculation results
            infra_result: Infrastructure cost calculation results
            
        Returns:
            Compact summary dictionary
        """
        total_monthly = llm_result.monthly_total_cost + infra_result.total_monthly_cost
        
        return {
            "costs": {
                "llm_monthly": round(llm_result.monthly_total_cost, 2),
                "infra_monthly": round(infra_result.total_monthly_cost, 2),
                "total_monthly": round(total_monthly, 2),
                "total_yearly": round(total_monthly * 12, 2)
            },
            "infrastructure": {
                "pods": infra_result.total_pods_with_headroom,
                "instance_type": infra_result.instance_type,
                "region": infra_result.region
            },
            "efficiency": {
                "cost_per_request": round(llm_result.cost_per_request, 6),
                "utilization_percent": round(infra_result.utilization_percent, 2),
                "cache_savings": round(llm_result.cost_saved_by_cache, 2)
            }
        }
    
    def generate_api_response(
        self,
        config: Dict,
        llm_result: LLMCostResult,
        infra_result: InfraCostResult,
        analysis: ScalingAnalysisResult,
        success: bool = True,
        error: Optional[str] = None
    ) -> Dict:
        """
        Generate an API-friendly response structure.
        
        Args:
            config: Configuration parameters
            llm_result: LLM cost calculation results
            infra_result: Infrastructure cost calculation results
            analysis: Scaling analysis results
            success: Whether the calculation was successful
            error: Error message if any
            
        Returns:
            API response dictionary
        """
        if not success:
            return {
                "success": False,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": self.generate_report(config, llm_result, infra_result, analysis)
        }
