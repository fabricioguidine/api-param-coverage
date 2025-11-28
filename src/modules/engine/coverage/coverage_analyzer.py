"""
Coverage Analyzer

Compares generated Gherkin scenarios with BRD requirements to calculate coverage metrics.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import time

from ...brd.brd_schema import BRDSchema, BRDRequirement
from ..analytics import MetricsCollector


class CoverageAnalyzer:
    """Analyzes test coverage by comparing Gherkin scenarios with BRD requirements."""
    
    def __init__(self, analytics_dir: Optional[str] = None):
        """
        Initialize the Coverage Analyzer.
        
        Args:
            analytics_dir: Analytics directory (default: "output/analytics")
        """
        analytics_path = analytics_dir or "output/analytics"
        self.metrics_collector = MetricsCollector(analytics_dir=analytics_path)
    
    def analyze_coverage(
        self,
        gherkin_content: str,
        brd: BRDSchema,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze coverage of Gherkin scenarios against BRD requirements.
        
        Args:
            gherkin_content: Generated Gherkin scenarios as string
            brd: BRD schema with requirements
            analysis_data: Swagger analysis data
            
        Returns:
            Coverage analysis report dictionary
        """
        start_time = time.time()
        
        # Parse Gherkin scenarios
        scenarios = self._parse_gherkin_scenarios(gherkin_content)
        
        # Map scenarios to BRD requirements
        requirement_coverage = self._map_scenarios_to_requirements(scenarios, brd)
        
        # Calculate coverage metrics
        coverage_metrics = self._calculate_coverage_metrics(requirement_coverage, brd)
        
        # Identify missing scenarios
        missing_scenarios = self._identify_missing_scenarios(requirement_coverage, brd)
        
        # Generate coverage gaps
        coverage_gaps = self._identify_coverage_gaps(requirement_coverage, brd)
        
        execution_time = time.time() - start_time
        
        coverage_report = {
            'total_requirements': len(brd.requirements),
            'total_scenarios': len(scenarios),
            'covered_requirements': coverage_metrics['covered_requirements'],
            'uncovered_requirements': coverage_metrics['uncovered_requirements'],
            'coverage_percentage': coverage_metrics['coverage_percentage'],
            'requirement_coverage': requirement_coverage,
            'missing_scenarios': missing_scenarios,
            'coverage_gaps': coverage_gaps,
            'execution_time': execution_time
        }
        
        # Track algorithm execution
        complexity_metrics = {
            "requirements_count": len(brd.requirements),
            "scenarios_count": len(scenarios),
            "average_scenarios_per_requirement": coverage_metrics.get('avg_scenarios_per_requirement', 0),
            "coverage_percentage": coverage_metrics['coverage_percentage']
        }
        
        algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
            algorithm_name="CoverageAnalyzer",
            algorithm_type="analyzer",
            input_data={"requirements": len(brd.requirements), "scenarios": len(scenarios)},
            output_data={"coverage_percentage": coverage_metrics['coverage_percentage']},
            execution_time=execution_time,
            complexity_metrics=complexity_metrics,
            llm_call=False,
            llm_metrics=None
        )
        report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
        if report_path:
            print(f"📈 Coverage analysis report saved: {report_path}")
        
        return coverage_report
    
    def _parse_gherkin_scenarios(self, gherkin_content: str) -> List[Dict[str, Any]]:
        """
        Parse Gherkin content to extract scenarios.
        
        Args:
            gherkin_content: Gherkin scenarios as string
            
        Returns:
            List of scenario dictionaries
        """
        scenarios = []
        lines = gherkin_content.split('\n')
        
        current_feature = None
        current_scenario = None
        current_steps = []
        current_tags = []
        in_scenario = False
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Feature
            if line.startswith('Feature:'):
                current_feature = line.replace('Feature:', '').strip()
                continue
            
            # Tags
            if line.startswith('@'):
                tags = re.findall(r'@(\w+)', line)
                current_tags = tags
                continue
            
            # Scenario
            if line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                # Save previous scenario
                if current_scenario:
                    scenarios.append({
                        'feature': current_feature,
                        'scenario': current_scenario,
                        'steps': current_steps.copy(),
                        'tags': current_tags.copy()
                    })
                
                current_scenario = line.replace('Scenario:', '').replace('Scenario Outline:', '').strip()
                current_steps = []
                in_scenario = True
                continue
            
            # Background
            if line.startswith('Background:'):
                in_scenario = False
                continue
            
            # Steps
            step_keywords = ['Given', 'When', 'Then', 'And', 'But']
            if in_scenario and any(line.startswith(kw) for kw in step_keywords):
                current_steps.append(line)
        
        # Add last scenario
        if current_scenario:
            scenarios.append({
                'feature': current_feature,
                'scenario': current_scenario,
                'steps': current_steps.copy(),
                'tags': current_tags.copy()
            })
        
        return scenarios
    
    def _map_scenarios_to_requirements(
        self,
        scenarios: List[Dict[str, Any]],
        brd: BRDSchema
    ) -> Dict[str, Dict[str, Any]]:
        """
        Map Gherkin scenarios to BRD requirements.
        
        Args:
            scenarios: Parsed Gherkin scenarios
            brd: BRD schema
            
        Returns:
            Dictionary mapping requirement_id to coverage information
        """
        requirement_coverage = {}
        
        # Initialize coverage for all requirements
        for requirement in brd.requirements:
            requirement_coverage[requirement.requirement_id] = {
                'requirement': requirement,
                'matched_scenarios': [],
                'scenario_count': 0,
                'coverage_percentage': 0.0,
                'matched_endpoints': []
            }
        
        # Try to match scenarios to requirements
        for scenario in scenarios:
            # Extract endpoint information from scenario steps
            endpoint_info = self._extract_endpoint_from_scenario(scenario)
            
            if endpoint_info:
                path, method = endpoint_info
                
                # Find matching requirements
                for requirement in brd.requirements:
                    if (requirement.endpoint_path == path and 
                        requirement.endpoint_method.upper() == method.upper()):
                        
                        requirement_coverage[requirement.requirement_id]['matched_scenarios'].append(scenario)
                        requirement_coverage[requirement.requirement_id]['scenario_count'] += 1
                        requirement_coverage[requirement.requirement_id]['matched_endpoints'].append((path, method))
        
        # Calculate coverage percentage for each requirement
        for req_id, coverage in requirement_coverage.items():
            requirement = coverage['requirement']
            expected_scenarios = len(requirement.test_scenarios)
            actual_scenarios = coverage['scenario_count']
            
            if expected_scenarios > 0:
                coverage['coverage_percentage'] = round((actual_scenarios / expected_scenarios * 100), 2)
            else:
                # If no expected scenarios, mark as covered if at least one scenario exists
                coverage['coverage_percentage'] = 100.0 if actual_scenarios > 0 else 0.0
        
        return requirement_coverage
    
    def _extract_endpoint_from_scenario(self, scenario: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Extract endpoint path and method from scenario steps.
        
        Args:
            scenario: Scenario dictionary
            
        Returns:
            Tuple of (path, method) or None
        """
        # Look for endpoint patterns in steps
        for step in scenario.get('steps', []):
            # Pattern: "When I send a GET request to "/users""
            match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+request\s+to\s+["\']([^"\']+)["\']', step, re.IGNORECASE)
            if match:
                method = match.group(1).upper()
                path = match.group(2)
                return (path, method)
            
            # Pattern: "When I send a request to "/users" with method GET"
            match = re.search(r'request\s+to\s+["\']([^"\']+)["\'].*?(GET|POST|PUT|DELETE|PATCH)', step, re.IGNORECASE)
            if match:
                path = match.group(1)
                method = match.group(2).upper()
                return (path, method)
        
        return None
    
    def _calculate_coverage_metrics(
        self,
        requirement_coverage: Dict[str, Dict[str, Any]],
        brd: BRDSchema
    ) -> Dict[str, Any]:
        """
        Calculate overall coverage metrics.
        
        Args:
            requirement_coverage: Requirement coverage mapping
            brd: BRD schema
            
        Returns:
            Coverage metrics dictionary
        """
        total_requirements = len(brd.requirements)
        covered_requirements = sum(
            1 for cov in requirement_coverage.values() 
            if cov['scenario_count'] > 0
        )
        uncovered_requirements = total_requirements - covered_requirements
        
        coverage_percentage = round((covered_requirements / total_requirements * 100), 2) if total_requirements > 0 else 0.0
        
        total_scenarios = sum(cov['scenario_count'] for cov in requirement_coverage.values())
        avg_scenarios_per_requirement = round(total_scenarios / total_requirements, 2) if total_requirements > 0 else 0.0
        
        return {
            'covered_requirements': covered_requirements,
            'uncovered_requirements': uncovered_requirements,
            'coverage_percentage': coverage_percentage,
            'avg_scenarios_per_requirement': avg_scenarios_per_requirement
        }
    
    def _identify_missing_scenarios(
        self,
        requirement_coverage: Dict[str, Dict[str, Any]],
        brd: BRDSchema
    ) -> List[Dict[str, Any]]:
        """
        Identify missing test scenarios for requirements.
        
        Args:
            requirement_coverage: Requirement coverage mapping
            brd: BRD schema
            
        Returns:
            List of missing scenario information
        """
        missing = []
        
        for requirement in brd.requirements:
            coverage = requirement_coverage.get(requirement.requirement_id, {})
            expected_count = len(requirement.test_scenarios)
            actual_count = coverage.get('scenario_count', 0)
            
            if actual_count < expected_count:
                missing.append({
                    'requirement_id': requirement.requirement_id,
                    'requirement_title': requirement.title,
                    'endpoint': f"{requirement.endpoint_method} {requirement.endpoint_path}",
                    'expected_scenarios': expected_count,
                    'actual_scenarios': actual_count,
                    'missing_count': expected_count - actual_count
                })
        
        return missing
    
    def _identify_coverage_gaps(
        self,
        requirement_coverage: Dict[str, Dict[str, Any]],
        brd: BRDSchema
    ) -> List[Dict[str, Any]]:
        """
        Identify coverage gaps (requirements with low or no coverage).
        
        Args:
            requirement_coverage: Requirement coverage mapping
            brd: BRD schema
            
        Returns:
            List of coverage gap information
        """
        gaps = []
        
        for requirement in brd.requirements:
            coverage = requirement_coverage.get(requirement.requirement_id, {})
            coverage_pct = coverage.get('coverage_percentage', 0.0)
            
            if coverage_pct < 100.0:
                gaps.append({
                    'requirement_id': requirement.requirement_id,
                    'requirement_title': requirement.title,
                    'endpoint': f"{requirement.endpoint_method} {requirement.endpoint_path}",
                    'priority': requirement.priority.value,
                    'coverage_percentage': coverage_pct,
                    'scenario_count': coverage.get('scenario_count', 0),
                    'expected_scenarios': len(requirement.test_scenarios)
                })
        
        # Sort by priority and coverage percentage
        gaps.sort(key=lambda x: (
            0 if x['priority'] == 'critical' else 1 if x['priority'] == 'high' else 2,
            x['coverage_percentage']
        ))
        
        return gaps
    
    def generate_coverage_report(
        self,
        coverage_report: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate a human-readable coverage report.
        
        Args:
            coverage_report: Coverage analysis report
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated report file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"output/coverage_report_{timestamp}.txt")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        lines.append("=" * 80)
        lines.append("Test Coverage Analysis Report")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("COVERAGE SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Requirements: {coverage_report['total_requirements']}")
        lines.append(f"Covered Requirements: {coverage_report['covered_requirements']}")
        lines.append(f"Uncovered Requirements: {coverage_report['uncovered_requirements']}")
        lines.append(f"Coverage Percentage: {coverage_report['coverage_percentage']}%")
        lines.append(f"Total Scenarios: {coverage_report['total_scenarios']}")
        lines.append(f"Execution Time: {coverage_report['execution_time']:.2f} seconds")
        lines.append("")
        
        # Requirement Coverage Details
        lines.append("REQUIREMENT COVERAGE DETAILS")
        lines.append("-" * 80)
        for req_id, coverage in coverage_report['requirement_coverage'].items():
            req = coverage['requirement']
            lines.append(f"\nRequirement: {req.requirement_id} - {req.title}")
            lines.append(f"  Endpoint: {req.endpoint_method} {req.endpoint_path}")
            lines.append(f"  Priority: {req.priority.value}")
            lines.append(f"  Scenarios: {coverage['scenario_count']} / {len(req.test_scenarios)} expected")
            lines.append(f"  Coverage: {coverage['coverage_percentage']}%")
        
        lines.append("")
        
        # Missing Scenarios
        if coverage_report['missing_scenarios']:
            lines.append("MISSING SCENARIOS")
            lines.append("-" * 80)
            for missing in coverage_report['missing_scenarios']:
                lines.append(f"\nRequirement: {missing['requirement_id']} - {missing['requirement_title']}")
                lines.append(f"  Endpoint: {missing['endpoint']}")
                lines.append(f"  Missing: {missing['missing_count']} scenarios")
                lines.append(f"  Expected: {missing['expected_scenarios']}, Actual: {missing['actual_scenarios']}")
        
        lines.append("")
        
        # Coverage Gaps
        if coverage_report['coverage_gaps']:
            lines.append("COVERAGE GAPS (Prioritized)")
            lines.append("-" * 80)
            for gap in coverage_report['coverage_gaps'][:10]:  # Top 10 gaps
                lines.append(f"\nRequirement: {gap['requirement_id']} - {gap['requirement_title']}")
                lines.append(f"  Endpoint: {gap['endpoint']}")
                lines.append(f"  Priority: {gap['priority']}")
                lines.append(f"  Coverage: {gap['coverage_percentage']}%")
                lines.append(f"  Scenarios: {gap['scenario_count']} / {gap['expected_scenarios']} expected")
        
        lines.append("")
        lines.append("=" * 80)
        
        # Write report
        output_path.write_text("\n".join(lines), encoding='utf-8')
        
        return output_path




