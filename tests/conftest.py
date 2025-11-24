"""
Pytest configuration and fixtures for test result saving.
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
    """Hook to capture test results and save them to a file."""
    global _session_timestamp, _session_output_dir, _test_results
    
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    
    # Only save results for actual test calls (not setup/teardown)
    if rep.when == "call":
        # Get test suite name
        test_suite_name = _get_test_suite_name(item)
        
        # Prepare test result content
        test_result = {
            "name": item.name,
            "file": str(item.fspath),
            "status": rep.outcome.upper(),
            "timestamp": datetime.now().isoformat(),
            "longrepr": str(rep.longrepr) if rep.longrepr else None
        }
        
        # Store result grouped by test suite
        _test_results[test_suite_name].append(test_result)


@pytest.fixture(scope="session", autouse=True)
def save_test_results(request):
    """Save test results grouped by test suite to timestamped files."""
    global _session_timestamp, _session_output_dir, _test_results
    
    def finalize():
        if not _session_output_dir or not _session_timestamp:
            return
        
        # Save results for each test suite
        for test_suite_name, results in _test_results.items():
            filename = f"{_session_timestamp}_{test_suite_name}.txt"
            filepath = _session_output_dir / filename
            
            content_lines = []
            content_lines.append("=" * 80)
            content_lines.append(f"Test Suite: {test_suite_name}")
            content_lines.append("=" * 80)
            content_lines.append("")
            content_lines.append(f"Timestamp: {_session_timestamp}")
            content_lines.append(f"Total Tests: {len(results)}")
            content_lines.append("")
            
            # Count statuses
            passed = sum(1 for r in results if r["status"] == "PASSED")
            failed = sum(1 for r in results if r["status"] == "FAILED")
            skipped = sum(1 for r in results if r["status"] == "SKIPPED")
            
            content_lines.append("Summary:")
            content_lines.append(f"  - Passed: {passed}")
            content_lines.append(f"  - Failed: {failed}")
            content_lines.append(f"  - Skipped: {skipped}")
            content_lines.append("")
            content_lines.append("=" * 80)
            content_lines.append("")
            
            # Individual test results
            for result in results:
                content_lines.append("-" * 80)
                content_lines.append(f"Test: {result['name']}")
                content_lines.append(f"Status: {result['status']}")
                content_lines.append(f"Timestamp: {result['timestamp']}")
                
                if result["status"] == "FAILED" and result["longrepr"]:
                    content_lines.append("")
                    content_lines.append("Error Details:")
                    content_lines.append(result["longrepr"])
                elif result["status"] == "SKIPPED" and result["longrepr"]:
                    content_lines.append("")
                    content_lines.append("Skip Reason:")
                    content_lines.append(result["longrepr"])
                
                content_lines.append("")
            
            content_lines.append("=" * 80)
            
            # Write to file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("\n".join(content_lines))
            except Exception as e:
                print(f"Warning: Could not save test results to {filepath}: {e}", file=sys.stderr)
        
        # Save session summary
        session = request.session
        # Calculate totals from collected results
        total = sum(len(suite) for suite in _test_results.values())
        failed_count = sum(1 for suite in _test_results.values() for r in suite if r["status"] == "FAILED")
        skipped_count = sum(1 for suite in _test_results.values() for r in suite if r["status"] == "SKIPPED")
        passed = total - failed_count - skipped_count
        failed = failed_count
        skipped = skipped_count
        
        summary_file = _session_output_dir / f"{_session_timestamp}_test_session_summary.txt"
        
        content_lines = []
        content_lines.append("=" * 80)
        content_lines.append("Test Session Summary")
        content_lines.append("=" * 80)
        content_lines.append("")
        content_lines.append(f"Timestamp: {_session_timestamp}")
        content_lines.append(f"Total Tests: {total}")
        content_lines.append(f"Passed: {passed}")
        content_lines.append(f"Failed: {failed}")
        content_lines.append(f"Skipped: {skipped}")
        content_lines.append("")
        content_lines.append(f"Test Suites Run: {len(_test_results)}")
        for suite_name in sorted(_test_results.keys()):
            suite_results = _test_results[suite_name]
            suite_passed = sum(1 for r in suite_results if r["status"] == "PASSED")
            suite_failed = sum(1 for r in suite_results if r["status"] == "FAILED")
            suite_skipped = sum(1 for r in suite_results if r["status"] == "SKIPPED")
            content_lines.append(f"  - {suite_name}: {len(suite_results)} tests ({suite_passed} passed, {suite_failed} failed, {suite_skipped} skipped)")
        content_lines.append("")
        content_lines.append("=" * 80)
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content_lines))
        except Exception as e:
            print(f"Warning: Could not save test session summary: {e}", file=sys.stderr)
    
    request.addfinalizer(finalize)

