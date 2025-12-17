"""
Markdown Report Generator Module

Generates formatted Markdown reports for cost analysis results.
"""

from datetime import datetime
from typing import Dict, Optional

from ai_infra_cost_estimator.calculator.llm import LLMCostResult
from ai_infra_cost_estimator.calculator.infra import InfraCostResult
from ai_infra_cost_estimator.calculator.scaling import ScalingAnalysisResult, Recommendation


class MarkdownReportGenerator:
    """
    Generates Markdown formatted reports for cost analysis.
    
    Creates comprehensive, human-readable reports with cost breakdowns,
    scaling alerts, and recommendations.
    """
    
    def __init__(self):
        """Initialize the Markdown report generator."""
        self.report_lines = []
    
    def _add_line(self, line: str = ""):
        """Add a line to the report."""
        self.report_lines.append(line)
    
    def _add_section(self, title: str, level: int = 2):
        """Add a section header."""
        prefix = "#" * level
        self._add_line(f"\n{prefix} {title}\n")
    
    def _add_table(self, headers: list, rows: list):
        """Add a Markdown table."""
        # Header
        self._add_line("| " + " | ".join(headers) + " |")
        # Separator
        self._add_line("| " + " | ".join(["---"] * len(headers)) + " |")
        # Rows
        for row in rows:
            self._add_line("| " + " | ".join(str(cell) for cell in row) + " |")
        self._add_line("")
    
    def _format_currency(self, amount: float) -> str:
        """Format amount as currency."""
        if amount >= 1000:
            return f"${amount:,.0f}"
        elif amount >= 1:
            return f"${amount:.2f}"
        else:
            return f"${amount:.4f}"
    
    def _format_number(self, num: float) -> str:
        """Format large numbers with commas."""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.1f}"
    
    def generate_header(self, config: Dict) -> str:
        """Generate report header section."""
        self.report_lines = []
        
        self._add_line("# 📊 AI Infrastructure Cost Estimate Report")
        self._add_line(f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        self._add_line("")
        
        self._add_section("Configuration Summary", 2)
        
        config_items = [
            ("Model", config.get("model", "N/A")),
            ("Region", config.get("region", "N/A")),
            ("Requests/Day", f"{config.get('requests_per_day', 0):,}"),
            ("Avg Input Tokens", f"{config.get('avg_input_tokens', 0):,}"),
            ("Avg Output Tokens", f"{config.get('avg_output_tokens', 0):,}"),
            ("Cache Hit Ratio", f"{config.get('cache_hit_ratio', 0) * 100:.0f}%"),
            ("Concurrency Limit", config.get("concurrency_limit", "N/A")),
        ]
        
        for label, value in config_items:
            self._add_line(f"- **{label}:** {value}")
        
        return "\n".join(self.report_lines)
    
    def generate_cost_summary(
        self,
        llm_result: LLMCostResult,
        infra_result: InfraCostResult
    ) -> str:
        """Generate cost summary section."""
        self.report_lines = []
        
        total_monthly = llm_result.monthly_total_cost + infra_result.total_monthly_cost
        total_yearly = total_monthly * 12
        
        self._add_section("💰 Monthly Cost Summary", 2)
        
        self._add_line("```")
        self._add_line(f"LLM Cost:     {self._format_currency(llm_result.monthly_total_cost):>12}")
        self._add_line(f"Infra Cost:   {self._format_currency(infra_result.total_monthly_cost):>12}")
        self._add_line(f"{'─' * 26}")
        self._add_line(f"Total:        {self._format_currency(total_monthly):>12}")
        self._add_line("")
        self._add_line(f"Cost per Request: {self._format_currency(llm_result.cost_per_request + (infra_result.total_monthly_cost / (infra_result.requests_per_second * 86400 * 30)))}")
        self._add_line(f"Yearly Estimate:  {self._format_currency(total_yearly)}")
        self._add_line("```")
        
        return "\n".join(self.report_lines)
    
    def generate_llm_breakdown(self, llm_result: LLMCostResult) -> str:
        """Generate LLM cost breakdown section."""
        self.report_lines = []
        
        self._add_section("🤖 LLM Cost Breakdown", 2)
        
        self._add_line(f"**Model:** {llm_result.model} ({llm_result.provider})")
        self._add_line("")
        
        self._add_table(
            ["Metric", "Daily", "Monthly"],
            [
                ["Input Tokens", self._format_number(llm_result.daily_input_tokens), self._format_number(llm_result.monthly_input_tokens)],
                ["Output Tokens", self._format_number(llm_result.daily_output_tokens), self._format_number(llm_result.monthly_output_tokens)],
                ["Total Tokens", self._format_number(llm_result.daily_total_tokens), self._format_number(llm_result.monthly_total_tokens)],
                ["Input Cost", self._format_currency(llm_result.daily_input_cost), self._format_currency(llm_result.monthly_input_cost)],
                ["Output Cost", self._format_currency(llm_result.daily_output_cost), self._format_currency(llm_result.monthly_output_cost)],
                ["**Total Cost**", f"**{self._format_currency(llm_result.daily_total_cost)}**", f"**{self._format_currency(llm_result.monthly_total_cost)}**"],
            ]
        )
        
        if llm_result.cost_saved_by_cache > 0:
            self._add_line(f"💾 **Cache Savings:** {self._format_currency(llm_result.cost_saved_by_cache)}/month")
            self._add_line(f"   Tokens saved: {self._format_number(llm_result.tokens_saved_by_cache)}")
        
        return "\n".join(self.report_lines)
    
    def generate_infra_breakdown(self, infra_result: InfraCostResult) -> str:
        """Generate infrastructure cost breakdown section."""
        self.report_lines = []
        
        self._add_section("🖥️ Infrastructure Breakdown", 2)
        
        self._add_line(f"**Instance Type:** {infra_result.instance_type}")
        self._add_line(f"**Region:** {infra_result.region} (multiplier: {infra_result.region_multiplier}x)")
        self._add_line("")
        
        self._add_table(
            ["Metric", "Value"],
            [
                ["Requests/Second", f"{infra_result.requests_per_second:.2f}"],
                ["Required Concurrency", f"{infra_result.required_concurrency:.1f}"],
                ["Base Pods Required", str(infra_result.required_pods)],
                ["Headroom Pods", str(infra_result.headroom_pods)],
                ["**Total Pods**", f"**{infra_result.total_pods_with_headroom}**"],
                ["Utilization", f"{infra_result.utilization_percent:.1f}%"],
                ["Cost/Pod/Hour", self._format_currency(infra_result.cost_per_pod_hour)],
                ["Cost/Pod/Month", self._format_currency(infra_result.cost_per_pod_month)],
                ["**Total Monthly**", f"**{self._format_currency(infra_result.total_monthly_cost)}**"],
            ]
        )
        
        return "\n".join(self.report_lines)
    
    def generate_scaling_alerts(self, analysis: ScalingAnalysisResult) -> str:
        """Generate scaling alerts section."""
        self.report_lines = []
        
        self._add_section("⚠️ Scaling Alerts", 2)
        
        if analysis.scaling_alerts:
            for alert in analysis.scaling_alerts:
                self._add_line(f"- {alert}")
        else:
            self._add_line("No immediate scaling concerns identified.")
        
        return "\n".join(self.report_lines)
    
    def generate_breakpoints(self, analysis: ScalingAnalysisResult) -> str:
        """Generate scaling breakpoints section."""
        self.report_lines = []
        
        self._add_section("📈 Scaling Breakpoints", 2)
        
        significant_breakpoints = [bp for bp in analysis.breakpoints if bp.is_significant][:5]
        
        if significant_breakpoints:
            self._add_table(
                ["Requests/Day", "Pods", "LLM Cost", "Infra Cost", "Total"],
                [
                    [
                        f"{bp.requests_per_day:,}",
                        str(bp.pods_required),
                        self._format_currency(bp.monthly_llm_cost),
                        self._format_currency(bp.monthly_infra_cost),
                        self._format_currency(bp.monthly_total_cost)
                    ]
                    for bp in significant_breakpoints
                ]
            )
        else:
            self._add_line("No significant breakpoints within analyzed range.")
        
        return "\n".join(self.report_lines)
    
    def generate_recommendations(self, recommendations: list) -> str:
        """Generate recommendations section."""
        self.report_lines = []
        
        self._add_section("💡 Recommendations", 2)
        
        if not recommendations:
            self._add_line("No specific recommendations at this time.")
            return "\n".join(self.report_lines)
        
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        for i, rec in enumerate(recommendations[:5], 1):
            icon = priority_icons.get(rec.priority, "⚪")
            self._add_line(f"### {i}. {icon} {rec.title}")
            self._add_line("")
            self._add_line(f"{rec.description}")
            self._add_line("")
            self._add_line(f"- **Potential Savings:** {self._format_currency(rec.potential_savings)}/month")
            self._add_line(f"- **Effort:** {rec.implementation_effort.title()}")
            self._add_line(f"- **Category:** {rec.category.title()}")
            self._add_line("")
        
        return "\n".join(self.report_lines)
    
    def generate_cost_projections(self, analysis: ScalingAnalysisResult) -> str:
        """Generate cost projections section."""
        self.report_lines = []
        
        self._add_section("📊 Cost Projections", 2)
        
        if analysis.cost_projection:
            rows = []
            for growth, data in analysis.cost_projection.items():
                rows.append([
                    growth,
                    f"{data['requests_per_day']:,}",
                    str(data['pods_required']),
                    self._format_currency(data['monthly_cost'])
                ])
            
            self._add_table(
                ["Growth", "Requests/Day", "Pods", "Monthly Cost"],
                rows
            )
        
        return "\n".join(self.report_lines)
    
    def generate_full_report(
        self,
        config: Dict,
        llm_result: LLMCostResult,
        infra_result: InfraCostResult,
        analysis: ScalingAnalysisResult
    ) -> str:
        """Generate a complete report."""
        sections = [
            self.generate_header(config),
            self.generate_cost_summary(llm_result, infra_result),
            self.generate_llm_breakdown(llm_result),
            self.generate_infra_breakdown(infra_result),
            self.generate_scaling_alerts(analysis),
            self.generate_breakpoints(analysis),
            self.generate_recommendations(analysis.recommendations),
            self.generate_cost_projections(analysis),
        ]
        
        # Add footer
        footer_lines = [
            "\n---",
            "",
            "*Report generated by AI Infra Cost Estimator*",
            f"*Optimization potential: {analysis.optimization_potential:.1f}%*",
            "",
            "> **Disclaimer:** These are estimates based on current pricing and usage patterns.",
            "> Actual costs may vary. Review provider documentation for exact pricing.",
        ]
        
        sections.append("\n".join(footer_lines))
        
        return "\n".join(sections)
    
    def save_report(self, report: str, filepath: str):
        """Save report to a file."""
        with open(filepath, 'w') as f:
            f.write(report)
