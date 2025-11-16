"""
Tests for the SchemaFetcher module.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import yaml
import requests

from src.modules.swagger_tool.schema_fetcher import SchemaFetcher


class TestSchemaFetcher:
    """Test cases for SchemaFetcher class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def fetcher(self, temp_dir):
        """Create a SchemaFetcher instance with temporary directory."""
        return SchemaFetcher(schemas_dir=temp_dir)
    
    @pytest.fixture
    def sample_schema(self):
        """Sample Swagger schema for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {}
        }
    
    def test_init_creates_directory(self, temp_dir):
        """Test that __init__ creates the schemas directory."""
        new_dir = Path(temp_dir) / "new_schemas"
        fetcher = SchemaFetcher(schemas_dir=str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('src.modules.swagger_tool.schema_fetcher.SchemaValidator')
    @patch('builtins.print')
    def test_fetch_schema_json_success(self, mock_print, mock_validator_class, mock_get, fetcher, sample_schema):
        """Test successful fetching of JSON schema."""
        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_schema.return_value = (True, None)
        mock_validator.normalize_schema.return_value = sample_schema
        mock_validator.get_schema_info.return_value = {
            'type': 'openapi',
            'version': '3.0.0',
            'title': 'Test API'
        }
        mock_validator_class.return_value = mock_validator
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = sample_schema
        mock_response.text = json.dumps(sample_schema)
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetcher.fetch_schema("https://example.com/api/swagger.json")
        
        assert result == sample_schema
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://example.com/api/swagger.json" in str(call_args)
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('src.modules.swagger_tool.schema_fetcher.SchemaValidator')
    @patch('builtins.print')
    def test_fetch_schema_yaml_success(self, mock_print, mock_validator_class, mock_get, fetcher, sample_schema):
        """Test successful fetching of YAML schema."""
        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_schema.return_value = (True, None)
        mock_validator.normalize_schema.return_value = sample_schema
        mock_validator.get_schema_info.return_value = {
            'type': 'openapi',
            'version': '3.0.0',
            'title': 'Test API'
        }
        mock_validator_class.return_value = mock_validator
        
        # Mock HTTP response
        mock_response = Mock()
        # Create a proper JSONDecodeError
        json_error = json.JSONDecodeError("Not JSON", "", 0)
        mock_response.json.side_effect = json_error
        mock_response.text = yaml.dump(sample_schema)
        mock_response.headers = {'Content-Type': 'application/yaml'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetcher.fetch_schema("https://example.com/api/swagger.yaml")
        
        assert result == sample_schema
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('builtins.print')
    def test_fetch_schema_request_exception(self, mock_print, mock_get, fetcher):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = fetcher.fetch_schema("https://example.com/api/swagger.json")
        
        assert result is None
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('builtins.print')
    def test_fetch_schema_invalid_format(self, mock_print, mock_get, fetcher):
        """Test handling of invalid schema format."""
        mock_response = Mock()
        # Create a proper JSONDecodeError
        json_error = json.JSONDecodeError("Not JSON", "", 0)
        mock_response.json.side_effect = json_error
        mock_response.text = "invalid content that is not yaml either"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetcher.fetch_schema("https://example.com/api/swagger.txt")
        
        assert result is None
    
    def test_save_schema_json(self, fetcher, sample_schema, temp_dir):
        """Test saving schema as JSON."""
        url = "https://example.com/api/swagger.json"
        filepath = fetcher.save_schema(sample_schema, url, "json")
        
        assert filepath is not None
        assert Path(filepath).exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == sample_schema
        
        # Verify filename
        assert "example_com" in filepath
        assert filepath.endswith(".json")
    
    def test_save_schema_yaml(self, fetcher, sample_schema, temp_dir):
        """Test saving schema as YAML."""
        url = "https://example.com/api/swagger.yaml"
        filepath = fetcher.save_schema(sample_schema, url, "yaml")
        
        assert filepath is not None
        assert Path(filepath).exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            loaded = yaml.safe_load(f)
        assert loaded == sample_schema
        
        # Verify filename
        assert filepath.endswith(".yaml")
    
    def test_save_schema_filename_generation(self, fetcher, sample_schema, temp_dir):
        """Test filename generation from URL."""
        url = "https://api.example.com/v1/swagger"
        filepath = fetcher.save_schema(sample_schema, url, "json")
        
        assert "api_example_com" in filepath
        assert "v1_swagger" in filepath
    
    def test_save_schema_with_path(self, fetcher, sample_schema, temp_dir):
        """Test saving schema with URL path."""
        url = "https://example.com/docs/api/swagger.json"
        filepath = fetcher.save_schema(sample_schema, url, "json")
        
        assert "example_com" in filepath
        assert "docs_api_swagger" in filepath
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('builtins.print')
    def test_download_and_save_success(self, mock_print, mock_get, fetcher, sample_schema, temp_dir):
        """Test complete download and save workflow."""
        mock_response = Mock()
        mock_response.json.return_value = sample_schema
        mock_response.text = json.dumps(sample_schema)
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        url = "https://example.com/api/swagger.json"
        filepath = fetcher.download_and_save(url, "json")
        
        assert filepath is not None
        assert Path(filepath).exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == sample_schema
    
    @patch('src.modules.swagger_tool.schema_fetcher.requests.get')
    @patch('builtins.print')
    def test_download_and_save_fetch_failure(self, mock_print, mock_get, fetcher):
        """Test download_and_save when fetch fails."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        url = "https://example.com/api/swagger.json"
        filepath = fetcher.download_and_save(url, "json")
        
        assert filepath is None

