"""
Performance Profiler

Profiles algorithm execution and identifies performance bottlenecks.
"""

import time
import cProfile
import pstats
import io
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime


class PerformanceProfiler:
    """Profiles algorithm execution and generates performance reports."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the Performance Profiler.
        
        Args:
            output_dir: Directory for performance reports (default: output/performance)
        """
        self.output_dir = Path(output_dir) if output_dir else Path("output/performance")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, cProfile.Profile] = {}
    
    def profile_function(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, Dict[str, Any]]:
        """
        Profile a function execution.
        
        Args:
            func: Function to profile
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of (function result, performance metrics)
        """
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        profiler.disable()
        
        # Generate stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        metrics = {
            'execution_time': execution_time,
            'stats': stats_stream.getvalue(),
            'total_calls': stats.total_calls,
            'primitive_calls': stats.primitive_calls
        }
        
        return result, metrics
    
    def save_profile_report(
        self,
        algorithm_name: str,
        metrics: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Path:
        """
        Save performance profile report to file.
        
        Args:
            algorithm_name: Name of the algorithm
            metrics: Performance metrics dictionary
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to saved report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"profile_{algorithm_name}_{timestamp}.txt"
        
        report_path = self.output_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Performance Profile: {algorithm_name}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Execution Time: {metrics['execution_time']:.4f} seconds\n")
            f.write(f"Total Calls: {metrics['total_calls']}\n")
            f.write(f"Primitive Calls: {metrics['primitive_calls']}\n\n")
            f.write("Top Functions by Cumulative Time:\n")
            f.write("-" * 70 + "\n")
            f.write(metrics['stats'])
        
        return report_path


def profile_algorithm(profiler: Optional[PerformanceProfiler] = None):
    """
    Decorator to profile algorithm execution.
    
    Args:
        profiler: Optional PerformanceProfiler instance (creates new one if None)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prof = profiler or PerformanceProfiler()
            result, metrics = prof.profile_function(func, *args, **kwargs)
            
            # Save report
            algorithm_name = func.__name__
            prof.save_profile_report(algorithm_name, metrics)
            
            return result
        return wrapper
    return decorator


