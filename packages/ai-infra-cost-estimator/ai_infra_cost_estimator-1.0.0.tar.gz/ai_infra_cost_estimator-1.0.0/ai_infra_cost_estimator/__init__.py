"""
AI Infra Cost Estimator

A tool for estimating real-world AI + cloud infrastructure costs.
"""

__version__ = "1.0.0"
__author__ = "MindTheInfraAI"

from ai_infra_cost_estimator.calculator.llm import LLMCostCalculator, LLMCostResult
from ai_infra_cost_estimator.calculator.infra import InfraCostCalculator, InfraCostResult
from ai_infra_cost_estimator.calculator.scaling import ScalingAnalyzer, ScalingAnalysisResult, Recommendation
from ai_infra_cost_estimator.report.markdown import MarkdownReportGenerator
from ai_infra_cost_estimator.report.json_report import JSONReportGenerator

__all__ = [
    'LLMCostCalculator',
    'LLMCostResult',
    'InfraCostCalculator',
    'InfraCostResult',
    'ScalingAnalyzer',
    'ScalingAnalysisResult',
    'Recommendation',
    'MarkdownReportGenerator',
    'JSONReportGenerator',
    '__version__',
]
