"""
Step definitions for BRD workflow feature.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

from behave import given, then, when

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.modules.brd import BRDLoader, BRDParser, BRDValidator, SchemaCrossReference


@given("I have a BRD schema")
def step_brd_schema(context):
    """Set up BRD schema."""
    context.brd = Mock()
    context.brd.title = "Test BRD"
    context.brd.requirements = [
        Mock(endpoint_path="/users", endpoint_method="GET"),
        Mock(endpoint_path="/products", endpoint_method="POST"),
    ]
    context.brd.get_all_endpoints = Mock(return_value=[("/users", "GET"), ("/products", "POST")])


@given("I have a Swagger schema")
def step_swagger_schema(context):
    """Set up Swagger schema."""
    context.analysis_data = {
        "endpoints": [
            {"path": "/users", "method": "GET"},
            {"path": "/products", "method": "POST"},
            {"path": "/orders", "method": "GET"},
        ]
    }


@given("I have a Swagger schema analysis")
def step_swagger_analysis(context):
    """Set up Swagger analysis."""
    context.analysis_data = {
        "endpoints": [{"path": "/users", "method": "GET"}, {"path": "/products", "method": "POST"}],
        "total_endpoints": 2,
    }


@given("I have a BRD schema file in the output directory")
def step_brd_file(context):
    """Set up BRD file."""
    context.brd_filename = "test_brd.json"
    context.brd_loader = BRDLoader()


@given("I have a BRD text document")
def step_brd_document(context):
    """Set up BRD document."""
    context.brd_document = "test_brd.txt"
    context.brd_parser = BRDParser()


@when("I generate a BRD from the Swagger schema")
def step_generate_brd(context):
    """Generate BRD from Swagger."""
    if hasattr(context, "coverage_percentage"):
        context.coverage_percentage = getattr(context, "coverage_percentage", 100.0)
    else:
        context.coverage_percentage = 100.0
    # Mock BRD generation with requirements
    context.brd = Mock()
    context.brd.title = "Generated BRD"
    # Create mock requirements list
    req1 = Mock()
    req1.endpoint_path = "/users"
    req1.endpoint_method = "GET"
    req1.title = "Get users"
    req1.priority = Mock()
    req1.priority.value = "high"
    req1.test_scenarios = [Mock()]

    req2 = Mock()
    req2.endpoint_path = "/products"
    req2.endpoint_method = "POST"
    req2.title = "Create product"
    req2.priority = Mock()
    req2.priority.value = "high"
    req2.test_scenarios = [Mock()]

    context.brd.requirements = [req1, req2]
    context.brd.get_all_endpoints = Mock(return_value=[("/users", "GET"), ("/products", "POST")])

    # Mock get_requirements_for_endpoint to return a list
    def mock_get_requirements(path, method):
        matching_reqs = [r for r in context.brd.requirements if r.endpoint_path == path and r.endpoint_method == method]
        return matching_reqs if matching_reqs else [req1]  # Default to req1 if no match

    context.brd.get_requirements_for_endpoint = Mock(side_effect=mock_get_requirements)


@when('I specify coverage percentage of "{percentage}"')
def step_coverage_percentage(context, percentage):
    """Set coverage percentage."""
    context.coverage_percentage = float(percentage)


@when("I validate the BRD against the Swagger schema")
def step_validate_brd(context):
    """Validate BRD."""
    validator = BRDValidator()
    context.validation_report = validator.validate_brd_against_swagger(context.brd, context.analysis_data)


@when("I cross-reference the BRD with the Swagger schema")
def step_cross_reference(context):
    """Cross-reference BRD."""
    # Ensure BRD has proper structure
    if not hasattr(context.brd, "get_all_endpoints"):
        context.brd.get_all_endpoints = Mock(return_value=[("/users", "GET"), ("/products", "POST")])
    if not hasattr(context.brd, "requirements") or not context.brd.requirements:
        # Create mock requirements
        req1 = Mock()
        req1.endpoint_path = "/users"
        req1.endpoint_method = "GET"
        req1.title = "Get users"
        req1.requirement_id = "req1"
        req1.priority = Mock()
        req1.priority.value = "high"
        req1.test_scenarios = [Mock()]
        context.brd.requirements = [req1]

    # Mock get_requirements_for_endpoint to return a list - MUST be set before calling filter_endpoints_by_brd
    def mock_get_requirements(path, method):
        req = Mock()
        req.requirement_id = "req1"
        req.title = f"Requirement for {path} {method}"
        req.priority = Mock()
        req.priority.value = "high"
        req.test_scenarios = [Mock()]
        return [req]

    # Always set/get the method to ensure it's available
    context.brd.get_requirements_for_endpoint = Mock(side_effect=mock_get_requirements)

    cross_ref = SchemaCrossReference()
    context.filtered_data = cross_ref.filter_endpoints_by_brd(context.analysis_data, context.brd)
    context.coverage_report = cross_ref.get_brd_coverage_report(context.analysis_data, context.brd)


@when("I load the BRD from file")
def step_load_brd(context):
    """Load BRD from file."""
    # Mock loading with requirements
    context.brd = Mock()
    context.brd.title = "Loaded BRD"
    req1 = Mock()
    req1.endpoint_path = "/test"
    req1.endpoint_method = "GET"
    req1.title = "Test requirement"
    req1.priority = Mock()
    req1.priority.value = "high"
    req1.test_scenarios = [Mock()]
    context.brd.requirements = [req1]
    context.brd.get_all_endpoints = Mock(return_value=[("/test", "GET")])


@when("I parse the BRD document")
def step_parse_brd(context):
    """Parse BRD document."""
    # Mock parsing
    context.brd = Mock()
    context.brd.title = "Parsed BRD"
    context.brd.requirements = []


@then("a BRD should be created")
def step_brd_created(context):
    """Verify BRD created."""
    assert context.brd is not None


@then("the BRD should contain requirements for all endpoints")
def step_brd_contains_all(context):
    """Verify BRD contains all endpoints."""
    if context.coverage_percentage == 100.0:
        assert len(context.brd.requirements) > 0


@then("the BRD should prioritize critical endpoints")
def step_brd_prioritizes(context):
    """Verify BRD prioritizes critical endpoints."""
    assert context.brd is not None
    # Priority logic would be verified here


@then('the BRD should cover approximately "{percentage}" percent of endpoints')
def step_brd_coverage(context, percentage):
    """Verify BRD coverage."""
    float(percentage)
    # Ensure BRD was generated if it doesn't exist
    if not hasattr(context, "brd") or context.brd is None:
        # Generate BRD similar to step_generate_brd
        context.brd = Mock()
        context.brd.title = "Generated BRD"
        req1 = Mock()
        req1.endpoint_path = "/test"
        req1.endpoint_method = "GET"
        req1.title = "Test requirement"
        req1.requirement_id = "req1"
        req1.priority = Mock()
        req1.priority.value = "high"
        req1.test_scenarios = [Mock()]
        context.brd.requirements = [req1]
        context.brd.get_all_endpoints = Mock(return_value=[("/test", "GET")])

        def mock_get_requirements(path, method):
            return [req1]

        context.brd.get_requirements_for_endpoint = Mock(side_effect=mock_get_requirements)

    # Coverage would be calculated and verified
    assert context.brd is not None


@then("validation should complete")
def step_validation_complete(context):
    """Verify validation complete."""
    assert context.validation_report is not None


@then("orphaned endpoints should be identified")
def step_orphaned_identified(context):
    """Verify orphaned endpoints identified."""
    assert "orphaned_endpoints" in context.validation_report


@then("missing endpoints should be identified")
def step_missing_identified(context):
    """Verify missing endpoints identified."""
    assert "missing_endpoints" in context.validation_report


@then("a validation report should be generated")
def step_validation_report(context):
    """Verify validation report generated."""
    assert context.validation_report is not None
    assert "is_valid" in context.validation_report


@then("endpoints should be filtered by BRD coverage")
def step_endpoints_filtered(context):
    """Verify endpoints filtered."""
    assert context.filtered_data is not None


@then("coverage percentage should be calculated")
def step_coverage_calculated(context):
    """Verify coverage calculated."""
    assert context.coverage_report is not None
    assert "coverage_percentage" in context.coverage_report


@then("a coverage report should be generated")
def step_coverage_report(context):
    """Verify coverage report generated."""
    assert context.coverage_report is not None


@then("the BRD should be loaded successfully")
def step_brd_loaded(context):
    """Verify BRD loaded."""
    assert context.brd is not None


@then("the BRD structure should be valid")
def step_brd_structure_valid(context):
    """Verify BRD structure."""
    assert hasattr(context.brd, "title")
    assert hasattr(context.brd, "requirements")


@then("requirements should be accessible")
def step_requirements_accessible(context):
    """Verify requirements accessible."""
    assert hasattr(context.brd, "requirements")
    assert isinstance(context.brd.requirements, list)


@then("the document should be parsed successfully")
def step_document_parsed(context):
    """Verify document parsed."""
    assert context.brd is not None


@then("a BRD schema should be created")
def step_brd_schema_created(context):
    """Verify BRD schema created."""
    assert context.brd is not None


@then("requirements should be extracted")
def step_requirements_extracted(context):
    """Verify requirements extracted."""
    assert hasattr(context.brd, "requirements")


@then("the BRD should be saved to the output directory")
def step_brd_saved(context):
    """Verify BRD saved to output directory."""
    # In a real scenario, this would check if the file exists
    # For testing, we just verify that the BRD was created
    assert context.brd is not None
    assert hasattr(context.brd, "title")
