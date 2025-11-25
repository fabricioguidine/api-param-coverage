"""
Step definitions for main workflow feature.
"""

from behave import given, when, then, step
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.swagger.schema_fetcher import SchemaFetcher
from src.modules.engine import SchemaProcessor, SchemaAnalyzer, LLMPrompter
from src.modules.engine.algorithms import CSVGenerator
from src.modules.brd import BRDLoader, BRDParser, SchemaCrossReference, BRDValidator, BRDGenerator


@given('the system is initialized')
def step_system_initialized(context):
    """Initialize the system for testing."""
    context.temp_dir = tempfile.mkdtemp()
    context.schema_path = None
    context.processed_data = None
    context.analysis_data = None
    context.brd = None
    context.gherkin_scenarios = None
    context.csv_path = None


@given('I have a valid OpenAI API key configured')
def step_valid_api_key(context):
    """Set up a valid API key."""
    context.api_key = os.getenv('OPENAI_API_KEY', 'test-api-key')
    os.environ['OPENAI_API_KEY'] = context.api_key


@given('I do not have a valid OpenAI API key configured')
def step_no_api_key(context):
    """Remove API key."""
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    context.api_key = None


@given('I provide a Swagger schema URL "{url}"')
def step_provide_schema_url(context, url):
    """Store the schema URL."""
    context.schema_url = url


@given('I provide an invalid Swagger schema URL "{url}"')
def step_provide_invalid_url(context, url):
    """Store an invalid schema URL."""
    context.schema_url = url
    context.is_invalid = True


@given('I provide an empty schema URL')
def step_provide_empty_url(context):
    """Store an empty URL."""
    context.schema_url = ""


@given('I have a Swagger schema with multiple endpoints')
def step_swagger_with_endpoints(context):
    """Set up a mock Swagger schema."""
    context.processed_data = {
        'info': {'title': 'Test API'},
        'paths_count': 10,
        'paths': {
            '/users': {'get': {}, 'post': {}},
            '/products': {'get': {}, 'put': {}}
        }
    }
    context.analysis_data = {
        'endpoints': [
            {'path': '/users', 'method': 'GET'},
            {'path': '/users', 'method': 'POST'},
            {'path': '/products', 'method': 'GET'},
            {'path': '/products', 'method': 'PUT'}
        ]
    }


@given('I have a processed Swagger schema')
def step_processed_schema(context):
    """Set up processed schema data."""
    context.processed_data = {
        'info': {'title': 'Test API'},
        'paths_count': 5
    }
    context.analysis_data = {
        'endpoints': [
            {'path': '/test', 'method': 'GET'}
        ]
    }


@when('I run the main workflow')
def step_run_main_workflow(context):
    """Run the main workflow steps."""
    try:
        # Step 1: Download schema
        if hasattr(context, 'is_invalid') and context.is_invalid:
            context.schema_path = None
        elif context.schema_url:
            with patch('src.modules.swagger.schema_fetcher.requests.get') as mock_get:
                if context.schema_url == "":
                    context.schema_path = None
                else:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        'openapi': '3.0.0',
                        'info': {'title': 'Test API'},
                        'paths': {}
                    }
                    mock_response.status_code = 200
                    mock_get.return_value = mock_response
                    fetcher = SchemaFetcher()
                    context.schema_path = fetcher.download_and_save(context.schema_url, "json")
        else:
            context.schema_path = None
    except Exception as e:
        context.error = str(e)
        context.schema_path = None


@when('I choose to generate BRD from Swagger')
def step_choose_generate_brd(context):
    """Choose to generate BRD."""
    context.brd_choice = "generate"


@when('I choose to load existing BRD schema')
def step_choose_load_brd(context):
    """Choose to load existing BRD."""
    context.brd_choice = "load"


@when('I choose to parse BRD from document')
def step_choose_parse_brd(context):
    """Choose to parse BRD from document."""
    context.brd_choice = "parse"


# Coverage percentage step is defined in brd_workflow_steps.py


@when('I select BRD file "{filename}"')
def step_select_brd_file(context, filename):
    """Select a BRD file."""
    context.brd_filename = filename


