"""
BRD Generator

Generates BRD (Business Requirement Document) schemas using LLM based on Swagger schema analysis.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..brd.brd_schema import (
    BRDSchema, BRDRequirement, BRDTestScenario, 
    RequirementPriority, RequirementStatus
)
from ..engine.llm import LLMPrompter
from ..engine.analytics import MetricsCollector
from ..utils import extract_json_from_response
from ..utils.constants import DEFAULT_COVERAGE_PERCENTAGE, MAX_COVERAGE_PERCENTAGE, MIN_COVERAGE_PERCENTAGE
import time


class BRDGenerator:
    """Generates BRD schemas from Swagger schemas using LLM."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", provider: str = "openai", analytics_dir: Optional[str] = None):
        """
        Initialize the BRD Generator.
        
        Args:
            api_key: LLM API key
            model: LLM model to use
            provider: LLM provider ('openai', 'anthropic', 'google', 'azure')
            analytics_dir: Analytics directory (default: "output/analytics")
                          Typically should be: <run_output_dir>/analytics/
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.llm_prompter = LLMPrompter(model=model, api_key=api_key, provider=provider) if api_key else None
        analytics_path = analytics_dir or "output/analytics"
        self.metrics_collector = MetricsCollector(analytics_dir=analytics_path)
    
    def generate_brd_from_swagger(
        self,
        processed_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        schema_filename: str,
        coverage_percentage: float = 100.0
    ) -> Optional[BRDSchema]:
        """
        Generate a BRD schema from Swagger schema using heuristic analysis and LLM.
        
        Args:
            processed_data: Processed schema data from SchemaProcessor
            analysis_data: Analysis data from SchemaAnalyzer
            schema_filename: Name of the schema file
            coverage_percentage: Percentage of endpoints to include (1-100, default: 100)
            
        Returns:
            BRDSchema object, or None if generation fails
        """
        if not self.llm_prompter:
            error_msg = (
                "BRD generation requires an OpenAI API key. "
                "Please provide an API key via OPENAI_API_KEY environment variable "
                "or pass it to BRDGenerator constructor."
            )
            print(f"✗ Error: {error_msg}")
            return None
        
        # Validate coverage percentage
        if coverage_percentage < MIN_COVERAGE_PERCENTAGE or coverage_percentage > MAX_COVERAGE_PERCENTAGE:
            print(f"⚠ Warning: Invalid coverage percentage ({coverage_percentage}). "
                  f"Expected value between {MIN_COVERAGE_PERCENTAGE} and {MAX_COVERAGE_PERCENTAGE}. "
                  f"Using {DEFAULT_COVERAGE_PERCENTAGE}% as default.")
            coverage_percentage = DEFAULT_COVERAGE_PERCENTAGE
        
        print(f"📋 Generating BRD from Swagger schema using heuristic analysis...")
        print(f"   Target coverage: {coverage_percentage}% of endpoints")
        start_time = time.time()
        
        try:
            # Step 1: Analyze Swagger to create test plan heuristic with coverage filter
            test_plan = self._create_test_plan_heuristic(processed_data, analysis_data, coverage_percentage)
            
            # Step 2: Use LLM to generate structured BRD (with filtered endpoints)
            # The test_plan already contains only selected endpoints, so we use it directly
            brd_data = self._generate_brd_with_llm(test_plan, processed_data, analysis_data)
            
            if not brd_data:
                return None
            
            # Step 3: Parse LLM response into BRDSchema
            brd = self._parse_llm_brd_response(brd_data, processed_data)
            
            execution_time = time.time() - start_time
            
            # Track algorithm execution
            if brd:
                complexity_metrics = {
                    "requirements_count": len(brd.requirements),
                    "total_test_scenarios": sum(len(req.test_scenarios) for req in brd.requirements),
                    "average_scenarios_per_requirement": round(sum(len(req.test_scenarios) for req in brd.requirements) / len(brd.requirements), 2) if brd.requirements else 0
                }
                
                algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
                    algorithm_name="BRDGenerator",
                    algorithm_type="generator",
                    input_data={"endpoints_count": len(analysis_data.get('endpoints', []))},
                    output_data={"requirements": len(brd.requirements)},
                    execution_time=execution_time,
                    complexity_metrics=complexity_metrics,
                    llm_call=True,
                    llm_metrics={"brd_generation": True}
                )
                report_path = self.metrics_collector.save_algorithm_report(algorithm_metrics)
                if report_path:
                    print(f"📈 BRD Generator report saved: {report_path}")
            
            return brd
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            print(f"✗ Error in BRD generation ({error_type}): {e}")
            print(f"   Execution time: {execution_time:.2f}s")
            print(f"   Schema: {schema_filename}")
            raise
    
    def _create_test_plan_heuristic(
        self,
        processed_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        coverage_percentage: float = 100.0
    ) -> Dict[str, Any]:
        """
        Create a test plan heuristic by analyzing the Swagger schema.
        
        Args:
            processed_data: Processed schema data
            analysis_data: Analysis data
            coverage_percentage: Percentage of endpoints to include (1-100)
            
        Returns:
            Dictionary with test plan heuristic
        """
        all_endpoints = analysis_data.get('endpoints', [])
        api_info = processed_data.get('info', {})
        
        # Filter endpoints based on coverage percentage
        total_endpoints = len(all_endpoints)
        target_count = max(1, int(total_endpoints * (coverage_percentage / 100.0)))
        
        # Select endpoints based on priority (high priority first)
        # Sort endpoints by priority heuristic
        endpoints_with_priority = []
        for endpoint in all_endpoints:
            method = endpoint.get('method', '')
            params = endpoint.get('parameters', [])
            priority_score = self._calculate_priority_score(method, params)
            endpoints_with_priority.append((priority_score, endpoint))
        
        # Sort by priority score (descending) and take top N
        endpoints_with_priority.sort(key=lambda x: x[0], reverse=True)
        selected_endpoints = [endpoint for _, endpoint in endpoints_with_priority[:target_count]]
        
        print(f"   Selected {len(selected_endpoints)} out of {total_endpoints} endpoints ({coverage_percentage}% coverage)")
        
        # Analyze endpoints and create priority/coverage suggestions
        test_plan = {
            "api_name": api_info.get('title', 'Unknown API'),
            "api_version": api_info.get('version', 'Unknown'),
            "total_endpoints": total_endpoints,
            "selected_endpoints": len(selected_endpoints),
            "coverage_percentage": coverage_percentage,
            "endpoint_analysis": []
        }
        
        for endpoint in selected_endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '')
            params = endpoint.get('parameters', [])
            
            # Heuristic: Determine priority based on method and complexity
            priority = self._determine_priority_heuristic(method, params)
            
            # Heuristic: Determine test scenarios based on parameters
            suggested_scenarios = self._suggest_test_scenarios(method, params)
            
            test_plan["endpoint_analysis"].append({
                "path": path,
                "method": method,
                "suggested_priority": priority,
                "parameter_count": len(params),
                "suggested_scenarios": suggested_scenarios
            })
        
        return test_plan
    
    def _calculate_priority_score(self, method: str, params: List[Dict]) -> float:
        """
        Calculate a numeric priority score for endpoint selection.
        Higher score = higher priority for inclusion.
        
        Args:
            method: HTTP method
            params: List of parameters
            
        Returns:
            Priority score (float)
        """
        method_upper = method.upper()
        score = HTTP_METHOD_PRIORITY.get(method_upper, 30.0)
        
        # Parameter complexity bonus
        score += min(len(params) * PARAM_COMPLEXITY_MULTIPLIER, PARAM_COMPLEXITY_MAX)
        
        # Required parameters bonus
        required_params = [p for p in params if p.get('required', False)]
        score += len(required_params) * REQUIRED_PARAM_MULTIPLIER
        
        return score
    
    def _determine_priority_heuristic(self, method: str, params: List[Dict[str, Any]]) -> str:
        """Determine priority based on HTTP method and parameter complexity."""
        method_upper = method.upper()
        
        # Critical operations
        if method_upper in ['POST', 'PUT', 'DELETE']:
            return "high"
        
        # Important read operations
        if method_upper == 'GET':
            if len(params) > 5:  # Complex queries
                return "high"
            return "medium"
        
        # Other methods
        return "medium"
    
    def _suggest_test_scenarios(self, method: str, params: List[Dict[str, Any]]) -> List[str]:
        """Suggest test scenarios based on method and parameters."""
        scenarios = []
        method_upper = method.upper()
        
        # Base scenarios by method
        if method_upper == 'GET':
            scenarios.append("Valid request with correct parameters")
            scenarios.append("Request with missing required parameters")
            scenarios.append("Request with invalid parameter values")
        elif method_upper == 'POST':
            scenarios.append("Create resource with valid data")
            scenarios.append("Create resource with missing required fields")
            scenarios.append("Create resource with invalid data format")
            scenarios.append("Create resource with duplicate data")
        elif method_upper == 'PUT':
            scenarios.append("Update resource with valid data")
            scenarios.append("Update non-existent resource")
            scenarios.append("Update resource with invalid data")
        elif method_upper == 'DELETE':
            scenarios.append("Delete existing resource")
            scenarios.append("Delete non-existent resource")
            scenarios.append("Delete resource with dependencies")
        
        # Add parameter-specific scenarios
        required_params = [p for p in params if p.get('required', False)]
        if required_params:
            scenarios.append("Test with all required parameters")
        
        optional_params = [p for p in params if not p.get('required', False)]
        if optional_params:
            scenarios.append("Test with optional parameters")
        
        return scenarios
    
    def _generate_brd_with_llm(
        self,
        test_plan: Dict[str, Any],
        processed_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Optional[str]:
        """Use LLM to generate structured BRD JSON."""
        # Use endpoints from test_plan (already filtered by coverage)
        filtered_analysis = {
            **analysis_data,
            'endpoints': [ep for ep in analysis_data.get('endpoints', [])
                         if any(ep.get('path') == ea.get('path') and ep.get('method') == ea.get('method')
                                for ea in test_plan.get('endpoint_analysis', []))]
        }
        prompt = self._create_brd_generation_prompt(test_plan, processed_data, filtered_analysis)
        
        response = self.llm_prompter.send_prompt(prompt)
        
        if not response:
            return None
        
        # Try to extract JSON from response
        return extract_json_from_response(response)
    
    def _create_brd_generation_prompt(
        self,
        test_plan: Dict[str, Any],
        processed_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> str:
        """Create prompt for LLM to generate BRD."""
        api_info = processed_data.get('info', {})
        endpoint_summary = self._build_endpoint_summary(test_plan)
        instructions = self._build_brd_instructions()
        example_structure = self._build_brd_example_structure(api_info)
        
        prompt = f"""You are an expert in API testing and business requirement documentation.

