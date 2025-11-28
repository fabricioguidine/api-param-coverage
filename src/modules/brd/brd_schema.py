"""
BRD Schema Definition

Defines the schema structure for Business Requirement Documents (BRD).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class RequirementPriority(Enum):
    """Priority levels for requirements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(Enum):
    """Status of a requirement."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class BRDTestScenario:
    """Represents a test scenario within a requirement."""
    scenario_id: str
    scenario_name: str
    description: str
    test_steps: List[str] = field(default_factory=list)
    expected_result: str = ""
    priority: RequirementPriority = RequirementPriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "description": self.description,
            "test_steps": self.test_steps,
            "expected_result": self.expected_result,
            "priority": self.priority.value,
            "tags": self.tags
        }


@dataclass
class BRDRequirement:
    """Represents a single business requirement."""
    requirement_id: str
    title: str
    description: str
    endpoint_path: str  # API endpoint path (e.g., "/users/{id}")
    endpoint_method: str  # HTTP method (e.g., "GET", "POST")
    priority: RequirementPriority = RequirementPriority.MEDIUM
    status: RequirementStatus = RequirementStatus.PENDING
    test_scenarios: List[BRDTestScenario] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    related_endpoints: List[str] = field(default_factory=list)  # Other endpoints that might be related
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "endpoint_path": self.endpoint_path,
            "endpoint_method": self.endpoint_method,
            "priority": self.priority.value,
            "status": self.status.value,
            "test_scenarios": [scenario.to_dict() for scenario in self.test_scenarios],
            "acceptance_criteria": self.acceptance_criteria,
            "related_endpoints": self.related_endpoints
        }


@dataclass
class BRDSchema:
    """Business Requirement Document schema."""
    brd_id: str
    title: str
    description: str
    api_name: str
    api_version: str = ""
    created_date: str = ""
    requirements: List[BRDRequirement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "brd_id": self.brd_id,
            "title": self.title,
            "description": self.description,
            "api_name": self.api_name,
            "api_version": self.api_version,
            "created_date": self.created_date,
            "requirements": [req.to_dict() for req in self.requirements],
            "metadata": self.metadata
        }
    
    def get_requirements_for_endpoint(self, path: str, method: str) -> List[BRDRequirement]:
        """Get requirements for a specific endpoint."""
        return [
            req for req in self.requirements
            if req.endpoint_path == path and req.endpoint_method.upper() == method.upper()
        ]
    
    def get_all_endpoints(self) -> List[tuple]:
        """Get all unique endpoint (path, method) tuples from requirements."""
        endpoints = set()
        for req in self.requirements:
            endpoints.add((req.endpoint_path, req.endpoint_method.upper()))
        return list(endpoints)





