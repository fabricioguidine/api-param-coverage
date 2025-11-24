"""
Schema Cross-Reference

Cross-references BRD requirements with Swagger schema to filter test scope.
"""

import time
from typing import Dict, Any, List, Tuple, Optional
from ..brd import BRDSchema, BRDRequirement
from ..engine.algorithms import SchemaAnalyzer
from ..engine.analytics import MetricsCollector


class SchemaCrossReference:
    """Cross-references BRD with Swagger schema to determine test scope."""
    
    def __init__(self):
        """Initialize the Schema Cross-Reference."""
        self.metrics_collector = MetricsCollector()
    
    def filter_endpoints_by_brd(
        self,
        analysis_data: Dict[str, Any],
        brd: BRDSchema
    ) -> Dict[str, Any]:
        """
        Filter analysis data to only include endpoints covered by BRD requirements.
        
        Args:
            analysis_data: Full schema analysis data
            brd: BRD schema with requirements
            
        Returns:
            Filtered analysis data containing only BRD-covered endpoints
        """
        start_time = time.time()
        
        # Get all endpoints from BRD
        brd_endpoints = brd.get_all_endpoints()
        brd_endpoint_set = set(brd_endpoints)
        
        # Filter analysis data endpoints
        all_endpoints = analysis_data.get('endpoints', [])
        filtered_endpoints = []
        
        for endpoint in all_endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '').upper()
            
            # Check if this endpoint is in BRD
            if (path, method) in brd_endpoint_set:
                # Get BRD requirements for this endpoint
                requirements = brd.get_requirements_for_endpoint(path, method)
                
                # Add BRD metadata to endpoint
                endpoint_copy = endpoint.copy()
                endpoint_copy['brd_requirements'] = [
                    {
                        'requirement_id': req.requirement_id,
                        'title': req.title,
                        'priority': req.priority.value,
                        'test_scenarios_count': len(req.test_scenarios)
                    }
                    for req in requirements
                ]
                endpoint_copy['brd_covered'] = True
                
                filtered_endpoints.append(endpoint_copy)
            else:
                # Mark as not covered by BRD
                endpoint_copy = endpoint.copy()
                endpoint_copy['brd_covered'] = False
                # Optionally include non-covered endpoints with a flag
                # filtered_endpoints.append(endpoint_copy)
        
        # Create filtered analysis data
        filtered_analysis = {
            'endpoints': filtered_endpoints,
            'total_endpoints': len(all_endpoints),
            'brd_covered_endpoints': len(filtered_endpoints),
            'brd_endpoints': len(brd_endpoints),
            'coverage_percentage': round((len(filtered_endpoints) / len(all_endpoints) * 100), 2) if all_endpoints else 0
        }
        
        execution_time = time.time() - start_time
        
        # Track algorithm execution
        complexity_metrics = {
            "total_endpoints": len(all_endpoints),
            "filtered_endpoints": len(filtered_endpoints),
            "coverage_percentage": filtered_analysis['coverage_percentage'],
            "brd_requirements_count": len(brd.requirements)
        }
        
        algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
            algorithm_name="SchemaCrossReference",
            algorithm_type="cross_reference",
            input_data={"endpoints_count": len(all_endpoints), "brd_requirements": len(brd.requirements)},
            output_data={"filtered_endpoints": len(filtered_endpoints)},
            execution_time=execution_time,
            complexity_metrics=complexity_metrics,
            llm_call=False,
            llm_metrics=None
        )
        report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
        if report_path:
            print(f"📈 Cross-reference report saved: {report_path}")
        
        return filtered_analysis
    
    def get_brd_coverage_report(
        self,
        analysis_data: Dict[str, Any],
        brd: BRDSchema
    ) -> Dict[str, Any]:
        """
        Generate a coverage report showing which endpoints are covered by BRD.
        
        Args:
            analysis_data: Full schema analysis data
            brd: BRD schema
            
        Returns:
            Coverage report dictionary
        """
        all_endpoints = analysis_data.get('endpoints', [])
        brd_endpoints = brd.get_all_endpoints()
        brd_endpoint_set = set(brd_endpoints)
        
        covered = []
        not_covered = []
        
        for endpoint in all_endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '').upper()
            
            endpoint_info = {
                'path': path,
                'method': method,
                'parameters_count': len(endpoint.get('parameters', []))
            }
            
            if (path, method) in brd_endpoint_set:
                requirements = brd.get_requirements_for_endpoint(path, method)
                endpoint_info['requirements'] = [
                    {
                        'requirement_id': req.requirement_id,
                        'title': req.title,
                        'priority': req.priority.value
                    }
                    for req in requirements
                ]
                covered.append(endpoint_info)
            else:
                not_covered.append(endpoint_info)
        
        total = len(all_endpoints)
        coverage_pct = round((len(covered) / total * 100), 2) if total > 0 else 0
        
        return {
            'total_endpoints': total,
            'covered_endpoints': len(covered),
            'not_covered_endpoints': len(not_covered),
            'coverage_percentage': coverage_pct,
            'covered': covered,
            'not_covered': not_covered
        }

