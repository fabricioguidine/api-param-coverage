"""
Tests for the BRD Generator module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import shutil

from src.modules.brd_generator.brd_generator import BRDGenerator
from src.modules.brd.brd_schema import BRDSchema, BRDRequirement, BRDTestScenario, RequirementPriority, RequirementStatus


class TestBRDGenerator:
    """Test cases for BRDGenerator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create a BRDGenerator instance with mocked LLM."""
        with patch('src.modules.brd_generator.brd_generator.LLMPrompter'):
            gen = BRDGenerator(api_key="test-key", model="gpt-4", analytics_dir=temp_dir)
            gen.llm_prompter = MagicMock()
            return gen
    
    @pytest.fixture
    def sample_processed_data(self):
        """Sample processed schema data."""
        return {
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths_count": 5,
            "version": "3.0.0",
            "endpoints": [
                {"path": "/users", "method": "GET"},
                {"path": "/users", "method": "POST"},
                {"path": "/users/{id}", "method": "GET"},
                {"path": "/users/{id}", "method": "PUT"},
                {"path": "/users/{id}", "method": "DELETE"}
            ],
            "components": {
                "schemas_count": 2,
                "responses_count": 5,
                "parameters_count": 10,
                "security_schemes_count": 1
            },
            "tags": ["users"]
        }
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data."""
        return {
            "endpoints": [
                {"path": "/users", "method": "GET", "parameters": []},
                {"path": "/users", "method": "POST", "parameters": [{"name": "name", "required": True}]},
                {"path": "/users/{id}", "method": "GET", "parameters": [{"name": "id", "required": True}]},
                {"path": "/users/{id}", "method": "PUT", "parameters": [{"name": "id", "required": True}, {"name": "name", "required": False}]},
                {"path": "/users/{id}", "method": "DELETE", "parameters": [{"name": "id", "required": True}]}
            ]
        }
    
    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response with BRD JSON."""
        return json.dumps({
            "brd_id": "BRD-001",
            "title": "Test API BRD",
            "description": "Test BRD description",
            "api_name": "Test API",
            "api_version": "1.0.0",
            "created_date": "2024-01-01T00:00:00",
            "requirements": [
                {
                    "requirement_id": "REQ-001",
                    "title": "Test User Retrieval",
                    "description": "Test retrieving users",
                    "endpoint_path": "/users",
                    "endpoint_method": "GET",
                    "priority": "high",
                    "status": "pending",
                    "test_scenarios": [
                        {
                            "scenario_id": "SCEN-001",
                            "scenario_name": "Retrieve users successfully",
                            "description": "Test retrieving all users",
                            "test_steps": [
                                "Given I have access to the API",
                                "When I send a GET request to /users",
                                "Then I should receive a 200 OK response"
                            ],
                            "expected_result": "List of users is returned",
                            "priority": "high",
                            "tags": ["positive", "smoke"]
                        }
                    ],
                    "acceptance_criteria": ["API returns user list"],
                    "related_endpoints": []
                }
            ],
            "metadata": {}
        })
    
    def test_generator_initialization(self, temp_dir):
        """Test BRDGenerator initialization."""
        with patch('src.modules.brd_generator.brd_generator.LLMPrompter'):
            gen = BRDGenerator(api_key="test-key", model="gpt-4", analytics_dir=temp_dir)
            assert gen.api_key == "test-key"
            assert gen.model == "gpt-4"
            assert gen.llm_prompter is not None
    
    def test_generator_initialization_no_api_key(self, temp_dir):
        """Test BRDGenerator initialization without API key."""
        gen = BRDGenerator(api_key=None, analytics_dir=temp_dir)
        assert gen.api_key is None
        assert gen.llm_prompter is None
    
    def test_select_endpoints_by_coverage_exact_percentage(self, generator):
        """Test endpoint selection with exact coverage percentage."""
        endpoints = [
            {"path": "/ep1", "method": "GET"},
            {"path": "/ep2", "method": "POST"},
            {"path": "/ep3", "method": "PUT"},
            {"path": "/ep4", "method": "DELETE"},
            {"path": "/ep5", "method": "GET"}
        ]
        
        selected = generator._select_endpoints_by_coverage(endpoints, 60.0)
        # 60% of 5 = 3 endpoints
        # Should prioritize POST, PUT, DELETE (3 critical) = 3 total
        assert len(selected) == 3
        assert all(e.get('method') in ['POST', 'PUT', 'DELETE'] for e in selected)
    
    def test_select_endpoints_by_coverage_random(self, generator):
        """Test endpoint selection with random coverage (None)."""
        endpoints = [
            {"path": "/ep1", "method": "GET"},
            {"path": "/ep2", "method": "POST"},
            {"path": "/ep3", "method": "GET"}
        ]
        
        selected = generator._select_endpoints_by_coverage(endpoints, None)
        # Random coverage should select 50-80% of endpoints
        # With 3 endpoints, should select at least 1 (50% = 1.5, rounded down to 1)
        assert len(selected) >= 1
        assert len(selected) <= 3
    
    def test_select_endpoints_by_coverage_empty_list(self, generator):
        """Test endpoint selection with empty list."""
        selected = generator._select_endpoints_by_coverage([], 50.0)
        assert selected == []
    
    def test_select_endpoints_by_coverage_prioritizes_critical(self, generator):
        """Test that critical endpoints are prioritized."""
        endpoints = [
            {"path": "/ep1", "method": "GET"},
            {"path": "/ep2", "method": "GET"},
            {"path": "/ep3", "method": "POST"},  # Critical
            {"path": "/ep4", "method": "PUT"},   # Critical
            {"path": "/ep5", "method": "GET"}
        ]
        
        selected = generator._select_endpoints_by_coverage(endpoints, 40.0)
        # 40% of 5 = 2 endpoints
        # Should select POST and PUT (critical) first
        assert len(selected) == 2
        selected_methods = {e.get('method') for e in selected}
        assert 'POST' in selected_methods or 'PUT' in selected_methods
    
    def test_determine_priority_heuristic_critical_methods(self, generator):
        """Test priority determination for critical HTTP methods."""
        assert generator._determine_priority_heuristic("POST", []) == "high"
        assert generator._determine_priority_heuristic("PUT", []) == "high"
        assert generator._determine_priority_heuristic("DELETE", []) == "high"
    
    def test_determine_priority_heuristic_get_simple(self, generator):
        """Test priority determination for simple GET requests."""
        assert generator._determine_priority_heuristic("GET", []) == "medium"
        assert generator._determine_priority_heuristic("GET", [{"name": "param1"}]) == "medium"
    
    def test_determine_priority_heuristic_get_complex(self, generator):
        """Test priority determination for complex GET requests."""
        complex_params = [{"name": f"param{i}"} for i in range(6)]
        assert generator._determine_priority_heuristic("GET", complex_params) == "high"
    
    def test_suggest_test_scenarios_get(self, generator):
        """Test test scenario suggestions for GET method."""
        scenarios = generator._suggest_test_scenarios("GET", [])
        assert "Valid request with correct parameters" in scenarios
        assert "Request with missing required parameters" in scenarios
        assert "Request with invalid parameter values" in scenarios
    
    def test_suggest_test_scenarios_post(self, generator):
        """Test test scenario suggestions for POST method."""
        scenarios = generator._suggest_test_scenarios("POST", [])
        assert "Create resource with valid data" in scenarios
        assert "Create resource with missing required fields" in scenarios
        assert "Create resource with invalid data format" in scenarios
    
    def test_suggest_test_scenarios_put(self, generator):
        """Test test scenario suggestions for PUT method."""
        scenarios = generator._suggest_test_scenarios("PUT", [])
        assert "Update resource with valid data" in scenarios
        assert "Update non-existent resource" in scenarios
    
    def test_suggest_test_scenarios_delete(self, generator):
        """Test test scenario suggestions for DELETE method."""
        scenarios = generator._suggest_test_scenarios("DELETE", [])
        assert "Delete existing resource" in scenarios
        assert "Delete non-existent resource" in scenarios
    
    def test_suggest_test_scenarios_with_required_params(self, generator):
        """Test test scenario suggestions with required parameters."""
        params = [{"name": "id", "required": True}]
        scenarios = generator._suggest_test_scenarios("GET", params)
        assert "Test with all required parameters" in scenarios
    
    def test_suggest_test_scenarios_with_optional_params(self, generator):
        """Test test scenario suggestions with optional parameters."""
        params = [{"name": "filter", "required": False}]
        scenarios = generator._suggest_test_scenarios("GET", params)
        assert "Test with optional parameters" in scenarios
    
    def test_create_test_plan_heuristic(self, generator, sample_processed_data, sample_analysis_data):
        """Test test plan heuristic creation."""
        test_plan = generator._create_test_plan_heuristic(
            sample_processed_data,
            sample_analysis_data,
            coverage_percentage=60.0
        )
        
        assert test_plan["api_name"] == "Test API"
        assert test_plan["api_version"] == "1.0.0"
        assert test_plan["total_endpoints"] == 5
        assert test_plan["coverage_percentage"] == 60.0
        assert len(test_plan["endpoint_analysis"]) > 0
        
        for analysis in test_plan["endpoint_analysis"]:
            assert "path" in analysis
            assert "method" in analysis
            assert "suggested_priority" in analysis
            assert "suggested_scenarios" in analysis
    
    def test_extract_json_from_response_code_block(self, generator, sample_llm_response):
        """Test JSON extraction from markdown code block."""
        from src.modules.utils import extract_json_from_response
        wrapped_response = f"```json\n{sample_llm_response}\n```"
        extracted = extract_json_from_response(wrapped_response)
        assert extracted is not None
        data = json.loads(extracted)
        assert data["brd_id"] == "BRD-001"
    
    def test_extract_json_from_response_direct(self, generator, sample_llm_response):
        """Test JSON extraction from direct JSON response."""
        from src.modules.utils import extract_json_from_response
        extracted = extract_json_from_response(sample_llm_response)
        assert extracted is not None
        data = json.loads(extracted)
        assert data["brd_id"] == "BRD-001"
    
    def test_parse_llm_brd_response_success(self, generator, sample_processed_data, sample_llm_response):
        """Test parsing LLM BRD response into BRDSchema."""
        brd = generator._parse_llm_brd_response(sample_llm_response, sample_processed_data)
        
        assert brd is not None
        assert isinstance(brd, BRDSchema)
        assert brd.brd_id == "BRD-001"
        assert brd.title == "Test API BRD"
        assert len(brd.requirements) == 1
        
        req = brd.requirements[0]
        assert req.requirement_id == "REQ-001"
        assert len(req.test_scenarios) == 1
        assert req.test_scenarios[0].scenario_id == "SCEN-001"
    
    def test_parse_llm_brd_response_invalid_json(self, generator, sample_processed_data):
        """Test parsing invalid JSON response."""
        invalid_json = "This is not valid JSON {"
        brd = generator._parse_llm_brd_response(invalid_json, sample_processed_data)
        assert brd is None
    
    def test_generate_brd_from_swagger_success(
        self,
        generator,
        sample_processed_data,
        sample_analysis_data,
        sample_llm_response,
        temp_dir
    ):
        """Test successful BRD generation from Swagger."""
        import time as time_module
        
        # Mock time.time to return sequential values
        time_values = [1000.0, 1001.5]
        time_index = [0]
        
        def mock_time():
            result = time_values[time_index[0]]
            time_index[0] = min(time_index[0] + 1, len(time_values) - 1)
            return result
        
        with patch('src.modules.brd_generator.brd_generator.time.time', side_effect=mock_time):
            generator.llm_prompter.send_prompt.return_value = sample_llm_response
            
            brd = generator.generate_brd_from_swagger(
                sample_processed_data,
                sample_analysis_data,
                "test_schema.json",
                coverage_percentage=60.0
            )
            
            assert brd is not None
            assert isinstance(brd, BRDSchema)
            generator.llm_prompter.send_prompt.assert_called_once()
    
    def test_generate_brd_from_swagger_no_api_key(self, temp_dir, sample_processed_data, sample_analysis_data):
        """Test BRD generation without API key."""
        gen = BRDGenerator(api_key=None, analytics_dir=temp_dir)
        brd = gen.generate_brd_from_swagger(
            sample_processed_data,
            sample_analysis_data,
            "test_schema.json"
        )
        assert brd is None
    
    def test_generate_brd_from_swagger_llm_failure(
        self,
        generator,
        sample_processed_data,
        sample_analysis_data
    ):
        """Test BRD generation when LLM call fails."""
        generator.llm_prompter.send_prompt.return_value = None
        
        brd = generator.generate_brd_from_swagger(
            sample_processed_data,
            sample_analysis_data,
            "test_schema.json"
        )
        
        assert brd is None
    
    def test_generate_brd_from_swagger_with_coverage_percentage(
        self,
        generator,
        sample_processed_data,
        sample_analysis_data,
        sample_llm_response
    ):
        """Test BRD generation with specific coverage percentage."""
        import time as time_module
        
        # Mock time.time to return sequential values
        time_values = [1000.0, 1001.5]
        time_index = [0]
        
        def mock_time():
            result = time_values[time_index[0]]
            time_index[0] = min(time_index[0] + 1, len(time_values) - 1)
            return result
        
        with patch('src.modules.brd_generator.brd_generator.time.time', side_effect=mock_time):
            generator.llm_prompter.send_prompt.return_value = sample_llm_response
            
            with patch.object(generator, '_create_test_plan_heuristic') as mock_heuristic:
                mock_heuristic.return_value = {
                    "api_name": "Test API",
                    "api_version": "1.0.0",
                    "total_endpoints": 5,
                    "selected_endpoints": 3,
                    "coverage_percentage": 60.0,
                    "endpoint_analysis": []
                }
                
                brd = generator.generate_brd_from_swagger(
                    sample_processed_data,
                    sample_analysis_data,
                    "test_schema.json",
                    coverage_percentage=60.0
                )
                
                # Verify coverage percentage was passed to heuristic
                mock_heuristic.assert_called_once()
                call_args = mock_heuristic.call_args
                # Check positional arguments: processed_data, analysis_data, coverage_percentage
                assert len(call_args[0]) == 3
                assert call_args[0][0] == sample_processed_data
                assert call_args[0][1] == sample_analysis_data
                assert call_args[0][2] == 60.0  # coverage_percentage parameter
                assert brd is not None
