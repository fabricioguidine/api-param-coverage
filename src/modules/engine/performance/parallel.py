"""
Parallel Processing Module

Provides parallel processing capabilities for independent operations.
"""

from typing import List, Callable, Any, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing


class ParallelProcessor:
    """Handles parallel processing of independent operations."""
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Initialize the Parallel Processor.
        
        Args:
            max_workers: Maximum number of workers (default: CPU count)
            use_processes: Use processes instead of threads (default: False)
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.use_processes = use_processes
        self.executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    def process_parallel(
        self,
        items: List[Any],
        func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Process items in parallel.
        
        Args:
            items: List of items to process
            func: Function to apply to each item
            *args: Additional positional arguments for func
            **kwargs: Additional keyword arguments for func
            
        Returns:
            List of results in the same order as items
        """
        results = [None] * len(items)
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(func, item, *args, **kwargs): i
                for i, item in enumerate(items)
            }
            
            # Collect results
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    # Store error for debugging
                    results[index] = {'error': str(e)}
        
        return results
    
    def map_parallel(
        self,
        items: List[Any],
        func: Callable
    ) -> List[Any]:
        """
        Map function over items in parallel.
        
        Args:
            items: List of items to process
            func: Function to apply to each item
            
        Returns:
            List of results
        """
        with self.executor_class(max_workers=self.max_workers) as executor:
            results = list(executor.map(func, items))
        
        return results


def process_endpoints_parallel(
    endpoints: List[Dict[str, Any]],
    process_func: Callable,
    max_workers: Optional[int] = None
) -> List[Any]:
    """
    Process endpoints in parallel.
    
    Args:
        endpoints: List of endpoint dictionaries
        process_func: Function to process each endpoint
        max_workers: Maximum number of workers
        
    Returns:
        List of processed results
    """
    processor = ParallelProcessor(max_workers=max_workers)
    return processor.process_parallel(endpoints, process_func)

