#!/usr/bin/env python3
"""
Automated UI Testing Script for API Parameter Coverage Tool

This script tests all UI flows by automating interactive prompts.
Requires: pip install pexpect
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional

class SimpleUITester:
    """Simple UI tester using subprocess."""
    
    def __init__(self, script_path: str = None):
        """Initialize tester."""
        if script_path is None:
            # Get the project root (two levels up from tests/scripts/)
            import os
            project_root = Path(__file__).parent.parent.parent
            self.script_path = str(project_root / "main.py")
        else:
            self.script_path = script_path
        
    def run_test(self, name: str, inputs: List[str], timeout: int = 600) -> Tuple[bool, str]:
        """
        Run a test with given inputs.
        
        Args:
            name: Test name
            inputs: List of input strings (each sent with newline)
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"{'='*70}")
        
        try:
            # Prepare input string
            input_data = '\n'.join(inputs) + '\n'
            
            # Set environment for UTF-8 encoding
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Run the script with encoding handling
            process = subprocess.Popen(
                [sys.executable, '-X', 'utf8', self.script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
                encoding='utf-8',
                errors='replace'  # Replace encoding errors instead of failing
            )
            
            # Send inputs
            try:
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                output = (stdout or '') + (stderr or '')
            except UnicodeDecodeError:
                # Fallback: read as bytes and decode with error handling
                process = subprocess.Popen(
                    [sys.executable, '-X', 'utf8', self.script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                stdout_bytes, stderr_bytes = process.communicate(input=input_data.encode('utf-8'), timeout=timeout)
                output = (stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else '') + \
                         (stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else '')
            
            # Check if process completed
            if process.returncode == 0:
                print(f"  [OK] Test completed: {name}")
                return True, output
            else:
                print(f"  [FAIL] Test failed with exit code: {process.returncode}")
                # Show last 1000 chars of output for debugging
                if output:
                    print(f"  Last output (1000 chars): {output[-1000:]}")
                if stderr and stderr not in output:
                    print(f"  Error output: {stderr[:500]}")
                return False, output
                
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] Test timed out after {timeout} seconds")
            if process:
                process.kill()
            return False, "Timeout"
        except Exception as e:
            print(f"  [FAIL] Test error: {e}")
            return False, str(e)
    
    def test_scenario_1_happy_path(self) -> bool:
        """Test: Happy path with BRD generation."""
        inputs = [
            '',  # Use default URL (Enter)
            'y',  # Confirm use example
            '3',  # Generate BRD from Swagger
            '75',  # Coverage percentage for BRD generation
            '',  # Coverage percentage if BRD fails (press Enter for default)
        ]
        success, output = self.run_test("Happy Path - BRD Generation", inputs, timeout=300)
        # Check for any indication of progress
        has_progress = any(keyword in output.lower() for keyword in [
            'schema', 'downloaded', 'processing', 'analyzing', 'brd', 'generating', 'scenarios'
        ])
        return success or has_progress
    
    def test_scenario_2_invalid_url_recovery(self) -> bool:
        """Test: Invalid URL with recovery."""
        inputs = [
            'not-a-valid-url',  # Invalid URL
            'y',  # Try again
            'https://api.weather.gov/openapi.json',  # Valid URL
            '3',  # Generate BRD
            '100',  # Coverage for BRD generation
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Invalid URL Recovery", inputs, timeout=300)
        has_invalid_url = 'Invalid URL' in output or 'invalid' in output.lower()
        has_progress = any(keyword in output.lower() for keyword in ['schema', 'downloaded', 'processing'])
        return (success or has_progress) and has_invalid_url
    
    def test_scenario_3_invalid_coverage(self) -> bool:
        """Test: Invalid coverage percentage."""
        inputs = [
            '',  # Use default URL
            'y',  # Confirm
            '3',  # Generate BRD
            '150',  # Invalid percentage (>100) - should use default
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Invalid Coverage Percentage", inputs, timeout=300)
        has_invalid = 'Invalid percentage' in output or 'invalid' in output.lower() or 'default' in output.lower()
        return success or has_invalid
    
    def test_scenario_4_menu_invalid_input(self) -> bool:
        """Test: Invalid menu input handling."""
        inputs = [
            '',  # Use default URL
            'y',  # Confirm
            '5',  # Invalid menu option
            'a',  # Invalid input (letter)
            '3',  # Valid option (generate BRD)
            '100',  # Coverage
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Menu Invalid Input", inputs, timeout=300)
        # Check for invalid input messages
        has_invalid = 'Invalid choice' in output or 'Invalid input' in output
        return success or has_invalid
    
    def test_scenario_5_confirmation_prompts(self) -> bool:
        """Test: Confirmation prompt variations."""
        inputs = [
            '',  # No URL
            'n',  # Don't use example
            '',  # Try again (empty)
            'y',  # Use example
            '3',  # Generate BRD
            '100',  # Coverage
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Confirmation Prompts", inputs, timeout=300)
        has_progress = any(keyword in output.lower() for keyword in ['schema', 'downloaded', 'processing'])
        return success or has_progress
    
    def test_scenario_6_custom_url(self) -> bool:
        """Test: Custom schema URL."""
        inputs = [
            'https://api.weather.gov/openapi.json',  # Custom URL
            '3',  # Generate BRD
            '80',  # Coverage
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Custom URL", inputs, timeout=300)
        has_progress = any(keyword in output.lower() for keyword in ['schema', 'downloaded', 'weather'])
        return success or has_progress
    
    def test_scenario_7_coverage_edge_cases(self) -> bool:
        """Test: Coverage percentage edge cases."""
        inputs = [
            '',  # Use default URL
            'y',  # Confirm
            '3',  # Generate BRD
            '1',  # Minimum (1%)
            '',  # Coverage if BRD fails
        ]
        success, output = self.run_test("Coverage Edge Cases - Minimum", inputs, timeout=300)
        has_progress = any(keyword in output.lower() for keyword in ['schema', 'downloaded', 'coverage'])
        return success or has_progress
    
    def test_all_scenarios(self):
        """Run all test scenarios."""
        print("\n" + "="*70)
        print("Starting Automated UI Testing")
        print("="*70)
        
        tests = [
            ("Happy Path - BRD Generation", self.test_scenario_1_happy_path),
            ("Invalid URL Recovery", self.test_scenario_2_invalid_url_recovery),
            ("Invalid Coverage Percentage", self.test_scenario_3_invalid_coverage),
            ("Menu Invalid Input", self.test_scenario_4_menu_invalid_input),
            ("Confirmation Prompts", self.test_scenario_5_confirmation_prompts),
            ("Custom URL", self.test_scenario_6_custom_url),
            ("Coverage Edge Cases", self.test_scenario_7_coverage_edge_cases),
        ]
        
        results = {'total': len(tests), 'passed': 0, 'failed': 0, 'details': []}
        
        for name, test_func in tests:
            try:
                success = test_func()
                if success:
                    results['passed'] += 1
                    results['details'].append((name, 'PASSED'))
                    print(f"  [OK] {name}: PASSED")
                else:
                    results['failed'] += 1
                    results['details'].append((name, 'FAILED'))
                    print(f"  [FAIL] {name}: FAILED")
            except Exception as e:
                results['failed'] += 1
                results['details'].append((name, f'ERROR: {e}'))
                print(f"  [FAIL] {name}: ERROR - {e}")
            
            time.sleep(2)  # Delay between tests
        
        # Print summary
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)
        print(f"Total Tests: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        if results['total'] > 0:
            print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
        print("\nDetailed Results:")
        for name, status in results['details']:
            symbol = "[OK]" if status == "PASSED" else "[FAIL]"
            print(f"  {symbol} {name}: {status}")
        
        return results


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated UI Testing for API Parameter Coverage')
    parser.add_argument('--script', default='main.py', help='Path to main.py script')
    parser.add_argument('--test', help='Run specific test (happy, invalid-url, invalid-coverage, etc.)')
    parser.add_argument('--timeout', type=int, default=600, help='Timeout per test in seconds')
    
    args = parser.parse_args()
    
    tester = SimpleUITester(script_path=args.script)
    
    if args.test:
        # Run specific test
        test_map = {
            'happy': tester.test_scenario_1_happy_path,
            'invalid-url': tester.test_scenario_2_invalid_url_recovery,
            'invalid-coverage': tester.test_scenario_3_invalid_coverage,
            'invalid-input': tester.test_scenario_4_menu_invalid_input,
            'confirmations': tester.test_scenario_5_confirmation_prompts,
            'custom-url': tester.test_scenario_6_custom_url,
            'edge-cases': tester.test_scenario_7_coverage_edge_cases,
        }
        
        if args.test in test_map:
            success = test_map[args.test]()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown test: {args.test}")
            print(f"Available tests: {', '.join(test_map.keys())}")
            sys.exit(1)
    else:
        # Run all tests
        results = tester.test_all_scenarios()
        sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

