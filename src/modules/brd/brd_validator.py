"""
BRD Validator

Validates BRD schemas against Swagger endpoints to ensure consistency.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from ..brd import BRDSchema
from ..engine.analytics import MetricsCollector
import time


class BRDValidator:
    """Validates BRD schemas against Swagger schemas."""
    
    def __init__(self, analytics_dir: Optional[str] = None):
        """
        Initialize the BRD Validator.
        
        Args:
            analytics_dir: Analytics directory (default: "output/analytics")
                          Typically should be: <run_output_dir>/analytics/
        """
        analytics_path = analytics_dir or "output/analytics"
        self.metrics_collector = MetricsCollector(analytics_dir=analytics_path)
    
    def validate_brd_against_swagger(
        self,
        brd: BRDSchema,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate BRD schema against Swagger analysis data.
        
        Args:
            brd: BRD schema to validate
            analysis_data: Swagger schema analysis data
            
        Returns:
            Validation report dictionary
        """
        start_time = time.time()
        
        # Get all endpoints from Swagger
        swagger_endpoints = analysis_data.get('endpoints', [])
        swagger_endpoint_set = {
            (ep.get('path', ''), ep.get('method', '').upper())
            for ep in swagger_endpoints
        }
        
        # Get all endpoints from BRD
        brd_endpoints = brd.get_all_endpoints()
        brd_endpoint_set = set(brd_endpoints)
        
        # Find orphaned requirements (endpoints in BRD but not in Swagger)
        orphaned_endpoints = brd_endpoint_set - swagger_endpoint_set
        
        # Find missing endpoints (endpoints in Swagger but not in BRD)
        missing_endpoints = swagger_endpoint_set - brd_endpoint_set
        
        # Validate endpoint paths and methods
        validation_errors = []
        for requirement in brd.requirements:
            path = requirement.endpoint_path
            method = requirement.endpoint_method.upper()
            
            # Check if endpoint exists in Swagger
            if (path, method) not in swagger_endpoint_set:
                # Try fuzzy matching for path parameters
                matched = self._fuzzy_match_endpoint(path, method, swagger_endpoint_set)
                if not matched:
                    validation_errors.append({
                        'requirement_id': requirement.requirement_id,
                        'endpoint': f"{method} {path}",
                        'error': 'Endpoint not found in Swagger schema',
                        'suggestion': self._suggest_similar_endpoint(path, method, swagger_endpoint_set)
                    })
        
        # Calculate validation metrics
        total_brd_endpoints = len(brd_endpoint_set)
        total_swagger_endpoints = len(swagger_endpoint_set)
        matched_endpoints = len(brd_endpoint_set & swagger_endpoint_set)
        match_percentage = round((matched_endpoints / total_swagger_endpoints * 100), 2) if total_swagger_endpoints > 0 else 0
        
        execution_time = time.time() - start_time
        
        validation_report = {
            'is_valid': len(validation_errors) == 0 and len(orphaned_endpoints) == 0,
            'total_brd_endpoints': total_brd_endpoints,
            'total_swagger_endpoints': total_swagger_endpoints,
            'matched_endpoints': matched_endpoints,
            'match_percentage': match_percentage,
            'orphaned_endpoints': list(orphaned_endpoints),
            'missing_endpoints': list(missing_endpoints),
            'validation_errors': validation_errors,
            'execution_time': execution_time
        }
        
        # Track algorithm execution
        complexity_metrics = {
            "brd_endpoints_count": total_brd_endpoints,
            "swagger_endpoints_count": total_swagger_endpoints,
            "match_percentage": match_percentage,
            "orphaned_count": len(orphaned_endpoints),
            "missing_count": len(missing_endpoints),
            "error_count": len(validation_errors)
        }
        
        algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
            algorithm_name="BRDValidator",
            algorithm_type="validator",
            input_data={"brd_requirements": len(brd.requirements), "swagger_endpoints": total_swagger_endpoints},
            output_data={"validation_result": validation_report['is_valid']},
            execution_time=execution_time,
            complexity_metrics=complexity_metrics,
            llm_call=False,
            llm_metrics=None
        )
        report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
        if report_path:
            print(f"📈 BRD Validation report saved: {report_path}")
        
        return validation_report
    
    def _fuzzy_match_endpoint(
        self,
        path: str,
        method: str,
        swagger_endpoint_set: set
    ) -> Optional[Tuple[str, str]]:
        """
        Try to find a similar endpoint using fuzzy matching.
        
        Args:
            path: BRD endpoint path
            method: HTTP method
            swagger_endpoint_set: Set of (path, method) tuples from Swagger
            
        Returns:
            Matched (path, method) tuple or None
        """
        # Normalize path by replacing path parameters
        def normalize_path(p: str) -> str:
            import re
            # Replace {param} with {*}
            return re.sub(r'\{[^}]+\}', '{*}', p)
        
        normalized_brd_path = normalize_path(path)
        
        for swagger_path, swagger_method in swagger_endpoint_set:
            if swagger_method == method:
                normalized_swagger_path = normalize_path(swagger_path)
                if normalized_brd_path == normalized_swagger_path:
                    return (swagger_path, swagger_method)
        
        return None
    
    def _suggest_similar_endpoint(
        self,
        path: str,
        method: str,
        swagger_endpoint_set: set
    ) -> Optional[str]:
        """
        Suggest a similar endpoint from Swagger.
        
        Args:
            path: BRD endpoint path
            method: HTTP method
            swagger_endpoint_set: Set of (path, method) tuples from Swagger
            
        Returns:
            Suggested endpoint string or None
        """
        # Find endpoints with same method
        same_method_endpoints = [
            (p, m) for p, m in swagger_endpoint_set if m == method.upper()
        ]
        
        if not same_method_endpoints:
            return None
        
        # Simple similarity: check if path segments match
        brd_segments = path.strip('/').split('/')
        
        best_match = None
        best_score = 0
        
        for swagger_path, _ in same_method_endpoints:
            swagger_segments = swagger_path.strip('/').split('/')
            
            # Calculate similarity score
            if len(brd_segments) == len(swagger_segments):
                matches = sum(1 for b, s in zip(brd_segments, swagger_segments) 
                            if b == s or b.startswith('{') or s.startswith('{'))
                score = matches / len(brd_segments) if brd_segments else 0
                
                if score > best_score:
                    best_score = score
                    best_match = f"{method} {swagger_path}"
        
        return best_match if best_score > 0.5 else None
    
    def generate_validation_report(
        self,
        validation_report: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_report: Validation report dictionary
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated report file
        """
        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"docs/brd_validation_report_{timestamp}.txt")
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        lines.append("=" * 80)
        lines.append("BRD Validation Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("VALIDATION SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Status: {'✓ VALID' if validation_report['is_valid'] else '✗ INVALID'}")
        lines.append(f"BRD Endpoints: {validation_report['total_brd_endpoints']}")
        lines.append(f"Swagger Endpoints: {validation_report['total_swagger_endpoints']}")
        lines.append(f"Matched Endpoints: {validation_report['matched_endpoints']}")
        lines.append(f"Match Percentage: {validation_report['match_percentage']}%")
        lines.append(f"Execution Time: {validation_report['execution_time']:.2f} seconds")
        lines.append("")
        
        # Orphaned endpoints
        if validation_report['orphaned_endpoints']:
            lines.append("ORPHANED ENDPOINTS (in BRD but not in Swagger)")
            lines.append("-" * 80)
            for path, method in validation_report['orphaned_endpoints']:
                lines.append(f"  - {method} {path}")
            lines.append("")
        
        # Missing endpoints
        if validation_report['missing_endpoints']:
            lines.append("MISSING ENDPOINTS (in Swagger but not in BRD)")
            lines.append("-" * 80)
            for path, method in validation_report['missing_endpoints']:
                lines.append(f"  - {method} {path}")
            lines.append("")
        
        # Validation errors
        if validation_report['validation_errors']:
            lines.append("VALIDATION ERRORS")
            lines.append("-" * 80)
            for error in validation_report['validation_errors']:
                lines.append(f"Requirement: {error['requirement_id']}")
                lines.append(f"  Endpoint: {error['endpoint']}")
                lines.append(f"  Error: {error['error']}")
                if error.get('suggestion'):
                    lines.append(f"  Suggestion: {error['suggestion']}")
                lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        if validation_report['orphaned_endpoints']:
            lines.append("• Remove or update orphaned endpoints in BRD")
        if validation_report['missing_endpoints']:
            lines.append(f"• Consider adding {len(validation_report['missing_endpoints'])} missing endpoints to BRD")
        if validation_report['match_percentage'] < 100:
            lines.append(f"• Improve BRD coverage (currently {validation_report['match_percentage']}%)")
        if not validation_report['orphaned_endpoints'] and not validation_report['missing_endpoints']:
            lines.append("• BRD is well-aligned with Swagger schema")
        lines.append("")
        
        lines.append("=" * 80)
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path

