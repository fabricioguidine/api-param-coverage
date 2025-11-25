"""
Tests for the BRD Validator module.
"""

import pytest
from src.modules.brd.brd_validator import BRDValidator
from src.modules.brd.brd_schema import BRDSchema, BRDRequirement, RequirementPriority, RequirementStatus


class TestBRDValidator:
    """Test cases for BRDValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a BRDValidator instance."""
        return BRDValidator()
    
    @pytest.fixture
    def sample_brd(self):
        """Create a sample BRD schema."""
        requirement1 = BRDRequirement(
            requirement_id="REQ-001",
            title="Get User",
            description="Test getting a user",
            endpoint_path="/users/{id}",
            endpoint_method="GET"
        )
        requirement2 = BRDRequirement(
            requirement_id="REQ-002",
            title="Create User",
            description="Test creating a user",
            endpoint_path="/users",
            endpoint_method="POST"
        )
        requirement3 = BRDRequirement(
            requirement_id="REQ-003",
            title="Invalid Endpoint",
            description="This endpoint doesn't exist",
            endpoint_path="/nonexistent",
            endpoint_method="GET"
        )
        
        return BRDSchema(
            brd_id="BRD-001",
            title="Test BRD",
            description="Test",
            api_name="Test API",
            requirements=[requirement1, requirement2, requirement3]
        )
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Create sample Swagger analysis data."""
        return {
            "endpoints": [
                {
                    "path": "/users/{id}",
                    "method": "GET",
                    "parameters": []
                },
                {
                    "path": "/users",
                    "method": "POST",
                    "parameters": []
                },
                {
                    "path": "/products",
                    "method": "GET",
                    "parameters": []
                }
            ]
        }
    
    def test_validator_initialization(self, validator):
        """Test BRDValidator initialization."""
        assert validator is not None
        assert validator.metrics_collector is not None
    
    def test_validate_brd_against_swagger_valid(self, validator, sample_brd, sample_analysis_data):
        """Test validation with valid BRD."""
        # Remove invalid requirement for this test
        sample_brd.requirements = sample_brd.requirements[:2]
        
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        assert report['total_brd_endpoints'] == 2
        assert report['total_swagger_endpoints'] == 3
        assert report['matched_endpoints'] == 2
        assert report['match_percentage'] > 0
        assert 'orphaned_endpoints' in report
        assert 'missing_endpoints' in report
    
    def test_validate_brd_orphaned_endpoints(self, validator, sample_brd, sample_analysis_data):
        """Test validation detects orphaned endpoints."""
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        assert len(report['orphaned_endpoints']) > 0
        assert ("/nonexistent", "GET") in report['orphaned_endpoints']
    
    def test_validate_brd_missing_endpoints(self, validator, sample_brd, sample_analysis_data):
        """Test validation detects missing endpoints."""
        # Remove invalid requirement to focus on missing
        sample_brd.requirements = sample_brd.requirements[:2]
        
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        assert len(report['missing_endpoints']) > 0
        assert ("/products", "GET") in report['missing_endpoints']
    
    def test_fuzzy_match_endpoint(self, validator):
        """Test fuzzy matching for endpoints with path parameters."""
        swagger_endpoints = {
            ("/users/123", "GET"),
            ("/users/{id}", "GET"),
            ("/products/{productId}", "GET")
        }
        
        # Should match even if parameter name differs
        result = validator._fuzzy_match_endpoint("/users/{userId}", "GET", swagger_endpoints)
        assert result is not None
        assert result[0] == "/users/{id}" or result[0] == "/users/123"
    
    def test_suggest_similar_endpoint(self, validator):
        """Test suggesting similar endpoints."""
        swagger_endpoints = {
            ("/users", "GET"),
            ("/users/{id}", "GET"),
            ("/products", "GET")
        }
        
        # Test with a path that should match
        suggestion = validator._suggest_similar_endpoint("/users/{userId}", "GET", swagger_endpoints)
        assert suggestion is not None
        assert "GET" in suggestion
        
        # Test with a path that shouldn't match (different method)
        suggestion2 = validator._suggest_similar_endpoint("/users", "POST", swagger_endpoints)
        # Should return None since no POST endpoints exist
        assert suggestion2 is None
    
    def test_generate_validation_report(self, validator, sample_brd, sample_analysis_data, tmp_path):
        """Test generating validation report file."""
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        output_path = tmp_path / "validation_report.txt"
        result_path = validator.generate_validation_report(report, output_path)
        
        assert result_path.exists()
        assert result_path == output_path
        
        # Check report content
        content = result_path.read_text()
        assert "BRD Validation Report" in content
        assert "VALIDATION SUMMARY" in content
        assert "RECOMMENDATIONS" in content
    
    def test_validate_empty_brd(self, validator, sample_analysis_data):
        """Test validation with empty BRD."""
        empty_brd = BRDSchema(
            brd_id="BRD-EMPTY",
            title="Empty BRD",
            description="Test",
            api_name="Test API",
            requirements=[]
        )
        
        report = validator.validate_brd_against_swagger(empty_brd, sample_analysis_data)
        
        assert report['total_brd_endpoints'] == 0
        assert report['matched_endpoints'] == 0
        assert len(report['missing_endpoints']) == 3  # All Swagger endpoints are missing
        assert len(report['orphaned_endpoints']) == 0
    
    def test_validate_empty_swagger(self, validator, sample_brd):
        """Test validation with empty Swagger."""
        empty_analysis = {"endpoints": []}
        
        report = validator.validate_brd_against_swagger(sample_brd, empty_analysis)
        
        assert report['total_swagger_endpoints'] == 0
        assert report['matched_endpoints'] == 0
        assert len(report['orphaned_endpoints']) == len(sample_brd.requirements)
        assert len(report['missing_endpoints']) == 0
    
    def test_validate_case_insensitive_methods(self, validator):
        """Test validation handles case-insensitive HTTP methods."""
        brd = BRDSchema(
            brd_id="BRD-CASE",
            title="Test BRD",
            description="Test",
            api_name="Test API",
            requirements=[
                BRDRequirement(
                    requirement_id="REQ-001",
                    title="Get User",
                    description="Test",
                    endpoint_path="/users",
                    endpoint_method="get"  # lowercase
                )
            ]
        )
        
        analysis_data = {
            "endpoints": [
                {"path": "/users", "method": "GET", "parameters": []}
            ]
        }
        
        report = validator.validate_brd_against_swagger(brd, analysis_data)
        assert report['matched_endpoints'] == 1
        assert report['is_valid'] is True
    
    def test_fuzzy_match_different_parameter_names(self, validator):
        """Test fuzzy matching with different parameter names."""
        swagger_endpoints = {
            ("/users/{id}", "GET"),
            ("/products/{productId}", "GET"),
            ("/orders/{orderId}/items/{itemId}", "GET")
        }
        
        # Different parameter name should still match
        result = validator._fuzzy_match_endpoint("/users/{userId}", "GET", swagger_endpoints)
        assert result is not None
        assert result[0] == "/users/{id}"
        
        # Multiple parameters
        result2 = validator._fuzzy_match_endpoint("/orders/{order}/items/{item}", "GET", swagger_endpoints)
        assert result2 is not None
        assert result2[0] == "/orders/{orderId}/items/{itemId}"
    
    def test_fuzzy_match_no_match(self, validator):
        """Test fuzzy matching when no match exists."""
        swagger_endpoints = {
            ("/users", "GET"),
            ("/products", "GET")
        }
        
        result = validator._fuzzy_match_endpoint("/orders", "GET", swagger_endpoints)
        assert result is None
    
    def test_suggest_similar_endpoint_partial_match(self, validator):
        """Test suggesting endpoints with partial path matches."""
        swagger_endpoints = {
            ("/api/v1/users", "GET"),
            ("/api/v1/products", "GET"),
            ("/api/v2/users", "GET")
        }
        
        # Should suggest closest match - test with exact path segment match
        suggestion = validator._suggest_similar_endpoint("/api/v1/users", "GET", swagger_endpoints)
        assert suggestion is not None
        assert "/api/v1/users" in suggestion or "users" in suggestion.lower()
        
        # Test with similar but not exact match
        suggestion2 = validator._suggest_similar_endpoint("/api/v1/user", "GET", swagger_endpoints)
        # Should return a suggestion (may not be perfect match due to scoring)
        assert suggestion2 is not None
    
    def test_suggest_similar_endpoint_low_score(self, validator):
        """Test that low similarity scores return None."""
        swagger_endpoints = {
            ("/users", "GET"),
            ("/products", "GET")
        }
        
        # Very different path should return None
        suggestion = validator._suggest_similar_endpoint("/completely/different/path", "GET", swagger_endpoints)
        assert suggestion is None
    
    def test_validation_report_with_errors(self, validator, sample_brd, sample_analysis_data, tmp_path):
        """Test validation report generation with validation errors."""
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        output_path = tmp_path / "validation_report_errors.txt"
        result_path = validator.generate_validation_report(report, output_path)
        
        content = result_path.read_text()
        assert "✗ INVALID" in content or "INVALID" in content
        assert "orphaned" in content.lower() or "Orphaned" in content
    
    def test_validation_report_default_path(self, validator, sample_brd, sample_analysis_data):
        """Test validation report generation with default path."""
        report = validator.validate_brd_against_swagger(sample_brd, sample_analysis_data)
        
        result_path = validator.generate_validation_report(report)
        
        assert result_path.exists()
        assert "brd_validation_report" in str(result_path)

