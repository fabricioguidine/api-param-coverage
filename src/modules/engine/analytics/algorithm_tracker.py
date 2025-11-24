"""
Algorithm Tracker

Helper module to track algorithm execution and complexity analysis.
"""

import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from .metrics_collector import MetricsCollector


class AlgorithmTracker:
    """Tracks algorithm execution and generates reports."""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the Algorithm Tracker.
        
        Args:
            metrics_collector: MetricsCollector instance (creates new one if None)
        """
        self.metrics_collector = metrics_collector or MetricsCollector()
    
    def track_algorithm(
        self,
        algorithm_name: str,
        algorithm_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        complexity_metrics: Optional[Dict[str, Any]] = None,
        llm_call: bool = False,
        llm_metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Track algorithm execution and save report.
        
        Args:
            algorithm_name: Name of the algorithm
            algorithm_type: Type of algorithm
            input_data: Input data for complexity analysis
            output_data: Output data for complexity analysis
            execution_time: Execution time in seconds
            complexity_metrics: Algorithm-specific complexity metrics
            llm_call: Whether LLM was called
            llm_metrics: LLM-specific metrics
        """
        try:
            algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
                algorithm_name=algorithm_name,
                algorithm_type=algorithm_type,
                input_data=input_data,
                output_data=output_data,
                execution_time=None,  # Will be set by decorator
                complexity_metrics=complexity_metrics,
                llm_call=llm_call,
                llm_metrics=llm_metrics
            )
            
            report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
            return report_path
        except Exception as e:
            print(f"⚠ Warning: Failed to track algorithm {algorithm_name}: {e}")
            return None
    
    def track_execution(
        self,
        algorithm_name: str,
        algorithm_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator to track algorithm execution with timing.
        
        Usage:
            @tracker.track_execution("SchemaAnalyzer", "analyzer")
            def analyze_schema(self, schema):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # Extract input data if not provided
                if input_data is None and args:
                    # Try to get input from first argument
                    if isinstance(args[0], dict):
                        input_data_for_tracking = args[0]
                    else:
                        input_data_for_tracking = {"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
                else:
                    input_data_for_tracking = input_data
                
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    execution_time = time.time() - start_time
                    
                    # Analyze output
                    output_data_for_tracking = None
                    if result:
                        if isinstance(result, dict):
                            output_data_for_tracking = result
                        else:
                            output_data_for_tracking = {"result_type": type(result).__name__, "has_result": True}
                    
                    # Calculate complexity metrics
                    complexity_metrics = self._calculate_complexity_metrics(result)
                    
                    # Track the algorithm
                    algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
                        algorithm_name=algorithm_name,
                        algorithm_type=algorithm_type,
                        input_data=input_data_for_tracking,
                        output_data=output_data_for_tracking,
                        execution_time=execution_time,
                        complexity_metrics=complexity_metrics,
                        llm_call=False,
                        llm_metrics=None
                    )
                    
                    report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
                    if report_path:
                        print(f"📈 Algorithm report saved: {report_path}")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    print(f"⚠ Error in {algorithm_name}: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def _calculate_complexity_metrics(self, result: Any) -> Dict[str, Any]:
        """Calculate complexity metrics from algorithm result."""
        metrics = {}
        
        if isinstance(result, dict):
            # Count endpoints if present
            if 'endpoints' in result:
                endpoints = result['endpoints']
                metrics['endpoints_count'] = len(endpoints)
                
                # Calculate average parameters per endpoint
                total_params = sum(len(ep.get('parameters', [])) for ep in endpoints)
                metrics['average_parameters_per_endpoint'] = round(total_params / len(endpoints), 2) if endpoints else 0
                metrics['total_parameters'] = total_params
            
            # Count requirements if present
            if 'requirements' in result:
                metrics['requirements_count'] = len(result['requirements'])
            
            # Count total elements
            metrics['total_elements'] = len(result)
        
        return metrics

