"""
Tests for the BRD Schema module.
"""

import pytest
from src.modules.brd.brd_schema import (
    BRDSchema, BRDRequirement, BRDTestScenario,
    RequirementPriority, RequirementStatus
)


class TestBRDSchema:
    """Test cases for BRDSchema class."""
    
    def test_brd_schema_creation(self):
        """Test creating a BRD schema."""
        brd = BRDSchema(
            brd_id="BRD-001",
            title="Test BRD",
            description="Test description",
            api_name="Test API"
        )
        
        assert brd.brd_id == "BRD-001"
        assert brd.title == "Test BRD"
        assert brd.description == "Test description"
        assert brd.api_name == "Test API"
        assert len(brd.requirements) == 0
    
    def test_brd_schema_to_dict(self):
        """Test converting BRD schema to dictionary."""
        brd = BRDSchema(
            brd_id="BRD-001",
            title="Test BRD",
            description="Test",
            api_name="API"
        )
        
        result = brd.to_dict()
        assert result["brd_id"] == "BRD-001"
        assert result["title"] == "Test BRD"
        assert isinstance(result["requirements"], list)
    
    def test_brd_get_all_endpoints(self):
        """Test getting all endpoints from BRD."""
        requirement1 = BRDRequirement(
            requirement_id="REQ-001",
            title="Test 1",
            description="Test",
            endpoint_path="/users/{id}",
            endpoint_method="GET"
        )
        requirement2 = BRDRequirement(
            requirement_id="REQ-002",
            title="Test 2",
            description="Test",
            endpoint_path="/users",
            endpoint_method="POST"
        )
        
        brd = BRDSchema(
            brd_id="BRD-001",
            title="Test",
            description="Test",
            api_name="API",
            requirements=[requirement1, requirement2]
        )
        
        endpoints = brd.get_all_endpoints()
        assert len(endpoints) == 2
        assert ("/users/{id}", "GET") in endpoints
        assert ("/users", "POST") in endpoints
    
    def test_brd_get_requirements_for_endpoint(self):
        """Test getting requirements for a specific endpoint."""
        requirement = BRDRequirement(
            requirement_id="REQ-001",
            title="Test",
            description="Test",
            endpoint_path="/users/{id}",
            endpoint_method="GET"
        )
        
        brd = BRDSchema(
            brd_id="BRD-001",
            title="Test",
            description="Test",
            api_name="API",
            requirements=[requirement]
        )
        
        requirements = brd.get_requirements_for_endpoint("/users/{id}", "GET")
        assert len(requirements) == 1
        assert requirements[0].requirement_id == "REQ-001"


class TestBRDRequirement:
    """Test cases for BRDRequirement class."""
    
    def test_requirement_creation(self):
        """Test creating a requirement."""
        req = BRDRequirement(
            requirement_id="REQ-001",
            title="Test Requirement",
            description="Test description",
            endpoint_path="/users",
            endpoint_method="GET"
        )
        
        assert req.requirement_id == "REQ-001"
        assert req.title == "Test Requirement"
        assert req.endpoint_path == "/users"
        assert req.endpoint_method == "GET"
        assert req.priority == RequirementPriority.MEDIUM
        assert req.status == RequirementStatus.PENDING
    
    def test_requirement_to_dict(self):
        """Test converting requirement to dictionary."""
        req = BRDRequirement(
            requirement_id="REQ-001",
            title="Test",
            description="Test",
            endpoint_path="/users",
            endpoint_method="GET"
        )
        
        result = req.to_dict()
        assert result["requirement_id"] == "REQ-001"
        assert result["priority"] == "medium"
        assert isinstance(result["test_scenarios"], list)


class TestBRDTestScenario:
    """Test cases for BRDTestScenario class."""
    
    def test_scenario_creation(self):
        """Test creating a test scenario."""
        scenario = BRDTestScenario(
            scenario_id="SCEN-001",
            scenario_name="Test Scenario",
            description="Test description",
            test_steps=["Given step", "When step", "Then step"]
        )
        
        assert scenario.scenario_id == "SCEN-001"
        assert scenario.scenario_name == "Test Scenario"
        assert len(scenario.test_steps) == 3
        assert scenario.priority == RequirementPriority.MEDIUM
    
    def test_scenario_to_dict(self):
        """Test converting scenario to dictionary."""
        scenario = BRDTestScenario(
            scenario_id="SCEN-001",
            scenario_name="Test",
            description="Test",
            test_steps=["Step 1"]
        )
        
        result = scenario.to_dict()
        assert result["scenario_id"] == "SCEN-001"
        assert result["priority"] == "medium"
        assert isinstance(result["test_steps"], list)



