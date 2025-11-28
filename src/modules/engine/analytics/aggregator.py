"""
Analytics Aggregator

Aggregates analytics data across multiple runs to generate summary reports and track trends.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict


class AnalyticsAggregator:
    """Aggregates analytics data across multiple execution runs."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the Analytics Aggregator.
        
        Args:
            output_dir: Root output directory containing run folders
        """
        self.output_dir = Path(output_dir)
    
    def aggregate_runs(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Aggregate analytics from all execution runs.
        
        Args:
            limit: Maximum number of runs to process (None for all)
            
        Returns:
            Aggregated analytics dictionary
        """
        run_folders = self._find_run_folders()
        
        if limit:
            run_folders = run_folders[:limit]
        
        aggregated = {
            'total_runs': len(run_folders),
            'runs': [],
            'summary': {
                'total_llm_calls': 0,
                'total_algorithm_executions': 0,
                'total_execution_time': 0.0,
                'total_tokens_used': 0,
                'total_cost_estimate': 0.0,
                'average_execution_time': 0.0,
                'average_tokens_per_call': 0.0
            },
            'trends': {
                'execution_times': [],
                'token_usage': [],
                'costs': [],
                'dates': []
            }
        }
        
        for run_folder in run_folders:
            run_data = self._process_run_folder(run_folder)
            if run_data:
                aggregated['runs'].append(run_data)
                
                # Update summary
                aggregated['summary']['total_llm_calls'] += run_data.get('llm_calls', 0)
                aggregated['summary']['total_algorithm_executions'] += run_data.get('algorithm_executions', 0)
                aggregated['summary']['total_execution_time'] += run_data.get('total_execution_time', 0.0)
                aggregated['summary']['total_tokens_used'] += run_data.get('total_tokens', 0)
                aggregated['summary']['total_cost_estimate'] += run_data.get('cost_estimate', 0.0)
                
                # Update trends
                if run_data.get('timestamp'):
                    aggregated['trends']['dates'].append(run_data['timestamp'])
                    aggregated['trends']['execution_times'].append(run_data.get('total_execution_time', 0.0))
                    aggregated['trends']['token_usage'].append(run_data.get('total_tokens', 0))
                    aggregated['trends']['costs'].append(run_data.get('cost_estimate', 0.0))
        
        # Calculate averages
        if aggregated['summary']['total_llm_calls'] > 0:
            aggregated['summary']['average_execution_time'] = (
                aggregated['summary']['total_execution_time'] / aggregated['summary']['total_llm_calls']
            )
            aggregated['summary']['average_tokens_per_call'] = (
                aggregated['summary']['total_tokens_used'] / aggregated['summary']['total_llm_calls']
            )
        
        return aggregated
    
    def _find_run_folders(self) -> List[Path]:
        """Find all run folders in the output directory."""
        run_folders = []
        
        if not self.output_dir.exists():
            return run_folders
        
        # Look for folders matching timestamp pattern: YYYYMMDD_HHMMSS_*
        pattern = re.compile(r'^\d{8}_\d{6}_')
        
        for item in self.output_dir.iterdir():
            if item.is_dir() and pattern.match(item.name):
                run_folders.append(item)
        
        # Sort by name (which includes timestamp) - newest first
        run_folders.sort(key=lambda x: x.name, reverse=True)
        
        return run_folders
    
    def _process_run_folder(self, run_folder: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single run folder and extract analytics.
        
        Args:
            run_folder: Path to the run folder
            
        Returns:
            Run data dictionary or None
        """
        analytics_dir = run_folder / "analytics"
        
        if not analytics_dir.exists():
            return None
        
        run_data = {
            'run_id': run_folder.name,
            'timestamp': self._extract_timestamp(run_folder.name),
            'llm_calls': 0,
            'algorithm_executions': 0,
            'total_execution_time': 0.0,
            'total_tokens': 0,
            'cost_estimate': 0.0,
            'metrics_files': [],
            'algorithm_reports': []
        }
        
        # Process LLM execution metrics
        for metrics_file in analytics_dir.glob("llm_execution_metrics_*.txt"):
            metrics_data = self._parse_metrics_file(metrics_file)
            if metrics_data:
                run_data['llm_calls'] += 1
                run_data['total_execution_time'] += metrics_data.get('execution_time', 0.0)
                run_data['total_tokens'] += metrics_data.get('total_tokens', 0)
                run_data['cost_estimate'] += metrics_data.get('cost_estimate', 0.0)
                run_data['metrics_files'].append(str(metrics_file))
        
        # Process algorithm reports
        for report_file in analytics_dir.glob("algorithm_report_*.txt"):
            algorithm_data = self._parse_algorithm_report(report_file)
            if algorithm_data:
                run_data['algorithm_executions'] += 1
                run_data['algorithm_reports'].append({
                    'file': str(report_file),
                    'algorithm': algorithm_data.get('algorithm_name', 'unknown'),
                    'execution_time': algorithm_data.get('execution_time', 0.0)
                })
        
        return run_data
    
    def _extract_timestamp(self, run_id: str) -> Optional[str]:
        """Extract timestamp from run ID."""
        # Format: YYYYMMDD_HHMMSS_schema_name
        match = re.match(r'^(\d{8}_\d{6})_', run_id)
        if match:
            timestamp_str = match.group(1)
            try:
                dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                return dt.isoformat()
            except ValueError:
                return None
        return None
    
    def _parse_metrics_file(self, metrics_file: Path) -> Optional[Dict[str, Any]]:
        """Parse LLM execution metrics file."""
        try:
            content = metrics_file.read_text(encoding='utf-8')
            
            metrics = {
                'execution_time': 0.0,
                'total_tokens': 0,
                'cost_estimate': 0.0
            }
            
            # Extract execution time
            time_match = re.search(r'Execution Time:\s*([\d.]+)\s*seconds', content)
            if time_match:
                metrics['execution_time'] = float(time_match.group(1))
            
            # Extract token usage
            tokens_match = re.search(r'Total Tokens:\s*(\d+)', content)
            if tokens_match:
                metrics['total_tokens'] = int(tokens_match.group(1))
            
            # Extract cost estimate (if available)
            cost_match = re.search(r'Cost Estimate:\s*\$?([\d.]+)', content)
            if cost_match:
                metrics['cost_estimate'] = float(cost_match.group(1))
            else:
                # Estimate cost based on tokens (GPT-4 pricing: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens)
                if metrics['total_tokens'] > 0:
                    # Rough estimate: assume 50/50 input/output split
                    input_tokens = metrics['total_tokens'] * 0.5
                    output_tokens = metrics['total_tokens'] * 0.5
                    cost = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
                    metrics['cost_estimate'] = round(cost, 4)
            
            return metrics
        except Exception as e:
            print(f"Warning: Failed to parse metrics file {metrics_file}: {e}")
            return None
    
    def _parse_algorithm_report(self, report_file: Path) -> Optional[Dict[str, Any]]:
        """Parse algorithm report file."""
        try:
            content = report_file.read_text(encoding='utf-8')
            
            report = {
                'algorithm_name': 'unknown',
                'execution_time': 0.0
            }
            
            # Extract algorithm name
            name_match = re.search(r'Algorithm:\s*(\w+)', content)
            if name_match:
                report['algorithm_name'] = name_match.group(1)
            
            # Extract execution time
            time_match = re.search(r'Execution Time:\s*([\d.]+)\s*seconds', content)
            if time_match:
                report['execution_time'] = float(time_match.group(1))
            
            return report
        except Exception as e:
            print(f"Warning: Failed to parse algorithm report {report_file}: {e}")
            return None
    
    def generate_summary_report(self, aggregated: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """
        Generate a human-readable summary report.
        
        Args:
            aggregated: Aggregated analytics data
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated report file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"output/analytics_summary_{timestamp}.txt")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        lines.append("=" * 80)
        lines.append("Analytics Summary Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary Statistics
        summary = aggregated['summary']
        lines.append("SUMMARY STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total Runs Analyzed: {aggregated['total_runs']}")
        lines.append(f"Total LLM Calls: {summary['total_llm_calls']}")
        lines.append(f"Total Algorithm Executions: {summary['total_algorithm_executions']}")
        lines.append(f"Total Execution Time: {summary['total_execution_time']:.2f} seconds")
        lines.append(f"Total Tokens Used: {summary['total_tokens_used']:,}")
        lines.append(f"Total Cost Estimate: ${summary['total_cost_estimate']:.4f}")
        lines.append(f"Average Execution Time: {summary['average_execution_time']:.2f} seconds")
        lines.append(f"Average Tokens per Call: {summary['average_tokens_per_call']:.0f}")
        lines.append("")
        
        # Per-Run Breakdown
        if aggregated['runs']:
            lines.append("PER-RUN BREAKDOWN")
            lines.append("-" * 80)
            for run in aggregated['runs'][:10]:  # Top 10 runs
                lines.append(f"\nRun: {run['run_id']}")
                lines.append(f"  Timestamp: {run.get('timestamp', 'Unknown')}")
                lines.append(f"  LLM Calls: {run['llm_calls']}")
                lines.append(f"  Algorithm Executions: {run['algorithm_executions']}")
                lines.append(f"  Execution Time: {run['total_execution_time']:.2f} seconds")
                lines.append(f"  Tokens Used: {run['total_tokens']:,}")
                lines.append(f"  Cost Estimate: ${run['cost_estimate']:.4f}")
        
        lines.append("")
        lines.append("=" * 80)
        
        # Write report
        output_path.write_text("\n".join(lines), encoding='utf-8')
        
        return output_path




