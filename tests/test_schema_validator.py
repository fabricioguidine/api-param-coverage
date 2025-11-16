"""
Tests for the SchemaValidator module.
"""

import pytest
from src.modules.swagger_tool.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test cases for SchemaValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a SchemaValidator instance."""
        return SchemaValidator()
    
    @pytest.fixture
    def openapi_3_schema(self):
        """Sample OpenAPI 3.0 schema."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "components": {
                "schemas": {}
            }
        }
    
    @pytest.fixture
    def swagger_2_schema(self):
        """Sample Swagger 2.0 schema."""
        return {
            "swagger": "2.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "definitions": {}
        }
    
    def test_detect_openapi_3_0(self, validator, openapi_3_schema):
        """Test detection of OpenAPI 3.0 schema."""
        schema_type, version = validator.detect_schema_type(openapi_3_schema)
        assert schema_type == "openapi"
        assert version == "3.0.0"
    
    def test_detect_swagger_2_0(self, validator, swagger_2_schema):
        """Test detection of Swagger 2.0 schema."""
        schema_type, version = validator.detect_schema_type(swagger_2_schema)
        assert schema_type == "swagger"
        assert version == "2.0"
    
    def test_detect_unknown_schema(self, validator):
        """Test detection of unknown schema."""
        schema_type, version = validator.detect_schema_type({})
        assert schema_type == "unknown"
        assert version is None
    
    def test_validate_valid_schema(self, validator, openapi_3_schema):
        """Test validation of valid schema."""
        is_valid, error = validator.validate_schema(openapi_3_schema)
        assert is_valid is True
        assert error is None
    
    def test_validate_missing_paths(self, validator):
        """Test validation of schema missing paths."""
        schema = {"info": {"title": "Test"}}
        is_valid, error = validator.validate_schema(schema)
        assert is_valid is False
        assert "paths" in error
    
    def test_validate_missing_info(self, validator):
        """Test validation of schema missing info."""
        schema = {"paths": {}}
        is_valid, error = validator.validate_schema(schema)
        assert is_valid is False
        assert "info" in error
    
    def test_normalize_schema(self, validator, openapi_3_schema):
        """Test schema normalization."""
        normalized = validator.normalize_schema(openapi_3_schema)
        assert "components" in normalized
        assert "schemas" in normalized["components"]
    
    def test_get_schema_info(self, validator, openapi_3_schema):
        """Test getting schema information."""
        info = validator.get_schema_info(openapi_3_schema)
        assert info["type"] == "openapi"
        assert info["version"] == "3.0.0"
        assert info["is_valid"] is True
        assert info["endpoint_count"] == 1

