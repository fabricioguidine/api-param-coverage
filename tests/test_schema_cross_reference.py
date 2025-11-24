"""
Tests for the Schema Cross-Reference module.
"""

import pytest
from src.modules.brd.schema_cross_reference import SchemaCrossReference
from src.modules.brd.brd_schema import BRDSchema, BRDRequirement, RequirementPriority


class TestSchemaCrossReference:
    """Test cases for SchemaCrossReference class."""
    
    @pytest.fixture
    def cross_ref(self):
        """Create a SchemaCrossReference instance."""
        return SchemaCrossReference()
    
    @pytest.fixture
    def sample_brd(self):
        """Create a sample BRD for testing."""
        requirement1 = BRDRequirement(
            requirement_id="REQ-001",
            title="Get User",
            description="Test",
            endpoint_path="/users/{id}",
            endpoint_method="GET",
            priority=RequirementPriority.HIGH
        )
        requirement2 = BRDRequirement(
            requirement_id="REQ-002",
            title="Create User",
            description="Test",
            endpoint_path="/users",
            endpoint_method="POST",
            priority=RequirementPriority.HIGH
        )
        
        return BRDSchema(
            brd_id="BRD-001",
            title="Test BRD",
            description="Test",
            api_name="Test API",
            requirements=[requirement1, requirement2]
        )
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Create sample analysis data."""
        return {
            "endpoints": [
                {
                    "path": "/users/{id}",
                    "method": "GET",
                    "parameters": [
                        {"name": "id", "type": "string", "location": "path"}
                    ]
                },
                {
                    "path": "/users",
                    "method": "POST",
                    "parameters": [
                        {"name": "name", "type": "string", "location": "body"}
                    ]
                },
                {
                    "path": "/posts",
                    "method": "GET",
                    "parameters": []
                }
            ]
        }
    
    def test_filter_endpoints_by_brd(self, cross_ref, sample_brd, sample_analysis_data):
        """Test filtering endpoints by BRD."""
        filtered = cross_ref.filter_endpoints_by_brd(sample_analysis_data, sample_brd)
        
        assert "endpoints" in filtered
        assert filtered["total_endpoints"] == 3
        assert filtered["brd_covered_endpoints"] == 2
        assert filtered["coverage_percentage"] == pytest.approx(66.67, rel=0.1)
        
        # Check that filtered endpoints have BRD metadata
        for endpoint in filtered["endpoints"]:
            assert endpoint["brd_covered"] is True
            assert "brd_requirements" in endpoint
    
    def test_get_brd_coverage_report(self, cross_ref, sample_brd, sample_analysis_data):
        """Test generating BRD coverage report."""
        report = cross_ref.get_brd_coverage_report(sample_analysis_data, sample_brd)
        
        assert report["total_endpoints"] == 3
        assert report["covered_endpoints"] == 2
        assert report["not_covered_endpoints"] == 1
        assert report["coverage_percentage"] == pytest.approx(66.67, rel=0.1)
        assert len(report["covered"]) == 2
        assert len(report["not_covered"]) == 1
    
    def test_empty_brd_coverage(self, cross_ref, sample_analysis_data):
        """Test coverage with empty BRD."""
        empty_brd = BRDSchema(
            brd_id="BRD-EMPTY",
            title="Empty BRD",
            description="Test",
            api_name="API"
        )
        
        filtered = cross_ref.filter_endpoints_by_brd(sample_analysis_data, empty_brd)
        assert filtered["brd_covered_endpoints"] == 0
        assert filtered["coverage_percentage"] == 0.0