Given the following API information and test plan heuristic, generate a comprehensive Business Requirement Document (BRD) in JSON format.

API Information:
- Name: {api_info.get('title', 'Unknown')}
- Version: {api_info.get('version', 'Unknown')}

Selected Endpoints to analyze ({test_plan.get('coverage_percentage', 100)}% coverage):
{chr(10).join(endpoint_summary) if endpoint_summary else 'No endpoints selected'}

Note: This BRD covers {test_plan.get('selected_endpoints', 0)} out of {test_plan.get('total_endpoints', 0)} total endpoints.

Test Plan Heuristic:
{json.dumps(test_plan, indent=2)}

{instructions}

OUTPUT FORMAT:
Return ONLY valid JSON in this exact structure:
{example_structure}

Generate the complete BRD JSON now:
"""
        return prompt
    
    def _build_endpoint_summary(self, test_plan: Dict[str, Any]) -> List[str]:
        """Build a compact summary of selected endpoints."""
        endpoint_analysis = test_plan.get('endpoint_analysis', [])
        endpoint_summary = []
        for endpoint_info in endpoint_analysis:
            path = endpoint_info.get('path', '')
            method = endpoint_info.get('method', '')
            params_count = endpoint_info.get('parameter_count', 0)
            endpoint_summary.append(f"- {method} {path} ({params_count} parameters)")
        return endpoint_summary
    
    def _build_brd_instructions(self) -> str:
        """Build the instructions section for BRD generation prompt."""
        return """INSTRUCTIONS:
