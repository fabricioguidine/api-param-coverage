"""
Analytics Dashboard

Provides dashboard functionality for visualizing analytics data and trends.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .aggregator import AnalyticsAggregator


class AnalyticsDashboard:
    """Dashboard for visualizing analytics data and trends."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the Analytics Dashboard.
        
        Args:
            output_dir: Root output directory containing run folders
        """
        self.aggregator = AnalyticsAggregator(output_dir=output_dir)
        self.output_dir = Path(output_dir)
    
    def generate_dashboard_report(self, limit: Optional[int] = None) -> Path:
        """
        Generate a comprehensive dashboard report.
        
        Args:
            limit: Maximum number of runs to include
            
        Returns:
            Path to the generated dashboard report
        """
        # Aggregate data
        aggregated = self.aggregator.aggregate_runs(limit=limit)
        
        # Generate summary report
        summary_path = self.aggregator.generate_summary_report(aggregated)
        
        # Generate trend analysis
        trend_path = self._generate_trend_analysis(aggregated)
        
        # Generate cost analysis
        cost_path = self._generate_cost_analysis(aggregated)
        
        # Generate main dashboard report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_path = self.output_dir / f"analytics_dashboard_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 80)
        lines.append("Analytics Dashboard")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Overview
        lines.append("OVERVIEW")
        lines.append("-" * 80)
        summary = aggregated['summary']
        lines.append(f"Total Runs: {aggregated['total_runs']}")
        lines.append(f"Total LLM Calls: {summary['total_llm_calls']}")
        lines.append(f"Total Cost: ${summary['total_cost_estimate']:.4f}")
        lines.append(f"Average Execution Time: {summary['average_execution_time']:.2f} seconds")
        lines.append("")
        
        # Key Metrics
        lines.append("KEY METRICS")
        lines.append("-" * 80)
        lines.append(f"Total Tokens: {summary['total_tokens_used']:,}")
        lines.append(f"Average Tokens per Call: {summary['average_tokens_per_call']:.0f}")
        lines.append(f"Total Execution Time: {summary['total_execution_time']:.2f} seconds")
        lines.append("")
        
        # Trend Summary
        if aggregated['trends']['dates']:
            lines.append("TREND SUMMARY")
            lines.append("-" * 80)
            lines.append(f"Runs Tracked: {len(aggregated['trends']['dates'])}")
            
            if len(aggregated['trends']['execution_times']) > 1:
                first_time = aggregated['trends']['execution_times'][-1]
                last_time = aggregated['trends']['execution_times'][0]
                time_change = ((last_time - first_time) / first_time * 100) if first_time > 0 else 0
                lines.append(f"Execution Time Trend: {time_change:+.1f}%")
            
            if len(aggregated['trends']['costs']) > 1:
                first_cost = aggregated['trends']['costs'][-1]
                last_cost = aggregated['trends']['costs'][0]
                cost_change = ((last_cost - first_cost) / first_cost * 100) if first_cost > 0 else 0
                lines.append(f"Cost Trend: {cost_change:+.1f}%")
            lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        recommendations = self._generate_recommendations(aggregated)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Report References
        lines.append("DETAILED REPORTS")
        lines.append("-" * 80)
        lines.append(f"Summary Report: {summary_path}")
        if trend_path:
            lines.append(f"Trend Analysis: {trend_path}")
        if cost_path:
            lines.append(f"Cost Analysis: {cost_path}")
        lines.append("")
        
        lines.append("=" * 80)
        
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text("\n".join(lines), encoding='utf-8')
        
        return dashboard_path
    
    def _generate_trend_analysis(self, aggregated: Dict[str, Any]) -> Optional[Path]:
        """Generate trend analysis report."""
        if not aggregated['trends']['dates']:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trend_path = self.output_dir / f"analytics_trends_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 80)
        lines.append("Analytics Trends Analysis")
        lines.append("=" * 80)
        lines.append("")
        
        trends = aggregated['trends']
        
        # Execution Time Trends
        lines.append("EXECUTION TIME TRENDS")
        lines.append("-" * 80)
        if trends['execution_times']:
            lines.append(f"First Run: {trends['execution_times'][-1]:.2f} seconds")
            lines.append(f"Latest Run: {trends['execution_times'][0]:.2f} seconds")
            if len(trends['execution_times']) > 1:
                avg_time = sum(trends['execution_times']) / len(trends['execution_times'])
                lines.append(f"Average: {avg_time:.2f} seconds")
        lines.append("")
        
        # Token Usage Trends
        lines.append("TOKEN USAGE TRENDS")
        lines.append("-" * 80)
        if trends['token_usage']:
            lines.append(f"First Run: {trends['token_usage'][-1]:,} tokens")
            lines.append(f"Latest Run: {trends['token_usage'][0]:,} tokens")
            if len(trends['token_usage']) > 1:
                avg_tokens = sum(trends['token_usage']) / len(trends['token_usage'])
                lines.append(f"Average: {avg_tokens:,.0f} tokens")
        lines.append("")
        
        # Cost Trends
        lines.append("COST TRENDS")
        lines.append("-" * 80)
        if trends['costs']:
            lines.append(f"First Run: ${trends['costs'][-1]:.4f}")
            lines.append(f"Latest Run: ${trends['costs'][0]:.4f}")
            if len(trends['costs']) > 1:
                total_cost = sum(trends['costs'])
                avg_cost = total_cost / len(trends['costs'])
                lines.append(f"Total: ${total_cost:.4f}")
                lines.append(f"Average: ${avg_cost:.4f}")
        lines.append("")
        
        lines.append("=" * 80)
        
        trend_path.write_text("\n".join(lines), encoding='utf-8')
        
        return trend_path
    
    def _generate_cost_analysis(self, aggregated: Dict[str, Any]) -> Optional[Path]:
        """Generate cost analysis report."""
        summary = aggregated['summary']
        
        if summary['total_cost_estimate'] == 0:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cost_path = self.output_dir / f"analytics_costs_{timestamp}.txt"
        
        lines = []
        lines.append("=" * 80)
        lines.append("Cost Analysis Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall Costs
        lines.append("OVERALL COSTS")
        lines.append("-" * 80)
        lines.append(f"Total Cost: ${summary['total_cost_estimate']:.4f}")
        lines.append(f"Total LLM Calls: {summary['total_llm_calls']}")
        lines.append(f"Average Cost per Call: ${summary['total_cost_estimate'] / summary['total_llm_calls']:.4f}" if summary['total_llm_calls'] > 0 else "N/A")
        lines.append("")
        
        # Cost Breakdown by Run
        if aggregated['runs']:
            lines.append("COST BREAKDOWN BY RUN")
            lines.append("-" * 80)
            for run in aggregated['runs'][:10]:  # Top 10 runs
                if run['cost_estimate'] > 0:
                    lines.append(f"{run['run_id']}: ${run['cost_estimate']:.4f} ({run['llm_calls']} calls)")
            lines.append("")
        
        # Cost Projections
        lines.append("COST PROJECTIONS")
        lines.append("-" * 80)
        if summary['total_llm_calls'] > 0:
            avg_cost_per_call = summary['total_cost_estimate'] / summary['total_llm_calls']
            lines.append(f"Average Cost per Call: ${avg_cost_per_call:.4f}")
            lines.append(f"Projected Cost for 100 Calls: ${avg_cost_per_call * 100:.2f}")
            lines.append(f"Projected Cost for 1000 Calls: ${avg_cost_per_call * 1000:.2f}")
        lines.append("")
        
        lines.append("=" * 80)
        
        cost_path.write_text("\n".join(lines), encoding='utf-8')
        
        return cost_path
    
    def _generate_recommendations(self, aggregated: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []
        summary = aggregated['summary']
        
        if summary['total_llm_calls'] == 0:
            recommendations.append("No LLM calls detected. Ensure analytics are being collected.")
            return recommendations
        
        # Check average execution time
        if summary['average_execution_time'] > 30:
            recommendations.append("High average execution time detected. Consider optimizing prompts or reducing chunk sizes.")
        
        # Check token usage
        if summary['average_tokens_per_call'] > 5000:
            recommendations.append("High token usage per call. Consider optimizing prompts to reduce token consumption.")
        
        # Check cost
        if summary['total_cost_estimate'] > 10.0:
            recommendations.append("Total cost is significant. Review token usage and consider optimizing prompts.")
        
        # Check trends
        if len(aggregated['trends']['execution_times']) > 1:
            times = aggregated['trends']['execution_times']
            if times[0] > times[-1] * 1.5:
                recommendations.append("Execution time is increasing. Review recent changes that might affect performance.")
        
        if not recommendations:
            recommendations.append("Analytics look healthy. Continue monitoring trends.")
        
        return recommendations


