"""
Coverage Handler

Handles coverage filtering logic for endpoints.
"""

from typing import Dict, Any, Optional, List, Tuple
from ..brd import BRDSchema
from ..brd import SchemaCrossReference
from ..utils.constants import (
    DEFAULT_COVERAGE_PERCENTAGE,
    HTTP_METHOD_PRIORITY,
    PARAM_COMPLEXITY_MULTIPLIER,
    PARAM_COMPLEXITY_MAX,
    REQUIRED_PARAM_MULTIPLIER
)


def calculate_endpoint_priority(endpoint: Dict[str, Any]) -> float:
    """
    Calculate priority score for an endpoint.
    
    Args:
        endpoint: Endpoint dictionary with 'method' and 'parameters' keys
        
    Returns:
        Priority score (higher = more important)
    """
    method = endpoint.get('method', '').upper()
    params = endpoint.get('parameters', [])
    
    score = HTTP_METHOD_PRIORITY.get(method, 30.0)
    score += min(len(params) * PARAM_COMPLEXITY_MULTIPLIER, PARAM_COMPLEXITY_MAX)
    
    required_params = [p for p in params if p.get('required', False)]
    score += len(required_params) * REQUIRED_PARAM_MULTIPLIER
    
    return score


def apply_coverage_filter(
    analysis_data: Dict[str, Any],
    coverage_percentage: float = DEFAULT_COVERAGE_PERCENTAGE
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply coverage percentage filter to endpoints.
    
    Args:
        analysis_data: Schema analysis data
        coverage_percentage: Percentage of endpoints to include (1-100)
        
    Returns:
        Tuple of (filtered_analysis_data, coverage_report)
    """
    all_endpoints = analysis_data.get('endpoints', [])
    total_endpoints = len(all_endpoints)
    target_count = max(1, int(total_endpoints * (coverage_percentage / 100.0)))
    
    # Sort by priority and take top N
    sorted_endpoints = sorted(all_endpoints, key=calculate_endpoint_priority, reverse=True)
    selected_endpoints = sorted_endpoints[:target_count]
    
    filtered_analysis_data = {
        **analysis_data,
        'endpoints': selected_endpoints
    }
    
    coverage_report = {
        'total_endpoints': total_endpoints,
        'selected_endpoints': len(selected_endpoints),
        'coverage_percentage': coverage_percentage,
        'not_covered_endpoints': total_endpoints - len(selected_endpoints)
    }
    
    return filtered_analysis_data, coverage_report


def apply_brd_filter(
    analysis_data: Dict[str, Any],
    brd: BRDSchema
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply BRD-based filtering to endpoints.
    
    Args:
        analysis_data: Schema analysis data
        brd: BRD schema to filter against
        
    Returns:
        Tuple of (filtered_analysis_data, coverage_report)
    """
    cross_ref = SchemaCrossReference()
    filtered_analysis_data = cross_ref.filter_endpoints_by_brd(analysis_data, brd)
    coverage_report = cross_ref.get_brd_coverage_report(analysis_data, brd)
    
    return filtered_analysis_data, coverage_report

