"""
Mock Services for Testing

Mock LLM API, HTTP requests, and other external dependencies.
"""

import json
from typing import Optional
from unittest.mock import Mock


def mock_openai_response(content: Optional[str] = None, model: str = "gpt-4"):
    """Create a mock OpenAI API response."""
    if content is None:
        content = """Feature: Test API
  Scenario: Test endpoint
    Given the API is available
    When I call GET /test
    Then I should receive a 200 response
"""

    return Mock(
        choices=[Mock(message=Mock(content=content))],
        model=model,
        usage=Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )


def mock_http_response(status_code: int = 200, content: Optional[dict] = None, headers: Optional[dict] = None):
    """Create a mock HTTP response."""
    if content is None:
        content = {"swagger": "2.0", "info": {"title": "Test API", "version": "1.0.0"}, "paths": {}}

    response = Mock()
    response.status_code = status_code
    response.json.return_value = content
    response.text = json.dumps(content)
    response.headers = headers or {"Content-Type": "application/json"}
    response.raise_for_status = Mock()

    return response


def mock_brd_schema():
    """Create a mock BRD schema for testing."""
    return {
        "title": "Test BRD",
        "version": "1.0.0",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "title": "User Management",
                "description": "Manage users",
                "endpoint_path": "/users",
                "endpoint_method": "GET",
                "priority": "high",
                "status": "active",
                "test_scenarios": [
                    {
                        "scenario_id": "SCEN-001",
                        "scenario_name": "Get all users",
                        "description": "Retrieve list of users",
                        "test_steps": ["Given users exist", "When I request users", "Then I receive user list"],
                        "expected_result": "200 OK with user list",
                        "priority": "high",
                    }
                ],
            }
        ],
    }
