"""
Tests for the LLMPrompter module.
"""

import pytest
from unittest.mock import Mock, patch
from src.modules.engine.llm.prompter import LLMPrompter


class TestLLMPrompter:
    """Test cases for LLMPrompter class."""
    
    @pytest.fixture
    def prompter(self):
        """Create an LLMPrompter instance."""
        return LLMPrompter(model="gpt-4", api_key="test-key")
    
    @pytest.fixture
    def processed_data(self):
        """Sample processed data."""
        return {
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "version": "3.0.0",
            "paths_count": 2,
            "endpoints": [
                {"method": "GET", "path": "/test", "summary": "Test endpoint"}
            ],
            "components": {
                "schemas": {},
                "responses": {},
                "parameters": {},
                "securitySchemes": {}
            },
            "tags": ["test"]
        }
    
    @pytest.fixture
    def analysis_data(self):
        """Sample analysis data."""
        return {
            "endpoints": [
                {
                    "path": "/test",
                    "method": "GET",
                    "parameters": [
                        {
                            "location": "query",
                            "name": "id",
                            "type": "string",
                            "required": True
                        }
                    ]
                }
            ]
        }
    
    def test_create_prompt_empty_processed_data(self, prompter):
        """Test that empty processed_data raises ValueError."""
        with pytest.raises(ValueError, match="processed_data cannot be empty"):
            prompter.create_prompt({}, "analyze")
    
    def test_create_prompt_none_processed_data(self, prompter):
        """Test that None processed_data raises ValueError."""
        with pytest.raises(ValueError, match="processed_data cannot be empty"):
            prompter.create_prompt(None, "analyze")
    
    def test_create_prompt_invalid_processed_data_type(self, prompter):
        """Test that non-dict processed_data raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            prompter.create_prompt("not a dict", "analyze")
    
    def test_create_prompt_gherkin_missing_analysis_data(self, prompter, processed_data):
        """Test that gherkin task without analysis_data raises ValueError."""
        with pytest.raises(ValueError, match="analysis_data is required"):
            prompter.create_prompt(processed_data, "gherkin", None)
    
    def test_create_prompt_gherkin_empty_endpoints(self, prompter, processed_data):
        """Test that gherkin task with empty endpoints raises ValueError."""
        with pytest.raises(ValueError, match="contains no endpoints"):
            prompter.create_prompt(processed_data, "gherkin", {"endpoints": []})
    
    def test_create_prompt_success(self, prompter, processed_data):
        """Test successful prompt creation."""
        prompt = prompter.create_prompt(processed_data, "analyze")
        assert prompt is not None
        assert len(prompt) > 50
        assert "Test API" in prompt
    
    def test_create_prompt_gherkin_success(self, prompter, processed_data, analysis_data):
        """Test successful Gherkin prompt creation."""
        prompt = prompter.create_prompt(processed_data, "gherkin", analysis_data)
        assert prompt is not None
        assert len(prompt) > 50
        assert "Test API" in prompt
    
    def test_send_prompt_empty_string(self, prompter):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            prompter.send_prompt("")
    
    def test_send_prompt_none(self, prompter):
        """Test that None prompt raises ValueError."""
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            prompter.send_prompt(None)
    
    def test_send_prompt_whitespace_only(self, prompter):
        """Test that whitespace-only prompt raises ValueError."""
        with pytest.raises(ValueError, match="whitespace only"):
            prompter.send_prompt("   \n\t  ")
    
    def test_send_prompt_too_short(self, prompter):
        """Test that too short prompt raises ValueError."""
        with pytest.raises(ValueError, match="too short"):
            prompter.send_prompt("short")
    
    @patch('openai.OpenAI')
    def test_send_prompt_success(self, mock_openai_class, prompter):
        """Test successful prompt sending."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Feature: Test\n  Scenario: Test scenario\n  Given I have access to the API\n  When I send a request\n  Then I should receive a response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Ensure prompter has an API key
        prompter.api_key = "test-api-key"
        
        result = prompter.send_prompt("Generate Gherkin scenarios for this API")
        
        assert result is not None
        assert "Feature" in result
    
    def test_generate_gherkin_empty_processed_data(self, prompter, analysis_data):
        """Test that empty processed_data raises ValueError."""
        with pytest.raises(ValueError, match="processed_data cannot be empty"):
            prompter.generate_gherkin_scenarios({}, analysis_data)
    
    def test_generate_gherkin_empty_analysis_data(self, prompter, processed_data):
        """Test that empty analysis_data raises ValueError."""
        with pytest.raises(ValueError, match="analysis_data cannot be empty"):
            prompter.generate_gherkin_scenarios(processed_data, {})
    
    def test_generate_gherkin_no_endpoints(self, prompter, processed_data):
        """Test that analysis_data without endpoints raises ValueError."""
        with pytest.raises(ValueError, match="contains no endpoints"):
            prompter.generate_gherkin_scenarios(processed_data, {"endpoints": []})
    
    def test_optimize_analysis_data_empty(self, prompter):
        """Test that empty analysis_data raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            prompter._optimize_analysis_data({})
    
    def test_optimize_analysis_data_no_endpoints(self, prompter):
        """Test that analysis_data without endpoints raises ValueError."""
        with pytest.raises(ValueError, match="missing 'endpoints' key"):
            prompter._optimize_analysis_data({"other": "data"})
    
    def test_optimize_analysis_data_success(self, prompter, analysis_data):
        """Test successful optimization."""
        optimized = prompter._optimize_analysis_data(analysis_data)
        assert "endpoints" in optimized
        assert len(optimized["endpoints"]) > 0

