"""
Metrics Collector

Collects and saves complexity analysis metrics for each LLM API call.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json


class MetricsCollector:
    """Collects and saves complexity analysis metrics for LLM API executions."""
    
    def __init__(self, analytics_dir: str = "output/analytics"):
        """
        Initialize the Metrics Collector.
        
        Args:
            analytics_dir: Directory where analytics files will be saved
                          Default: "output/analytics" (follows project structure)
        """
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        # Save reports directly in the same directory (flat structure)
        self.reports_dir = self.analytics_dir
    
    def collect_metrics(
        self,
        processed_data: Optional[Dict[str, Any]] = None,
        analysis_data: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        api_response: Optional[Any] = None,
        execution_time: Optional[float] = None,
        model: Optional[str] = None,
        task: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect complexity analysis metrics from the execution.
        
        Args:
            processed_data: Processed schema data
            analysis_data: Schema analysis data with complexity information
            prompt: The prompt sent to the LLM
            api_response: The API response object (if available)
            execution_time: Time taken for execution in seconds
            model: LLM model used
            task: Task type (e.g., 'gherkin', 'analyze')
            
        Returns:
            Dictionary containing all collected metrics
        """
        timestamp = datetime.now()
        metrics = {
            "timestamp": timestamp.isoformat(),
            "model": model or "unknown",
            "task": task or "unknown",
            "execution_time_seconds": execution_time,
        }
        
        # Extract complexity metrics from processed_data
        if processed_data:
            metrics["api_info"] = {
                "title": processed_data.get('info', {}).get('title', 'Unknown'),
                "version": processed_data.get('info', {}).get('version', 'Unknown'),
                "openapi_version": processed_data.get('version', 'Unknown'),
            }
            metrics["schema_stats"] = {
                "total_endpoints": processed_data.get('paths_count', 0),
                "components_count": sum(processed_data.get('components', {}).values()) if isinstance(processed_data.get('components'), dict) else 0,
            }
        
        # Extract complexity metrics from analysis_data
        if analysis_data:
            endpoints = analysis_data.get('endpoints', [])
            total_params = 0
            total_iteration_count = 0
            param_types = {}
            param_locations = {}
            constraint_types = {}
            bounded_params = 0
            unbounded_params = 0
            enum_params = 0
            pattern_params = 0
            
            for endpoint in endpoints:
                params = endpoint.get('parameters', [])
                total_params += len(params)
                
                for param in params:
                    # Count parameter types
                    param_type = param.get('type', 'unknown')
                    param_types[param_type] = param_types.get(param_type, 0) + 1
                    
                    # Count parameter locations
                    location = param.get('location', 'unknown')
                    param_locations[location] = param_locations.get(location, 0) + 1
                    
                    # Analyze constraints
                    constraints = param.get('constraints', {})
                    if constraints:
                        if 'enum' in constraints:
                            enum_params += 1
                        if 'pattern' in constraints:
                            pattern_params += 1
                    
                    # Analyze iteration count
                    iteration_count = param.get('iterationCount')
                    if iteration_count:
                        if isinstance(iteration_count, (int, float)):
                            total_iteration_count += iteration_count
                        elif iteration_count == "bounded":
                            bounded_params += 1
                        elif iteration_count == "unbounded":
                            unbounded_params += 1
            
            metrics["complexity_analysis"] = {
                "total_endpoints_analyzed": len(endpoints),
                "total_parameters": total_params,
                "average_parameters_per_endpoint": round(total_params / len(endpoints), 2) if endpoints else 0,
                "total_iteration_count": total_iteration_count,
                "parameter_types_distribution": param_types,
                "parameter_locations_distribution": param_locations,
                "constraint_analysis": {
                    "enum_parameters": enum_params,
                    "pattern_parameters": pattern_params,
                    "bounded_parameters": bounded_params,
                    "unbounded_parameters": unbounded_params,
                },
            }
        
        # Extract prompt metrics
        if prompt:
            prompt_length = len(prompt)
            estimated_tokens = prompt_length // 4  # Rough estimate: 1 token = 4 chars
            metrics["prompt_metrics"] = {
                "prompt_length_chars": prompt_length,
                "estimated_tokens": estimated_tokens,
            }
        
        # Extract API response metrics (if available)
        if api_response:
            try:
                # Try to extract token usage from OpenAI response
                if hasattr(api_response, 'usage'):
                    usage = api_response.usage
                    metrics["api_usage"] = {
                        "prompt_tokens": getattr(usage, 'prompt_tokens', None),
                        "completion_tokens": getattr(usage, 'completion_tokens', None),
                        "total_tokens": getattr(usage, 'total_tokens', None),
                    }
                
                # Extract response content length
                if hasattr(api_response, 'choices') and api_response.choices:
                    content = api_response.choices[0].message.content if hasattr(api_response.choices[0].message, 'content') else None
                    if content:
                        metrics["response_metrics"] = {
                            "response_length_chars": len(content),
                            "estimated_response_tokens": len(content) // 4,
                        }
            except Exception as e:
                metrics["api_response_error"] = str(e)
        
        return metrics
    
    def collect_algorithm_metrics(
        self,
        algorithm_name: str,
        algorithm_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None,
        complexity_metrics: Optional[Dict[str, Any]] = None,
        llm_call: bool = False,
        llm_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect detailed metrics for algorithm execution and analysis.
        
        Args:
            algorithm_name: Name of the algorithm (e.g., 'SchemaAnalyzer', 'BRDGenerator')
            algorithm_type: Type of algorithm (e.g., 'analyzer', 'generator', 'processor', 'cross_reference')
            input_data: Input data metrics
            output_data: Output data metrics
            execution_time: Time taken for execution
            complexity_metrics: Algorithm-specific complexity metrics
            llm_call: Whether this algorithm made an LLM call
            llm_metrics: LLM-specific metrics if applicable
            
        Returns:
            Dictionary containing algorithm metrics
        """
        timestamp = datetime.now()
        
        metrics = {
            "timestamp": timestamp.isoformat(),
            "algorithm_name": algorithm_name,
            "algorithm_type": algorithm_type,
            "execution_time_seconds": execution_time,
            "llm_call": llm_call,
        }
        
        # Input complexity analysis
        if input_data:
            metrics["input_analysis"] = self._analyze_input_complexity(input_data)
        
        # Output complexity analysis
        if output_data:
            metrics["output_analysis"] = self._analyze_output_complexity(output_data)
        
        # Algorithm-specific complexity metrics
        if complexity_metrics:
            metrics["algorithm_complexity"] = complexity_metrics
        
        # LLM metrics if applicable
        if llm_call and llm_metrics:
            metrics["llm_analysis"] = llm_metrics
        
        return metrics
    
    def _analyze_input_complexity(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complexity of input data."""
        analysis = {
            "data_size": 0,
            "structure_complexity": "low",
            "nested_depth": 0,
            "element_count": 0
        }
        
        # Calculate data size (rough estimate)
        import sys
        analysis["data_size"] = sys.getsizeof(str(input_data))
        
        # Analyze structure
        if isinstance(input_data, dict):
            analysis["element_count"] = len(input_data)
            # Check for nested structures
            max_depth = self._calculate_max_depth(input_data)
            analysis["nested_depth"] = max_depth
            
            if max_depth > 5:
                analysis["structure_complexity"] = "very_high"
            elif max_depth > 3:
                analysis["structure_complexity"] = "high"
            elif max_depth > 1:
                analysis["structure_complexity"] = "medium"
        
        return analysis
    
    def _analyze_output_complexity(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complexity of output data."""
        analysis = {
            "data_size": 0,
            "structure_complexity": "low",
            "nested_depth": 0,
            "element_count": 0,
            "output_quality": "unknown"
        }
        
        import sys
        analysis["data_size"] = sys.getsizeof(str(output_data))
        
        if isinstance(output_data, dict):
            analysis["element_count"] = len(output_data)
            max_depth = self._calculate_max_depth(output_data)
            analysis["nested_depth"] = max_depth
            
            if max_depth > 5:
                analysis["structure_complexity"] = "very_high"
            elif max_depth > 3:
                analysis["structure_complexity"] = "high"
            elif max_depth > 1:
                analysis["structure_complexity"] = "medium"
            
            # Assess output quality based on completeness
            if 'endpoints' in output_data or 'requirements' in output_data:
                count = len(output_data.get('endpoints', output_data.get('requirements', [])))
                if count > 0:
                    analysis["output_quality"] = "complete"
                else:
                    analysis["output_quality"] = "empty"
        
        return analysis
    
    def _calculate_max_depth(self, obj: Any, depth: int = 0) -> int:
        """Calculate maximum nesting depth of a data structure."""
        if not isinstance(obj, (dict, list)):
            return depth
        
        if not obj:
            return depth
        
        if isinstance(obj, dict):
            return max([self._calculate_max_depth(v, depth + 1) for v in obj.values()], default=depth)
        else:  # list
            return max([self._calculate_max_depth(item, depth + 1) for item in obj], default=depth)
    
    def save_algorithm_report(self, algorithm_metrics: Dict[str, Any]) -> Path:
        """
        Save algorithm-specific report to a separate file.
        
        Args:
            algorithm_metrics: Dictionary containing algorithm metrics
            
        Returns:
            Path to the saved report file
        """
        timestamp = datetime.fromisoformat(algorithm_metrics['timestamp'])
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        algorithm_name = algorithm_metrics.get('algorithm_name', 'unknown').replace(' ', '_').lower()
        algorithm_type = algorithm_metrics.get('algorithm_type', 'unknown')
        
        filename = f"{timestamp_str}_{algorithm_type}_{algorithm_name}.txt"
        filepath = self.reports_dir / filename
        
        # Format report
        content = self._format_algorithm_report(algorithm_metrics)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _format_algorithm_report(self, metrics: Dict[str, Any]) -> str:
        """Format algorithm metrics as a detailed report."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"Algorithm Analysis Report: {metrics.get('algorithm_name', 'Unknown')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic info
        lines.append("ALGORITHM INFORMATION")
        lines.append("-" * 80)
        lines.append(f"Algorithm Name: {metrics.get('algorithm_name', 'N/A')}")
        lines.append(f"Algorithm Type: {metrics.get('algorithm_type', 'N/A')}")
        lines.append(f"Timestamp: {metrics.get('timestamp', 'N/A')}")
        if metrics.get('execution_time_seconds'):
            lines.append(f"Execution Time: {metrics['execution_time_seconds']:.2f} seconds")
        lines.append(f"LLM Call: {'Yes' if metrics.get('llm_call') else 'No'}")
        lines.append("")
        
        # Input analysis
        if 'input_analysis' in metrics:
            lines.append("INPUT COMPLEXITY ANALYSIS")
            lines.append("-" * 80)
            input_analysis = metrics['input_analysis']
            lines.append(f"Data Size (bytes): {input_analysis.get('data_size', 0):,}")
            lines.append(f"Element Count: {input_analysis.get('element_count', 0)}")
            lines.append(f"Nested Depth: {input_analysis.get('nested_depth', 0)}")
            lines.append(f"Structure Complexity: {input_analysis.get('structure_complexity', 'N/A')}")
            lines.append("")
        
        # Output analysis
        if 'output_analysis' in metrics:
            lines.append("OUTPUT COMPLEXITY ANALYSIS")
            lines.append("-" * 80)
            output_analysis = metrics['output_analysis']
            lines.append(f"Data Size (bytes): {output_analysis.get('data_size', 0):,}")
            lines.append(f"Element Count: {output_analysis.get('element_count', 0)}")
            lines.append(f"Nested Depth: {output_analysis.get('nested_depth', 0)}")
            lines.append(f"Structure Complexity: {output_analysis.get('structure_complexity', 'N/A')}")
            lines.append(f"Output Quality: {output_analysis.get('output_quality', 'N/A')}")
            lines.append("")
        
        # Algorithm-specific complexity
        if 'algorithm_complexity' in metrics:
            lines.append("ALGORITHM-SPECIFIC COMPLEXITY METRICS")
            lines.append("-" * 80)
            complexity = metrics['algorithm_complexity']
            for key, value in complexity.items():
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  - {sub_key}: {sub_value}")
                else:
                    lines.append(f"{key}: {value}")
            lines.append("")
        
        # LLM analysis if applicable
        if metrics.get('llm_call') and 'llm_analysis' in metrics:
            lines.append("LLM CALL ANALYSIS")
            lines.append("-" * 80)
            llm_analysis = metrics['llm_analysis']
            
            if 'prompt_metrics' in llm_analysis:
                prompt = llm_analysis['prompt_metrics']
                lines.append("Prompt Metrics:")
                lines.append(f"  - Length: {prompt.get('prompt_length_chars', 0):,} characters")
                lines.append(f"  - Estimated Tokens: {prompt.get('estimated_tokens', 0):,}")
            
            if 'api_usage' in llm_analysis:
                usage = llm_analysis['api_usage']
                lines.append("API Usage:")
                lines.append(f"  - Prompt Tokens: {usage.get('prompt_tokens', 'N/A')}")
                lines.append(f"  - Completion Tokens: {usage.get('completion_tokens', 'N/A')}")
                lines.append(f"  - Total Tokens: {usage.get('total_tokens', 'N/A')}")
            
            if 'response_metrics' in llm_analysis:
                response = llm_analysis['response_metrics']
                lines.append("Response Metrics:")
                lines.append(f"  - Length: {response.get('response_length_chars', 0):,} characters")
                lines.append(f"  - Estimated Tokens: {response.get('estimated_response_tokens', 0):,}")
            
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def save_metrics(self, metrics: Dict[str, Any]) -> Path:
        """
        Save metrics to a timestamped file in the analytics directory.
        
        Args:
            metrics: Dictionary containing metrics to save
            
        Returns:
            Path to the saved file
        """
        # Generate timestamp string for filename
        timestamp = datetime.fromisoformat(metrics['timestamp'])
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp_str}.txt"
        filepath = self.analytics_dir / filename
        
        # Format metrics as readable text
        content = self._format_metrics(metrics)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """
        Format metrics dictionary as readable text.
        
        Args:
            metrics: Dictionary containing metrics
            
        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("LLM API Execution - Complexity Analysis Metrics")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic execution info
        lines.append("EXECUTION INFORMATION")
        lines.append("-" * 80)
        lines.append(f"Timestamp: {metrics.get('timestamp', 'N/A')}")
        lines.append(f"Model: {metrics.get('model', 'N/A')}")
        lines.append(f"Task: {metrics.get('task', 'N/A')}")
        if metrics.get('execution_time_seconds'):
            lines.append(f"Execution Time: {metrics['execution_time_seconds']:.2f} seconds")
        lines.append("")
        
        # API info
        if 'api_info' in metrics:
            lines.append("API INFORMATION")
            lines.append("-" * 80)
            api_info = metrics['api_info']
            lines.append(f"Title: {api_info.get('title', 'N/A')}")
            lines.append(f"Version: {api_info.get('version', 'N/A')}")
            lines.append(f"OpenAPI Version: {api_info.get('openapi_version', 'N/A')}")
            lines.append("")
        
        # Schema stats
        if 'schema_stats' in metrics:
            lines.append("SCHEMA STATISTICS")
            lines.append("-" * 80)
            stats = metrics['schema_stats']
            lines.append(f"Total Endpoints: {stats.get('total_endpoints', 0)}")
            lines.append(f"Components Count: {stats.get('components_count', 0)}")
            lines.append("")
        
        # Complexity analysis
        if 'complexity_analysis' in metrics:
            lines.append("COMPLEXITY ANALYSIS")
            lines.append("-" * 80)
            complexity = metrics['complexity_analysis']
            lines.append(f"Total Endpoints Analyzed: {complexity.get('total_endpoints_analyzed', 0)}")
            lines.append(f"Total Parameters: {complexity.get('total_parameters', 0)}")
            lines.append(f"Average Parameters per Endpoint: {complexity.get('average_parameters_per_endpoint', 0)}")
            lines.append(f"Total Iteration Count: {complexity.get('total_iteration_count', 0)}")
            lines.append("")
            
            # Parameter types distribution
            if 'parameter_types_distribution' in complexity:
                lines.append("Parameter Types Distribution:")
                for param_type, count in sorted(complexity['parameter_types_distribution'].items()):
                    lines.append(f"  - {param_type}: {count}")
                lines.append("")
            
            # Parameter locations distribution
            if 'parameter_locations_distribution' in complexity:
                lines.append("Parameter Locations Distribution:")
                for location, count in sorted(complexity['parameter_locations_distribution'].items()):
                    lines.append(f"  - {location}: {count}")
                lines.append("")
            
            # Constraint analysis
            if 'constraint_analysis' in complexity:
                lines.append("Constraint Analysis:")
                constraints = complexity['constraint_analysis']
                lines.append(f"  - Enum Parameters: {constraints.get('enum_parameters', 0)}")
                lines.append(f"  - Pattern Parameters: {constraints.get('pattern_parameters', 0)}")
                lines.append(f"  - Bounded Parameters: {constraints.get('bounded_parameters', 0)}")
                lines.append(f"  - Unbounded Parameters: {constraints.get('unbounded_parameters', 0)}")
                lines.append("")
        
        # Prompt metrics
        if 'prompt_metrics' in metrics:
            lines.append("PROMPT METRICS")
            lines.append("-" * 80)
            prompt_metrics = metrics['prompt_metrics']
            lines.append(f"Prompt Length (chars): {prompt_metrics.get('prompt_length_chars', 0):,}")
            lines.append(f"Estimated Tokens: {prompt_metrics.get('estimated_tokens', 0):,}")
            lines.append("")
        
        # API usage
        if 'api_usage' in metrics:
            lines.append("API USAGE (Actual)")
            lines.append("-" * 80)
            usage = metrics['api_usage']
            lines.append(f"Prompt Tokens: {usage.get('prompt_tokens', 'N/A')}")
            lines.append(f"Completion Tokens: {usage.get('completion_tokens', 'N/A')}")
            lines.append(f"Total Tokens: {usage.get('total_tokens', 'N/A')}")
            lines.append("")
        
        # Response metrics
        if 'response_metrics' in metrics:
            lines.append("RESPONSE METRICS")
            lines.append("-" * 80)
            response_metrics = metrics['response_metrics']
            lines.append(f"Response Length (chars): {response_metrics.get('response_length_chars', 0):,}")
            lines.append(f"Estimated Response Tokens: {response_metrics.get('estimated_response_tokens', 0):,}")
            lines.append("")
        
        # Error info if any
        if 'api_response_error' in metrics:
            lines.append("ERROR INFORMATION")
            lines.append("-" * 80)
            lines.append(f"Error: {metrics['api_response_error']}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)

