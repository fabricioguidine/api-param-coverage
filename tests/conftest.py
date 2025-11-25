"""
Pytest configuration and fixtures for test metrics collection.
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys
from collections import defaultdict


# Session-level timestamp and output directory
_session_timestamp = None
_session_output_dir = None
_test_results = defaultdict(list)  # Group by test suite (file)
_test_timings = {}  # Track test execution times


@pytest.fixture(scope="session", autouse=True)
def setup_test_output_dir(request):
    """Create timestamped output directory for the test session."""
    global _session_timestamp, _session_output_dir
    
    # Generate timestamp once per session
    _session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create timestamp folder
    base_output_dir = Path("tests/output")
    base_output_dir.mkdir(parents=True, exist_ok=True)
    _session_output_dir = base_output_dir / _session_timestamp
    _session_output_dir.mkdir(parents=True, exist_ok=True)
    
    return _session_output_dir


def _get_test_suite_name(item):
    """Extract test suite name from test item (test file name without extension)."""
    test_file = Path(item.fspath)
    return test_file.stem  # filename without extension


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and metrics."""
    global _session_timestamp, _session_output_dir, _test_results, _test_timings
    
    # Track start time
    if call.when == "setup":
        _test_timings[item.nodeid] = {"start": datetime.now()}
    
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    
    # Track end time and calculate duration
    if call.when == "teardown":
        if item.nodeid in _test_timings:
            _test_timings[item.nodeid]["end"] = datetime.now()
            start = _test_timings[item.nodeid]["start"]
            end = _test_timings[item.nodeid]["end"]
            _test_timings[item.nodeid]["duration"] = (end - start).total_seconds()
    
    # Only save results for actual test calls (not setup/teardown)
    if rep.when == "call":
        # Get test suite name
        test_suite_name = _get_test_suite_name(item)
        
        # Get duration if available
        duration = _test_timings.get(item.nodeid, {}).get("duration", 0.0)
        
        # Prepare test result content
        test_result = {
            "name": item.name,
            "suite": test_suite_name,
            "file": str(item.fspath),
            "status": rep.outcome.upper(),
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "longrepr": str(rep.longrepr) if rep.longrepr else None
        }
        
        # Store result grouped by test suite
        _test_results[test_suite_name].append(test_result)


@pytest.fixture(scope="session", autouse=True)
def save_test_metrics(request):
    """Save all test metrics to a single file per session."""
    global _session_timestamp, _session_output_dir, _test_results
    
    def finalize():
        if not _session_output_dir or not _session_timestamp:
            return
        
        # Calculate overall metrics
        all_results = []
        for suite_results in _test_results.values():
            all_results.extend(suite_results)
        
        total = len(all_results)
        passed = sum(1 for r in all_results if r["status"] == "PASSED")
        failed = sum(1 for r in all_results if r["status"] == "FAILED")
        skipped = sum(1 for r in all_results if r["status"] == "SKIPPED")
        total_duration = sum(r["duration"] for r in all_results)
        avg_duration = total_duration / total if total > 0 else 0.0
        
        # Calculate per-suite metrics
        suite_metrics = {}
        for suite_name, results in _test_results.items():
            suite_passed = sum(1 for r in results if r["status"] == "PASSED")
            suite_failed = sum(1 for r in results if r["status"] == "FAILED")
            suite_skipped = sum(1 for r in results if r["status"] == "SKIPPED")
            suite_duration = sum(r["duration"] for r in results)
            suite_avg_duration = suite_duration / len(results) if results else 0.0
            suite_pass_rate = (suite_passed / len(results) * 100) if results else 0.0
            
            suite_metrics[suite_name] = {
                "total": len(results),
                "passed": suite_passed,
                "failed": suite_failed,
                "skipped": suite_skipped,
                "duration": suite_duration,
                "avg_duration": suite_avg_duration,
                "pass_rate": suite_pass_rate
            }
        
        # Create single metrics file
        metrics_file = _session_output_dir / f"{_session_timestamp}_test_metrics.txt"
        
        content_lines = []
        content_lines.append("=" * 80)
        content_lines.append("Test Execution Metrics")
        content_lines.append("=" * 80)
        content_lines.append("")
        content_lines.append(f"Session Timestamp: {_session_timestamp}")
        content_lines.append(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_lines.append("")
        
        # Overall Metrics
        content_lines.append("-" * 80)
        content_lines.append("Overall Metrics")
        content_lines.append("-" * 80)
        content_lines.append(f"Total Tests: {total}")
        content_lines.append(f"Passed: {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
        content_lines.append(f"Failed: {failed} ({failed/total*100:.1f}%)" if total > 0 else "Failed: 0")
        content_lines.append(f"Skipped: {skipped} ({skipped/total*100:.1f}%)" if total > 0 else "Skipped: 0")
        content_lines.append(f"Total Duration: {total_duration:.2f}s")
        content_lines.append(f"Average Duration: {avg_duration:.3f}s")
        content_lines.append(f"Test Suites: {len(_test_results)}")
        content_lines.append("")
        
        # Per-Suite Metrics
        content_lines.append("-" * 80)
        content_lines.append("Per-Suite Metrics")
        content_lines.append("-" * 80)
        for suite_name in sorted(suite_metrics.keys()):
            metrics = suite_metrics[suite_name]
            content_lines.append(f"Suite: {suite_name}")
            content_lines.append(f"  Tests: {metrics['total']} | Passed: {metrics['passed']} | Failed: {metrics['failed']} | Skipped: {metrics['skipped']}")
            content_lines.append(f"  Pass Rate: {metrics['pass_rate']:.1f}%")
            content_lines.append(f"  Duration: {metrics['duration']:.2f}s (avg: {metrics['avg_duration']:.3f}s)")
            content_lines.append("")
        
        # Failed Tests Summary
        failed_tests = [r for r in all_results if r["status"] == "FAILED"]
        if failed_tests:
            content_lines.append("-" * 80)
            content_lines.append("Failed Tests")
            content_lines.append("-" * 80)
            for test in failed_tests:
                content_lines.append(f"  - {test['suite']}::{test['name']}")
                if test["longrepr"]:
                    # Truncate long error messages
                    error_msg = test["longrepr"][:500] + "..." if len(test["longrepr"]) > 500 else test["longrepr"]
                    content_lines.append(f"    Error: {error_msg.split(chr(10))[0]}")
            content_lines.append("")
        
        content_lines.append("=" * 80)
        
        # Write to single file
        try:
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content_lines))
        except Exception as e:
            print(f"Warning: Could not save test metrics to {metrics_file}: {e}", file=sys.stderr)
    
    request.addfinalizer(finalize)

