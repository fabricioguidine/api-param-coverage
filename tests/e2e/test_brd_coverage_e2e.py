"""
End-to-end tests for BRD-driven coverage analysis.

These build a synthetic BRD plus matching schema analysis data and run the real
cross-reference / coverage-analysis code, asserting the computed coverage numbers.
Fully hermetic: outputs go to pytest tmp_path, no network, no LLM.
"""

import pytest

from src.modules.brd import BRDRequirement, BRDSchema, BRDTestScenario
from src.modules.brd.brd_schema import RequirementPriority
from src.modules.engine.coverage.coverage_analyzer import CoverageAnalyzer
from src.modules.workflow import apply_brd_filter, calculate_endpoint_priority

pytestmark = pytest.mark.e2e


def _analysis_data():
    return {
        "endpoints": [
            {"path": "/users", "method": "GET", "parameters": [{"name": "q", "required": True}]},
            {"path": "/users", "method": "POST", "parameters": [{"name": "body", "required": True}]},
            {"path": "/orders", "method": "GET", "parameters": []},
        ]
    }


def _brd():
    return BRDSchema(
        brd_id="BRD-1",
        title="Users BRD",
        description="Covers user endpoints only",
        api_name="Demo API",
        requirements=[
            BRDRequirement(
                requirement_id="REQ-1",
                title="List users",
                description="Users can be listed",
                endpoint_path="/users",
                endpoint_method="GET",
                priority=RequirementPriority.HIGH,
                test_scenarios=[
                    BRDTestScenario(
                        scenario_id="SC-1",
                        scenario_name="List users",
                        description="GET /users returns users",
                    )
                ],
            ),
            BRDRequirement(
                requirement_id="REQ-2",
                title="Create user",
                description="Users can be created",
                endpoint_path="/users",
                endpoint_method="POST",
                priority=RequirementPriority.CRITICAL,
                test_scenarios=[
                    BRDTestScenario(
                        scenario_id="SC-2",
                        scenario_name="Create user",
                        description="POST /users creates a user",
                    )
                ],
            ),
        ],
    )


def test_brd_filter_restricts_to_brd_endpoints(tmp_path):
    """apply_brd_filter must drop endpoints not described by the BRD."""
    analysis = _analysis_data()
    brd = _brd()

    filtered, report = apply_brd_filter(analysis, brd, run_output_dir=tmp_path, run_timestamp="20260101_000000")

    # /orders has no BRD requirement -> excluded.
    paths = {(e["path"], e["method"]) for e in filtered["endpoints"]}
    assert ("/orders", "GET") not in paths
    assert ("/users", "GET") in paths
    assert ("/users", "POST") in paths

    assert report["total_endpoints"] == 3
    assert report["covered_endpoints"] == 2
    assert report["not_covered_endpoints"] == 1
    assert report["coverage_percentage"] == pytest.approx(66.67, abs=0.01)


def test_coverage_analyzer_matches_gherkin_to_requirements(tmp_path):
    """CoverageAnalyzer must report full coverage when every requirement has a scenario."""
    brd = _brd()
    analysis = _analysis_data()

    gherkin = (
        "Feature: Users\n\n"
        "  Scenario: List users\n"
        '    When I send a GET request to "/users"\n'
        "    Then I get 200\n\n"
        "  Scenario: Create user\n"
        '    When I send a POST request to "/users"\n'
        "    Then I get 201\n"
    )

    analyzer = CoverageAnalyzer(run_output_dir=tmp_path, run_timestamp="20260101_000000")
    report = analyzer.analyze_coverage(gherkin, brd, analysis)

    assert report["total_requirements"] == 2
    assert report["total_scenarios"] == 2
    assert report["covered_requirements"] == 2
    assert report["uncovered_requirements"] == 0
    assert report["coverage_percentage"] == 100.0

    # Render the human-readable report into tmp_path and confirm it was written.
    out_path = tmp_path / "coverage_report.txt"
    written = analyzer.generate_coverage_report(report, output_path=out_path)
    assert written.exists()
    text = written.read_text(encoding="utf-8")
    assert "Coverage Percentage: 100.0%" in text


def test_coverage_analyzer_detects_gaps(tmp_path):
    """A requirement with no matching scenario must surface as a gap."""
    brd = _brd()
    analysis = _analysis_data()

    # Only the GET requirement has a scenario; POST is left uncovered.
    gherkin = (
        "Feature: Users\n\n" "  Scenario: List users\n" '    When I send a GET request to "/users"\n' "    Then I get 200\n"
    )

    analyzer = CoverageAnalyzer(run_output_dir=tmp_path, run_timestamp="20260101_000000")
    report = analyzer.analyze_coverage(gherkin, brd, analysis)

    assert report["covered_requirements"] == 1
    assert report["uncovered_requirements"] == 1
    assert report["coverage_percentage"] == 50.0
    gap_reqs = {g["requirement_id"] for g in report["coverage_gaps"]}
    assert "REQ-2" in gap_reqs


def test_endpoint_priority_orders_by_method_and_params():
    """Higher-impact endpoints must score above trivial ones (drives coverage selection)."""
    post_ep = {"method": "POST", "parameters": [{"required": True}, {"required": True}]}
    get_ep = {"method": "GET", "parameters": []}
    assert calculate_endpoint_priority(post_ep) > calculate_endpoint_priority(get_ep)
