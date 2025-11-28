"""
Performance Module

Provides performance profiling, caching, optimization, and parallel processing.
"""

from .profiler import PerformanceProfiler, profile_algorithm
from .cache import Cache, cached
from .optimizer import (
    DataStructureOptimizer,
    AlgorithmOptimizer,
    optimize_data_structures
)
from .parallel import ParallelProcessor, process_endpoints_parallel

__all__ = [
    'PerformanceProfiler',
    'profile_algorithm',
    'Cache',
    'cached',
    'DataStructureOptimizer',
    'AlgorithmOptimizer',
    'optimize_data_structures',
    'ParallelProcessor',
    'process_endpoints_parallel'
]




