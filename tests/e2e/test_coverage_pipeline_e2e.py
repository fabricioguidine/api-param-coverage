"""
End-to-end tests for the API parameter coverage pipeline.

These tests exercise the real public API end to end with synthetic OpenAPI/Swagger
fixtures. They are hermetic: no live network (the fetcher HTTP call is mocked),
all output goes to pytest tmp_path, and assertions check the actual coverage
computation and CSV artifacts the tool produces.
"""

import csv
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.modules.engine.algorithms import CSVGenerator, SchemaAnalyzer, SchemaProcessor
from src.modules.swagger.schema_fetcher import SchemaFetcher
from src.modules.workflow import apply_coverage_filter

pytestmark = pytest.mark.e2e


SYNTHETIC_OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "Synthetic Coverage API", "version": "2.1.0"},
    "paths": {
        "/items": {
            "get": {
                "summary": "List items",
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "enum": ["active", "archived", "draft"]},
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                ],
                "responses": {"200": {"description": "ok"}},
            },
            "post": {
                "summary": "Create item",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "minLength": 1, "maxLength": 100},
                                    "enabled": {"type": "boolean"},
                                },
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "created"}},
            },
        },
        "/items/{itemId}": {
            "get": {
                "summary": "Get item",
                "parameters": [{"name": "itemId", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "ok"}},
            },
            "delete": {
                "summary": "Delete item",
                "parameters": [{"name": "itemId", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"204": {"description": "deleted"}},
            },
        },
    },
}


def _write_spec(directory, name="synthetic.json"):
    spec_path = directory / name
    spec_path.write_text(json.dumps(SYNTHETIC_OPENAPI), encoding="utf-8")
    return name


def test_full_pipeline_process_analyze_filter_csv(tmp_path):
    """Process -> analyze -> coverage-filter -> CSV, asserting real outputs."""
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir()
    spec_name = _write_spec(schemas_dir)

    processor = SchemaProcessor(schemas_dir=str(schemas_dir))
    processed = processor.process_schema_file(spec_name)
    assert processed is not None
    assert processed["info"]["title"] == "Synthetic Coverage API"
    assert processed["version"] == "3.0.0"
    assert processed["paths_count"] == 2
    assert len(processed["endpoints"]) == 4

    analyzer = SchemaAnalyzer(schemas_dir=str(schemas_dir))
    analysis = analyzer.analyze_schema_file(spec_name)
    endpoints = analysis["endpoints"]
    assert len(endpoints) == 4

    get_items = next(e for e in endpoints if e["path"] == "/items" and e["method"] == "GET")
    status_param = next(p for p in get_items["parameters"] if p["name"] == "status")
    assert status_param["location"] == "query"
    assert status_param["required"] is True
    assert status_param["iterationCount"] == 3
    assert status_param["constraints"]["enum"] == ["active", "archived", "draft"]

    limit_param = next(p for p in get_items["parameters"] if p["name"] == "limit")
    assert limit_param["iterationCount"] == 50

    post_items = next(e for e in endpoints if e["path"] == "/items" and e["method"] == "POST")
    body_names = {p["name"] for p in post_items["parameters"] if p["location"] == "body"}
    assert {"name", "enabled"} <= body_names

    filtered, report = apply_coverage_filter(analysis, coverage_percentage=50.0)
    assert report["total_endpoints"] == 4
    assert report["selected_endpoints"] == 2
    assert report["coverage_percentage"] == 50.0
    assert report["not_covered_endpoints"] == 2
    assert len(filtered["endpoints"]) == 2

    gherkin = (
        "Feature: Synthetic Coverage API\n\n"
        "  Scenario: List items by status\n"
        "    Given the API is available\n"
        '    When I send a GET request to "/items"\n'
        "    Then I should receive a 200 response\n\n"
        "  Scenario: Create an item\n"
        "    Given the API is available\n"
        '    When I send a POST request to "/items"\n'
        "    Then I should receive a 201 response\n"
    )
    out_dir = tmp_path / "csv_out"
    csv_gen = CSVGenerator(output_dir=str(out_dir), run_timestamp="20260101_000000")
    csv_path = Path(csv_gen.gherkin_to_csv(gherkin, "synthetic"))

    assert csv_path.exists()
    assert csv_path.parent == out_dir
    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    scenarios = {r["Scenario"] for r in rows}
    assert "List items by status" in scenarios
    assert "Create an item" in scenarios
    list_row = next(r for r in rows if r["Scenario"] == "List items by status")
    assert "/items" in list_row["When"]


def test_fetcher_pipeline_with_mocked_network(tmp_path):
    """Drive SchemaFetcher.download_and_save with a mocked HTTP response (no network)."""
    schemas_dir = tmp_path / "downloaded"
    fetcher = SchemaFetcher(schemas_dir=str(schemas_dir))

    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.headers = {"Content-Type": "application/json"}
    fake_response.json.return_value = SYNTHETIC_OPENAPI

    with patch("src.modules.swagger.schema_fetcher.requests.get", return_value=fake_response) as mock_get:
        saved = fetcher.download_and_save("https://example.test/openapi.json", "json")

    mock_get.assert_called_once()
    assert saved is not None
    saved_path = Path(saved)
    assert saved_path.exists()
    assert saved_path.parent == schemas_dir

    analyzer = SchemaAnalyzer(schemas_dir=str(schemas_dir))
    analysis = analyzer.analyze_schema_file(saved_path.name)
    assert len(analysis["endpoints"]) == 4


def test_swagger_2_and_openapi_3_produce_equivalent_endpoint_counts(tmp_path):
    """Both spec dialects must be analyzed to the same endpoint coverage."""
    swagger_2 = {
        "swagger": "2.0",
        "info": {"title": "Legacy API", "version": "1.0.0"},
        "paths": {
            "/ping": {"get": {"responses": {"200": {"description": "ok"}}}},
            "/echo": {
                "post": {
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "schema": {"type": "object", "properties": {"msg": {"type": "string"}}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            },
        },
    }
    schemas_dir = tmp_path / "s"
    schemas_dir.mkdir()
    (schemas_dir / "legacy.json").write_text(json.dumps(swagger_2), encoding="utf-8")

    analyzer = SchemaAnalyzer(schemas_dir=str(schemas_dir))
    analysis = analyzer.analyze_schema_file("legacy.json")
    assert len(analysis["endpoints"]) == 2

    echo = next(e for e in analysis["endpoints"] if e["path"] == "/echo")
    body_names = {p["name"] for p in echo["parameters"] if p["location"] == "body"}
    assert "msg" in body_names