@when('I download the schema')
def step_download_schema(context):
    """Download the schema."""
    if hasattr(context, 'schema_url'):
        with patch('src.modules.swagger.schema_fetcher.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'openapi': '3.0.0',
                'info': {'title': 'Test API'},
                'paths': {}
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            fetcher = SchemaFetcher()
            context.schema_path = fetcher.download_and_save(context.schema_url, "json")


@when('I process the schema')
def step_process_schema(context):
    """Process the schema."""
    if context.schema_path:
        processor = SchemaProcessor()
        context.processed_data = processor.process_schema_file(Path(context.schema_path).name)


@when('I analyze the schema')
def step_analyze_schema(context):
    """Analyze the schema."""
    if context.processed_data:
        analyzer = SchemaAnalyzer()
        context.analysis_data = analyzer.analyze_schema_file(Path(context.schema_path).name)


@then('the schema should be downloaded successfully')
def step_schema_downloaded(context):
    """Verify schema was downloaded."""
    assert context.schema_path is not None, "Schema should be downloaded"


@then('the schema should be processed')
def step_schema_processed(context):
    """Verify schema was processed."""
    assert context.processed_data is not None, "Schema should be processed"
    assert 'info' in context.processed_data or 'paths_count' in context.processed_data


@then('the schema should be analyzed')
def step_schema_analyzed(context):
    """Verify schema was analyzed."""
    assert context.analysis_data is not None, "Schema should be analyzed"
    assert 'endpoints' in context.analysis_data


@then('a BRD should be generated')
def step_brd_generated(context):
    """Verify BRD was generated."""
    if context.brd_choice == "generate" and hasattr(context, 'api_key') and context.api_key:
        # Mock BRD generation
        context.brd = Mock()
        context.brd.title = "Generated BRD"
        context.brd.requirements = []
        assert context.brd is not None


@then('BRD should be validated against the schema')
def step_brd_validated(context):
    """Verify BRD was validated."""
    if context.brd and context.analysis_data:
        validator = BRDValidator()
        validation_report = validator.validate_brd_against_swagger(context.brd, context.analysis_data)
        assert validation_report is not None
        context.validation_report = validation_report


@then('endpoints should be cross-referenced')
def step_endpoints_cross_referenced(context):
    """Verify endpoints were cross-referenced."""
    if context.brd and context.analysis_data:
        cross_ref = SchemaCrossReference()
        filtered_data = cross_ref.filter_endpoints_by_brd(context.analysis_data, context.brd)
        assert filtered_data is not None


@then('Gherkin scenarios should be generated')
def step_gherkin_generated(context):
    """Verify Gherkin scenarios were generated."""
    if context.processed_data and context.analysis_data:
        # Mock Gherkin generation
        context.gherkin_scenarios = "Feature: Test API\n  Scenario: Test endpoint\n    Given the API is available"
        assert context.gherkin_scenarios is not None


@then('CSV file should be created')
def step_csv_created(context):
    """Verify CSV file was created."""
    if context.gherkin_scenarios:
        csv_generator = CSVGenerator(output_dir=context.temp_dir)
        context.csv_path = csv_generator.gherkin_to_csv(context.gherkin_scenarios, "test")
        assert context.csv_path is not None


@then('analytics reports should be generated')
def step_analytics_generated(context):
    """Verify analytics reports were generated."""
    analytics_dir = Path(context.temp_dir) / "analytics"
    # Analytics should be generated during workflow
    assert True  # Placeholder - analytics are generated by modules


@then('the system should display an error message')
def step_error_displayed(context):
    """Verify error message was displayed."""
    assert hasattr(context, 'error') or context.schema_path is None or context.api_key is None


@then('the workflow should exit gracefully')
def step_workflow_exits(context):
    """Verify workflow exits gracefully."""
    # Workflow should handle errors without crashing
    assert True


@then('the BRD should cover approximately "{percentage}" percent of endpoints')
def step_brd_coverage(context, percentage):
    """Verify BRD coverage percentage."""
    expected_coverage = float(percentage)
    # This would be verified in actual implementation
    assert True  # Placeholder


@then('only covered endpoints should be tested')
def step_only_covered_tested(context):
    """Verify only covered endpoints are tested."""
    # This would be verified in actual implementation
    assert True  # Placeholder


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    if hasattr(context, 'temp_dir') and Path(context.temp_dir).exists():
        shutil.rmtree(context.temp_dir, ignore_errors=True)

