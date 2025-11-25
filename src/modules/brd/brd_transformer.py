"""
BRD Transformer

Shared transformation logic for converting various formats to BRD schema.
Reusable across BRDGenerator, BRDParser, and other components.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .brd_schema import (
    BRDSchema, BRDRequirement, BRDTestScenario,
    RequirementPriority, RequirementStatus
)
from ..engine.llm import LLMPrompter
from ..utils import extract_json_from_response
from ..utils.constants import SUPPORTED_BRD_FORMATS


class BRDTransformer:
    """Shared transformer for converting various formats to BRD schema."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", provider: str = "openai"):
        """
        Initialize the BRD Transformer.
        
        Args:
            api_key: LLM API key
            model: LLM model to use
            provider: LLM provider ('openai', 'anthropic', 'google', 'azure')
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.llm_prompter = LLMPrompter(model=model, api_key=api_key, provider=provider) if api_key else None
    
    def transform_to_schema(
        self,
        source_data: Dict[str, Any],
        source_type: str = "swagger",
        api_info: Optional[Dict[str, Any]] = None
    ) -> Optional[BRDSchema]:
        """
        Transform source data to BRD schema.
        
        Args:
            source_data: Source data (Swagger analysis, document content, etc.)
            source_type: Type of source ('swagger', 'document', 'intermediate_brd')
            api_info: Optional API information for context
            
        Returns:
            BRDSchema object, or None if transformation fails
        """
        if source_type == "swagger":
            return self._transform_swagger_to_schema(source_data, api_info)
        elif source_type == "document":
            return self._transform_document_to_schema(source_data)
        elif source_type == "intermediate_brd":
            return self._transform_intermediate_brd_to_schema(source_data)
        else:
            print(f"✗ Error: Unknown source type: {source_type}")
            return None
    
    def _transform_swagger_to_schema(
        self,
        swagger_data: Dict[str, Any],
        api_info: Optional[Dict[str, Any]] = None
    ) -> Optional[BRDSchema]:
        """
        Transform Swagger analysis data to BRD schema.
        This is a two-step process:
        1. Swagger → Intermediate BRD (business requirements)
        2. Intermediate BRD → BRD Schema (structured format)
        """
        if not self.llm_prompter:
            print("✗ Error: LLM API key required for Swagger transformation")
            return None
        
        # Step 1: Transform Swagger to intermediate BRD
        intermediate_brd = self._swagger_to_intermediate_brd(swagger_data, api_info)
        if not intermediate_brd:
            return None
        
        # Step 2: Transform intermediate BRD to schema
        return self._transform_intermediate_brd_to_schema(intermediate_brd)
    
    def _swagger_to_intermediate_brd(
        self,
        swagger_data: Dict[str, Any],
        api_info: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Transform Swagger data to intermediate BRD format."""
        # This creates a business requirements document from Swagger
        # It's less structured than the final schema
        prompt = self._create_swagger_to_brd_prompt(swagger_data, api_info)
        response = self.llm_prompter.send_prompt(prompt)
        
        if not response:
            return None
        
        # Extract JSON from response
        brd_json = extract_json_from_response(response)
        if not brd_json:
            return None
        
        try:
            return json.loads(brd_json)
        except json.JSONDecodeError:
            print("⚠ Warning: Failed to parse intermediate BRD JSON")
            return None
    
    def _transform_intermediate_brd_to_schema(
        self,
        intermediate_brd: Dict[str, Any]
    ) -> Optional[BRDSchema]:
        """Transform intermediate BRD to structured BRD schema."""
        if not self.llm_prompter:
            print("✗ Error: LLM API key required for BRD transformation")
            return None
        
        # Use LLM to convert intermediate BRD to structured schema
        prompt = self._create_brd_to_schema_prompt(intermediate_brd)
        response = self.llm_prompter.send_prompt(prompt)
        
        if not response:
            return None
        
        brd_json = extract_json_from_response(response)
        if not brd_json:
            return None
        
        return self._parse_brd_json_to_schema(brd_json)
    
    def _transform_document_to_schema(
        self,
        document_data: Dict[str, Any]
    ) -> Optional[BRDSchema]:
        """Transform document content to BRD schema."""
        if not self.llm_prompter:
            print("✗ Error: LLM API key required for document transformation")
            return None
        
        # Extract content from document_data
        content = document_data.get('content', '')
        if not content:
            print("✗ Error: No content found in document data")
            return None
        
        # First transform document to intermediate BRD
        intermediate_brd = self._document_to_intermediate_brd(content)
        if not intermediate_brd:
            return None
        
        # Then transform to schema
        return self._transform_intermediate_brd_to_schema(intermediate_brd)
    
    def _document_to_intermediate_brd(
        self,
        document_content: str
    ) -> Optional[Dict[str, Any]]:
        """Transform document content to intermediate BRD."""
        prompt = self._create_document_to_brd_prompt(document_content)
        response = self.llm_prompter.send_prompt(prompt)
        
        if not response:
            return None
        
        brd_json = extract_json_from_response(response)
        if not brd_json:
            return None
        
        try:
            return json.loads(brd_json)
        except json.JSONDecodeError:
            print("⚠ Warning: Failed to parse document BRD JSON")
            return None
    
    def _create_swagger_to_brd_prompt(
        self,
        swagger_data: Dict[str, Any],
        api_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create prompt for Swagger → Intermediate BRD transformation."""
        # Extract test_plan if present (from BRDGenerator)
        test_plan = swagger_data.get('test_plan', {})
        processed_data = swagger_data.get('processed_data', {})
        analysis_data = swagger_data.get('analysis_data', {})
        
        # Use api_info from processed_data if not provided
        if not api_info:
            api_info = processed_data.get('info', {})
        
        # Build endpoint summary from test_plan if available
        endpoint_summary = []
        if test_plan and 'endpoint_analysis' in test_plan:
            for endpoint_info in test_plan['endpoint_analysis']:
                path = endpoint_info.get('path', '')
                method = endpoint_info.get('method', '')
                priority = endpoint_info.get('suggested_priority', 'medium')
                endpoint_summary.append(f"- {method} {path} (priority: {priority})")
        
        return f"""Transform the following Swagger/OpenAPI schema analysis into a Business Requirements Document (BRD).

API Information:
- Name: {api_info.get('title', 'Unknown')}
- Version: {api_info.get('version', 'Unknown')}

Selected Endpoints ({test_plan.get('coverage_percentage', 100)}% coverage):
{chr(10).join(endpoint_summary) if endpoint_summary else 'All endpoints'}

Test Plan Heuristic:
{json.dumps(test_plan, indent=2) if test_plan else 'N/A'}

Create a BRD that captures business requirements for testing this API.
Focus on:
- Endpoint priorities
- Test scenarios needed
- Business-critical operations
- Parameter validation requirements

Return the BRD as JSON with requirements and test scenarios.
"""
    
    def _create_brd_to_schema_prompt(
        self,
        intermediate_brd: Dict[str, Any]
    ) -> str:
        """Create prompt for Intermediate BRD → Schema transformation."""
        return f"""Convert the following Business Requirements Document into a structured BRD schema.

Intermediate BRD:
{json.dumps(intermediate_brd, indent=2)}

Convert it to the following structured format:
{{
  "brd_id": "BRD-001",
  "title": "BRD Title",
  "description": "Description",
  "api_name": "API Name",
  "api_version": "Version",
  "created_date": "{datetime.now().isoformat()}",
  "requirements": [
    {{
      "requirement_id": "REQ-001",
      "title": "Requirement title",
      "description": "Description",
      "endpoint_path": "/path",
      "endpoint_method": "GET",
      "priority": "high",
      "status": "pending",
      "test_scenarios": [...],
      "acceptance_criteria": [...],
      "related_endpoints": []
    }}
  ],
  "metadata": {{}}
}}

Return ONLY valid JSON.
"""
    
    def _create_document_to_brd_prompt(
        self,
        document_content: str
    ) -> str:
        """Create prompt for Document → Intermediate BRD transformation."""
        # Truncate if too long
        max_chars = 15000
        if len(document_content) > max_chars:
            document_content = document_content[:max_chars] + "\n\n[... truncated ...]"
        
        return f"""Extract business requirements from the following document and create a Business Requirements Document (BRD).

Document Content:
{document_content}

Extract:
- API endpoints mentioned
- Test requirements
- Priority levels
- Acceptance criteria
- Test scenarios

Return as JSON with requirements and test scenarios.
"""
    
    def _parse_brd_json_to_schema(self, brd_json: str) -> Optional[BRDSchema]:
        """Parse BRD JSON string into BRDSchema object."""
        try:
            data = json.loads(brd_json)
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing BRD JSON: {e}")
            return None
        
        # Parse requirements
        requirements = []
        for req_data in data.get('requirements', []):
            test_scenarios = []
            for scenario_data in req_data.get('test_scenarios', []):
                try:
                    priority = RequirementPriority(scenario_data.get('priority', 'medium').lower())
                except ValueError:
                    priority = RequirementPriority.MEDIUM
                
                scenario = BRDTestScenario(
                    scenario_id=scenario_data.get('scenario_id', ''),
                    scenario_name=scenario_data.get('scenario_name', ''),
                    description=scenario_data.get('description', ''),
                    test_steps=scenario_data.get('test_steps', []),
                    expected_result=scenario_data.get('expected_result', ''),
                    priority=priority,
                    tags=scenario_data.get('tags', [])
                )
                test_scenarios.append(scenario)
            
            try:
                req_priority = RequirementPriority(req_data.get('priority', 'medium').lower())
            except ValueError:
                req_priority = RequirementPriority.MEDIUM
            
            try:
                req_status = RequirementStatus(req_data.get('status', 'pending').lower())
            except ValueError:
                req_status = RequirementStatus.PENDING
            
            requirement = BRDRequirement(
                requirement_id=req_data.get('requirement_id', ''),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                endpoint_path=req_data.get('endpoint_path', ''),
                endpoint_method=req_data.get('endpoint_method', ''),
                priority=req_priority,
                status=req_status,
                test_scenarios=test_scenarios,
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                related_endpoints=req_data.get('related_endpoints', [])
            )
            requirements.append(requirement)
        
        brd = BRDSchema(
            brd_id=data.get('brd_id', 'BRD-001'),
            title=data.get('title', 'BRD Document'),
            description=data.get('description', ''),
            api_name=data.get('api_name', 'Unknown'),
            api_version=data.get('api_version', ''),
            created_date=data.get('created_date', datetime.now().isoformat()),
            requirements=requirements,
            metadata=data.get('metadata', {})
        )
        
        return brd

