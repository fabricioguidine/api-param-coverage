"""
Tests for the SchemaAnalyzer module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from src.modules.engine.algorithms.analyzer import SchemaAnalyzer


class TestSchemaAnalyzer:
    """Test cases for SchemaAnalyzer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def analyzer(self, temp_dir):
        """Create a SchemaAnalyzer instance with temporary directory."""
        return SchemaAnalyzer(schemas_dir=temp_dir)
    
    @pytest.fixture
    def sample_schema(self):
        """Sample OpenAPI schema for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/users/{id}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {}
            }
        }
    
    def test_analyze_schema_basic(self, analyzer, sample_schema):
        """Test basic schema analysis."""
        result = analyzer.analyze_schema(sample_schema)
        
        assert "endpoints" in result
        assert len(result["endpoints"]) > 0
        
        endpoint = result["endpoints"][0]
        assert endpoint["path"] == "/users/{id}"
        assert endpoint["method"] == "GET"
        assert len(endpoint["parameters"]) > 0
    
    def test_analyze_schema_path_parameters(self, analyzer, sample_schema):
        """Test path parameter extraction."""
        result = analyzer.analyze_schema(sample_schema)
        
        endpoint = result["endpoints"][0]
        path_params = [p for p in endpoint["parameters"] if p["location"] == "path"]
        
        assert len(path_params) > 0
        assert path_params[0]["name"] == "id"
        assert path_params[0]["required"] is True
    
    def test_analyze_schema_response_parameters(self, analyzer, sample_schema):
        """Test response parameter extraction."""
        result = analyzer.analyze_schema(sample_schema)
        
        endpoint = result["endpoints"][0]
        response_params = [p for p in endpoint["parameters"] if p["location"] == "response"]
        
        assert len(response_params) > 0
    
    def test_analyze_schema_file(self, analyzer, sample_schema, temp_dir):
        """Test analyzing schema from file."""
        # Save schema to file
        schema_file = Path(temp_dir) / "test_schema.json"
        with open(schema_file, 'w') as f:
            json.dump(sample_schema, f)
        
        result = analyzer.analyze_schema_file("test_schema.json")
        
        assert "endpoints" in result
        assert len(result["endpoints"]) > 0
    
    def test_analyze_schema_file_not_found(self, analyzer):
        """Test analyzing non-existent schema file."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_schema_file("nonexistent.json")
    
    def test_analyze_schema_swagger_2_0(self, analyzer):
        """Test analyzing Swagger 2.0 schema."""
        swagger_schema = {
            "swagger": "2.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/test": {
                    "get": {
                        "parameters": [
                            {
                                "name": "id",
                                "in": "query",
                                "type": "string"
                            }
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "definitions": {}
        }
        
        result = analyzer.analyze_schema(swagger_schema)
        
        assert "endpoints" in result
        assert len(result["endpoints"]) > 0

