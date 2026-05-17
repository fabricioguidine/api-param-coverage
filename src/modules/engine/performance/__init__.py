"""
Performance Module

Provides performance profiling, caching, optimization, and parallel processing.
"""

from .cache import Cache, cached
from .optimizer import AlgorithmOptimizer, DataStructureOptimizer, optimize_data_structures
from .parallel import ParallelProcessor, process_endpoints_parallel
from .profiler import PerformanceProfiler, profile_algorithm

__all__ = [
    "AlgorithmOptimizer",
    "Cache",
    "DataStructureOptimizer",
    "ParallelProcessor",
    "PerformanceProfiler",
    "cached",
    "optimize_data_structures",
    "process_endpoints_parallel",
    "profile_algorithm",
]
