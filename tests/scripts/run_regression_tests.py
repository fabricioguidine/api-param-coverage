#!/usr/bin/env python3
"""
Regression Test Runner

Comprehensive test suite runner for API Parameter Coverage tool.
Runs all test categories and generates coverage reports.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description, env=None):
    """Run a command and return success status."""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=False, env=env)
    return result.returncode == 0


def main():
    """Main regression test runner."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive regression test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_regression_tests.py

  # Run only unit tests
  python run_regression_tests.py --unit

  # Run with coverage report
  python run_regression_tests.py --coverage

  # Run specific category
  python run_regression_tests.py --category integration
        """,
    )

    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only E2E tests (Behave)")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("--security", action="store_true", help="Run only security tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "e2e", "performance", "security"],
        help="Run tests from specific category",
    )
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("=" * 70)
    print("API Parameter Coverage - Regression Test Suite")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    all_passed = True
    test_results = {}

    # Get project root (parent of tests/)
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"
    pytest_config = project_root / "tests" / "config" / "pytest.ini"

    # Determine what to run
    run_all = not any([args.unit, args.integration, args.e2e, args.performance, args.security, args.category])

    # Build pytest command with config
    pytest_cmd = ["pytest", "-c", str(pytest_config)] if pytest_config.exists() else ["pytest"]

    if args.verbose:
        pytest_cmd.append("-vv")

    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])

    if args.coverage:
        pytest_cmd.extend(["--cov=src", "--cov-report=html:htmlcov", "--cov-report=term-missing"])

    # Run specific categories
    if args.unit or (run_all and not args.category):
        print("\n[1/5] Running Unit Tests...")
        cmd = [*pytest_cmd, str(tests_dir / "unit"), "-m", "unit"]
        success = run_command(cmd, "Unit Tests")
        test_results["unit"] = success
        all_passed = all_passed and success

    if args.integration or (run_all and not args.category):
        print("\n[2/5] Running Integration Tests...")
        cmd = [*pytest_cmd, str(tests_dir / "integration"), "-m", "integration"]
        success = run_command(cmd, "Integration Tests")
        test_results["integration"] = success
        all_passed = all_passed and success

    if args.e2e or (run_all and not args.category):
        print("\n[3/5] Running E2E Tests (Behave)...")
        # Set UTF-8 encoding for Windows compatibility
        import os

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        # Run only core E2E tests (exclude UI/UX tests with undefined steps for now)
        core_features = [
            str(tests_dir / "features" / "brd_workflow.feature"),
            str(tests_dir / "features" / "main_workflow.feature"),
            str(tests_dir / "features" / "schema_processing.feature"),
        ]
        cmd = ["behave", *core_features, "--format", "pretty"]
        # Use behave config if available (behave uses --define or environment variable)
        behave_config = project_root / "tests" / "config" / "behave.ini"
        if behave_config.exists():
            # Change to config directory so behave.ini is found automatically
            original_cwd = os.getcwd()
            os.chdir(str(behave_config.parent))
            try:
                success = run_command(cmd, "E2E Tests (Behave)", env)
            finally:
                os.chdir(original_cwd)
        else:
            success = run_command(cmd, "E2E Tests (Behave)", env)
        test_results["e2e"] = success
        all_passed = all_passed and success

    if args.performance or (run_all and not args.category):
        print("\n[4/5] Running Performance Tests...")
        cmd = [*pytest_cmd, str(tests_dir / "performance"), "-m", "performance"]
        success = run_command(cmd, "Performance Tests")
        test_results["performance"] = success
        all_passed = all_passed and success

    if args.security or (run_all and not args.category):
        print("\n[5/5] Running Security Tests...")
        cmd = [*pytest_cmd, str(tests_dir / "security"), "-m", "security"]
        success = run_command(cmd, "Security Tests")
        test_results["security"] = success
        all_passed = all_passed and success

    # Handle specific category
    if args.category:
        category_map = {
            "unit": (tests_dir / "unit", "unit"),
            "integration": (tests_dir / "integration", "integration"),
            "e2e": (tests_dir / "features", None),
            "performance": (tests_dir / "performance", "performance"),
            "security": (tests_dir / "security", "security"),
        }

        if args.category == "e2e":
            cmd = ["behave", str(tests_dir / "features"), "--format", "pretty"]
        else:
            path, marker = category_map[args.category]
            cmd = [*pytest_cmd, str(path), "-m", marker]

        success = run_command(cmd, f"{args.category.upper()} Tests")
        test_results[args.category] = success
        all_passed = all_passed and success

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    for category, passed in test_results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {category.upper()}")

    print()
    if all_passed:
        print("[OK] All tests passed!")
        if args.coverage:
            print("\nCoverage report generated in htmlcov/index.html")
    else:
        print("[FAIL] Some tests failed. Check output above for details.")
        sys.exit(1)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
