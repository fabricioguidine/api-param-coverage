"""
Tests for the SchemaProcessor module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from src.modules.engine.algorithms.processor import SchemaProcessor


class TestSchemaProcessor:
    """Test cases for SchemaProcessor class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def processor(self, temp_dir):
        """Create a SchemaProcessor instance with temporary directory."""
        return SchemaProcessor(schemas_dir=temp_dir)
    
    @pytest.fixture
    def sample_schema(self):
        """Sample OpenAPI schema for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "operationId": "getUsers",
                        "tags": ["users"],
                        "responses": {"200": {"description": "OK"}}
                    },
                    "post": {
                        "summary": "Create user",
                        "tags": ["users"],
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {"type": "object"}
                },
                "responses": {},
                "parameters": {},
                "securitySchemes": {}
            },
            "tags": [
                {"name": "users", "description": "User operations"}
            ]
        }
    
    def test_load_schema_json(self, processor, sample_schema, temp_dir):
        """Test loading JSON schema."""
        schema_file = Path(temp_dir) / "test.json"
        with open(schema_file, 'w') as f:
            json.dump(sample_schema, f)
        
        loaded = processor.load_schema("test.json")
        assert loaded == sample_schema
    
    def test_load_schema_not_found(self, processor):
        """Test loading non-existent schema."""
        result = processor.load_schema("nonexistent.json")
        assert result is None
    
    def test_list_available_schemas(self, processor, sample_schema, temp_dir):
        """Test listing available schemas."""
        # Create some schema files
        schema1 = Path(temp_dir) / "schema1.json"
        schema2 = Path(temp_dir) / "schema2.yaml"
        schema3 = Path(temp_dir) / "other.txt"
        
        with open(schema1, 'w') as f:
            json.dump(sample_schema, f)
        with open(schema2, 'w') as f:
            f.write("test: data")
        with open(schema3, 'w') as f:
            f.write("not a schema")
        
        schemas = processor.list_available_schemas()
        
        assert "schema1.json" in schemas
        assert "schema2.yaml" in schemas
        assert "other.txt" not in schemas
    
    def test_process_schema(self, processor, sample_schema):
        """Test processing a schema."""
        processed = processor.process_schema(sample_schema)
        
        assert "info" in processed
        assert "version" in processed
        assert processed["version"] == "3.0.0"
        assert processed["paths_count"] == 1
        assert len(processed["endpoints"]) == 2
        assert "components" in processed
    
    def test_extract_endpoints(self, processor, sample_schema):
        """Test endpoint extraction."""
        endpoints = processor._extract_endpoints(sample_schema)
        
        assert len(endpoints) == 2
        assert endpoints[0]["method"] == "GET"
        assert endpoints[0]["path"] == "/users"
        assert endpoints[1]["method"] == "POST"
    
    def test_extract_components_openapi(self, processor, sample_schema):
        """Test component extraction for OpenAPI 3.x."""
        components = processor._extract_components(sample_schema)
        
        assert components["schemas_count"] == 1
        assert components["responses_count"] == 0
        assert components["parameters_count"] == 0
        assert components["security_schemes_count"] == 0
    
    def test_extract_components_swagger_2(self, processor):
        """Test component extraction for Swagger 2.0."""
        swagger_schema = {
            "swagger": "2.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "definitions": {"User": {}},
            "parameters": {"Param1": {}},
            "responses": {"Response1": {}},
            "securityDefinitions": {"Auth": {}}
        }
        
        components = processor._extract_components(swagger_schema)
        
        assert components["schemas_count"] == 1
        assert components["responses_count"] == 1
        assert components["parameters_count"] == 1
        assert components["security_schemes_count"] == 1
    
    def test_process_schema_file(self, processor, sample_schema, temp_dir):
        """Test processing schema from file."""
        schema_file = Path(temp_dir) / "test.json"
        with open(schema_file, 'w') as f:
            json.dump(sample_schema, f)
        
        processed = processor.process_schema_file("test.json")
        
        assert processed is not None
        assert processed["paths_count"] == 1