1. Create a BRD schema with requirements for each endpoint
2. Each requirement should have:
   - requirement_id: unique identifier (e.g., "REQ-001")
   - title: descriptive title
   - description: detailed description of what needs to be tested
   - endpoint_path: the API endpoint path
   - endpoint_method: HTTP method (GET, POST, PUT, DELETE, etc.)
   - priority: "critical", "high", "medium", or "low"
   - test_scenarios: list of test scenarios with:
     - scenario_id: unique identifier (e.g., "SCEN-001")
     - scenario_name: descriptive name
     - description: what the scenario tests
     - test_steps: list of steps (Given/When/Then format)
     - expected_result: expected outcome
     - priority: "critical", "high", "medium", or "low"
   - acceptance_criteria: list of acceptance criteria

3. Focus on realistic business requirements and test scenarios
4. Include positive, negative, and edge case scenarios
5. Prioritize based on business impact"""
    
    def _build_brd_example_structure(self, api_info: Dict[str, Any]) -> str:
        """Build the example JSON structure for BRD generation prompt."""
        return f"""{{
  "brd_id": "BRD-001",
  "title": "API Test Requirements Document",
  "description": "Business requirements for testing the API",
  "api_name": "{api_info.get('title', 'Unknown')}",
  "api_version": "{api_info.get('version', 'Unknown')}",
  "created_date": "{datetime.now().isoformat()}",
  "requirements": [
    {{
      "requirement_id": "REQ-001",
      "title": "Test User Retrieval",
      "description": "Test the ability to retrieve user information",
      "endpoint_path": "/users/{{id}}",
      "endpoint_method": "GET",
      "priority": "high",
      "status": "pending",
      "test_scenarios": [
        {{
          "scenario_id": "SCEN-001",
          "scenario_name": "Retrieve valid user",
          "description": "Test retrieving a user with valid ID",
          "test_steps": [
            "Given I have a valid user ID",
            "When I send a GET request to /users/{{id}}",
            "Then I should receive a 200 OK response with user data"
          ],
          "expected_result": "User data is returned successfully",
          "priority": "high",
          "tags": ["positive", "smoke"]
        }}
      ],
      "acceptance_criteria": [
        "API returns user data for valid IDs",
        "API handles invalid IDs gracefully"
      ],
      "related_endpoints": []
    }}
  ],
  "metadata": {{}}
}}"""
    
    
    def _parse_llm_brd_response(
        self,
        brd_json: str,
        processed_data: Dict[str, Any]
    ) -> Optional[BRDSchema]:
        """Parse LLM-generated JSON into BRDSchema object."""
        try:
            data = json.loads(brd_json)
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing BRD JSON: {e}")
            print(f"   Response preview: {brd_json[:200]}...")
            print(f"   Tip: The LLM response may not be valid JSON. "
                  f"Check the analytics report for the raw response.")
            return None
        
        # Parse requirements
        requirements = []
        for req_data in data.get('requirements', []):
            test_scenarios = []
            for scenario_data in req_data.get('test_scenarios', []):
                scenario = BRDTestScenario(
                    scenario_id=scenario_data.get('scenario_id', ''),
                    scenario_name=scenario_data.get('scenario_name', ''),
                    description=scenario_data.get('description', ''),
                    test_steps=scenario_data.get('test_steps', []),
                    expected_result=scenario_data.get('expected_result', ''),
                    priority=RequirementPriority(req_data.get('priority', 'medium')),
                    tags=scenario_data.get('tags', [])
                )
                test_scenarios.append(scenario)
            
            requirement = BRDRequirement(
                requirement_id=req_data.get('requirement_id', ''),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                endpoint_path=req_data.get('endpoint_path', ''),
                endpoint_method=req_data.get('endpoint_method', ''),
                priority=RequirementPriority(req_data.get('priority', 'medium')),
                status=RequirementStatus(req_data.get('status', 'pending')),
                test_scenarios=test_scenarios,
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                related_endpoints=req_data.get('related_endpoints', [])
            )
            requirements.append(requirement)
        
        brd = BRDSchema(
            brd_id=data.get('brd_id', 'BRD-001'),
            title=data.get('title', 'API Test Requirements'),
            description=data.get('description', ''),
            api_name=data.get('api_name', processed_data.get('info', {}).get('title', 'Unknown')),
            api_version=data.get('api_version', processed_data.get('info', {}).get('version', 'Unknown')),
            created_date=data.get('created_date', datetime.now().isoformat()),
            requirements=requirements,
            metadata=data.get('metadata', {})
        )
        
        return brd

