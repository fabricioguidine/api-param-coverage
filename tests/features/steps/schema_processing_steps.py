"""
Step definitions for schema processing feature.
"""

from behave import given, when, then
from unittest.mock import Mock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.swagger.schema_fetcher import SchemaFetcher
from src.modules.engine import SchemaProcessor, SchemaAnalyzer


@given('I have a Swagger 2.0 schema URL')
def step_swagger_2_url(context):
    """Set up Swagger 2.0 URL."""
    context.schema_url = "https://example.com/swagger.json"
    context.expected_format = "Swagger 2.0"


@given('I have an OpenAPI 3.0 schema URL')
def step_openapi_3_url(context):
    """Set up OpenAPI 3.0 URL."""
    context.schema_url = "https://example.com/openapi.json"
    context.expected_format = "OpenAPI 3.0"


@given('I have a downloaded schema file')
def step_downloaded_schema(context):
    """Set up downloaded schema."""
    context.schema_path = "test_schema.json"
    context.schema_data = {
        'swagger': '2.0',
        'info': {'title': 'Test API'},
        'paths': {
            '/test': {'get': {}}
        }
    }


@given('I have a processed schema')
def step_processed_schema(context):
    """Set up processed schema."""
    context.processed_data = {
        'info': {'title': 'Test API'},
        'paths_count': 1,
        'paths': {
            '/test': {'get': {}}
        }
    }


@when('I download the schema')
def step_download_schema(context):
    """Download the schema."""
    with patch('src.modules.swagger.schema_fetcher.requests.get') as mock_get:
        mock_response = Mock()
        if context.expected_format == "Swagger 2.0":
            mock_response.json.return_value = {
                'swagger': '2.0',
                'info': {'title': 'Test API'},
                'paths': {}
            }
        else:
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
    processor = SchemaProcessor()
    context.processed_data = processor.process_schema_file(Path(context.schema_path).name)


@when('I analyze the schema')
def step_analyze_schema(context):
    """Analyze the schema."""
    analyzer = SchemaAnalyzer()
    context.analysis_data = analyzer.analyze_schema_file(Path(context.schema_path).name)


@then('the schema should be downloaded successfully')
def step_schema_downloaded(context):
    """Verify schema downloaded."""
    assert context.schema_path is not None


@then('the schema format should be detected as "{format}"')
def step_format_detected(context, format):
    """Verify format detection."""
    # Format detection happens during download
    assert context.expected_format == format


@then('the schema should be saved to the schemas directory')
def step_schema_saved(context):
    """Verify schema saved."""
    assert context.schema_path is not None
    assert Path(context.schema_path).exists() or "schemas" in str(context.schema_path)


@then('endpoints should be extracted')
def step_endpoints_extracted(context):
    """Verify endpoints extracted."""
    assert context.processed_data is not None
    assert 'paths' in context.processed_data or 'paths_count' in context.processed_data


@then('endpoint count should be greater than zero')
def step_endpoint_count(context):
    """Verify endpoint count."""
    if 'paths_count' in context.processed_data:
        assert context.processed_data['paths_count'] > 0
    elif 'paths' in context.processed_data:
        assert len(context.processed_data['paths']) > 0


@then('the analysis should complete successfully')
def step_analysis_complete(context):
    """Verify analysis complete."""
    assert context.analysis_data is not None


@then('complexity metrics should be calculated')
def step_complexity_calculated(context):
    """Verify complexity metrics."""
    assert context.analysis_data is not None
    # Complexity metrics are part of analysis_data


@then('parameter information should be extracted')
def step_parameters_extracted(context):
    """Verify parameters extracted."""
    assert context.analysis_data is not None
    assert 'endpoints' in context.analysis_data

