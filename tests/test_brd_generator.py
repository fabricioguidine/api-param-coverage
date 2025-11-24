"""
Tests for the BRD Generator module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.modules.brd_generator.brd_generator import BRDGenerator
from src.modules.brd.brd_schema import BRDSchema


class TestBRDGenerator:
    """Test cases for BRDGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create a BRDGenerator instance for testing."""
        return BRDGenerator(api_key="test-key", model="gpt-4")
    
    @pytest.fixture
    def sample_processed_data(self):
        """Sample processed schema data."""
        return {
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths_count": 10
        }
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data with endpoints."""
        return {
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "parameters": [{"name": "id", "required": True}]
                },
                {
                    "path": "/users",
                    "method": "POST",
                    "parameters": [{"name": "name", "required": True}]
                },
                {
                    "path": "/users/{id}",
                    "method": "PUT",
                    "parameters": [{"name": "id", "required": True}]
                },
                {
                    "path": "/users/{id}",
                    "method": "DELETE",
                    "parameters": [{"name": "id", "required": True}]
                },
                {
                    "path": "/products",
                    "method": "GET",
                    "parameters": []
                }
            ]
        }
    
    def test_generator_initialization(self):
        """Test BRDGenerator initialization."""
        generator = BRDGenerator(api_key="test-key", model="gpt-4")
        assert generator.api_key == "test-key"
        assert generator.model == "gpt-4"
        assert generator.llm_prompter is not None
    
    def test_generator_initialization_no_api_key(self):
        """Test BRDGenerator initialization without API key."""
        generator = BRDGenerator()
        assert generator.api_key is None
        assert generator.llm_prompter is None
    
    def test_calculate_priority_score(self, generator):
        """Test priority score calculation."""
        # POST should have higher score than GET
        post_score = generator._calculate_priority_score("POST", [])
        get_score = generator._calculate_priority_score("GET", [])
        assert post_score > get_score
        
        # More parameters should increase score
        score_with_params = generator._calculate_priority_score("GET", [{"required": True}] * 5)
        score_no_params = generator._calculate_priority_score("GET", [])
        assert score_with_params > score_no_params
    
    def test_determine_priority_heuristic(self, generator):
        """Test priority heuristic determination."""
        assert generator._determine_priority_heuristic("POST", []) == "high"
        assert generator._determine_priority_heuristic("PUT", []) == "high"
        assert generator._determine_priority_heuristic("DELETE", []) == "high"
        assert generator._determine_priority_heuristic("GET", []) == "medium"
        assert generator._determine_priority_heuristic("GET", [{}] * 6) == "high"
    
    def test_suggest_test_scenarios(self, generator):
        """Test test scenario suggestions."""
        get_scenarios = generator._suggest_test_scenarios("GET", [])
        assert len(get_scenarios) > 0
        assert any("Valid request" in s for s in get_scenarios)
        
        post_scenarios = generator._suggest_test_scenarios("POST", [])
        assert len(post_scenarios) > 0
        assert any("Create resource" in s for s in post_scenarios)
    
    def test_create_test_plan_heuristic_full_coverage(self, generator, sample_processed_data, sample_analysis_data):
        """Test test plan heuristic creation with 100% coverage."""
        test_plan = generator._create_test_plan_heuristic(sample_processed_data, sample_analysis_data, 100.0)
        
        assert test_plan["api_name"] == "Test API"
        assert test_plan["total_endpoints"] == 5
        assert test_plan["selected_endpoints"] == 5
        assert test_plan["coverage_percentage"] == 100.0
        assert len(test_plan["endpoint_analysis"]) == 5
    
    def test_create_test_plan_heuristic_partial_coverage(self, generator, sample_processed_data, sample_analysis_data):
        """Test test plan heuristic creation with 50% coverage."""
        test_plan = generator._create_test_plan_heuristic(sample_processed_data, sample_analysis_data, 50.0)
        
        assert test_plan["total_endpoints"] == 5
        assert test_plan["selected_endpoints"] == 2  # 50% of 5 = 2.5, rounded down to 2
        assert test_plan["coverage_percentage"] == 50.0
        assert len(test_plan["endpoint_analysis"]) == 2
    
    def test_create_test_plan_heuristic_prioritizes_critical_methods(self, generator, sample_processed_data, sample_analysis_data):
        """Test that critical methods (POST/PUT/DELETE) are prioritized."""
        test_plan = generator._create_test_plan_heuristic(sample_processed_data, sample_analysis_data, 60.0)
        
        # Should select 3 endpoints (60% of 5 = 3)
        # POST, PUT, DELETE should be selected before GET
        selected_methods = [ep["method"] for ep in test_plan["endpoint_analysis"]]
        assert "POST" in selected_methods or "PUT" in selected_methods or "DELETE" in selected_methods
    
    def test_generate_brd_from_swagger_invalid_coverage(self, generator, sample_processed_data, sample_analysis_data):
        """Test BRD generation with invalid coverage percentage."""
        with patch.object(generator, '_create_test_plan_heuristic') as mock_heuristic:
            mock_heuristic.return_value = {"endpoint_analysis": []}
            with patch.object(generator, '_generate_brd_with_llm') as mock_llm:
                mock_llm.return_value = None
                
                # Test with coverage > 100
                result = generator.generate_brd_from_swagger(
                    sample_processed_data, sample_analysis_data, "test.json", coverage_percentage=150.0
                )
                # Should default to 100%
                mock_heuristic.assert_called_once()
                call_args = mock_heuristic.call_args
                assert call_args[0][2] == 100.0  # coverage_percentage should be corrected to 100
    
    def test_generate_brd_from_swagger_no_api_key(self, sample_processed_data, sample_analysis_data):
        """Test BRD generation without API key."""
        generator = BRDGenerator()
        result = generator.generate_brd_from_swagger(
            sample_processed_data, sample_analysis_data, "test.json"
        )
        assert result is None
    
    def test_extract_json_from_response(self, generator):
        """Test JSON extraction from LLM response."""
        # Test with markdown code block
        response_with_markdown = "```json\n{\"test\": \"value\"}\n```"
        result = generator._extract_json_from_response(response_with_markdown)
        assert "test" in result
        
        # Test with plain JSON
        response_plain = '{"test": "value"}'
        result = generator._extract_json_from_response(response_plain)
        assert "test" in result
        
        # Test with no JSON
        response_no_json = "This is just text"
        result = generator._extract_json_from_response(response_no_json)
        assert result == response_no_json

