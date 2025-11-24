"""
Performance Optimizer

Optimizes data structure operations and algorithm performance.
"""

from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict
import time


class DataStructureOptimizer:
    """Optimizes common data structure operations."""
    
    @staticmethod
    def optimize_dict_access(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize dictionary access patterns.
        
        Args:
            data: Dictionary to optimize
            
        Returns:
            Optimized dictionary (currently returns as-is, placeholder for future optimizations)
        """
        # Future: Could implement dict views, __missing__ handlers, etc.
        return data
    
    @staticmethod
    def batch_operations(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
        """
        Split items into batches for efficient processing.
        
        Args:
            items: List of items to batch
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    @staticmethod
    def optimize_list_comprehension(data: List[Any], filter_func: Optional[Callable] = None) -> List[Any]:
        """
        Optimize list operations using comprehensions.
        
        Args:
            data: List to process
            filter_func: Optional filter function
            
        Returns:
            Filtered list
        """
        if filter_func:
            return [item for item in data if filter_func(item)]
        return data


class AlgorithmOptimizer:
    """Optimizes algorithm execution."""
    
    @staticmethod
    def memoize(func: Callable) -> Callable:
        """
        Memoization decorator for functions with hashable arguments.
        
        Args:
            func: Function to memoize
            
        Returns:
            Memoized function
        """
        cache = {}
        
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        
        return wrapper
    
    @staticmethod
    def optimize_endpoint_processing(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize endpoint processing by pre-computing common operations.
        
        Args:
            endpoints: List of endpoint dictionaries
            
        Returns:
            Optimized list of endpoints
        """
        # Pre-compute method counts
        method_counts = defaultdict(int)
        for endpoint in endpoints:
            method = endpoint.get('method', '').upper()
            method_counts[method] += 1
        
        # Add pre-computed metadata to each endpoint
        for endpoint in endpoints:
            method = endpoint.get('method', '').upper()
            endpoint['_method_count'] = method_counts[method]
            endpoint['_has_params'] = bool(endpoint.get('parameters'))
            endpoint['_param_count'] = len(endpoint.get('parameters', []))
        
        return endpoints


def optimize_data_structures(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize data structures in analysis data.
    
    Args:
        data: Analysis data dictionary
        
    Returns:
        Optimized data dictionary
    """
    optimizer = DataStructureOptimizer()
    
    # Optimize endpoints list
    if 'endpoints' in data:
        algo_optimizer = AlgorithmOptimizer()
        data['endpoints'] = algo_optimizer.optimize_endpoint_processing(data['endpoints'])
    
    # Optimize dictionary access
    data = optimizer.optimize_dict_access(data)
    
    return data

