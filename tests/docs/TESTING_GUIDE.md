# Testing Guide

## Quick Start

Run the comprehensive regression test suite:

```bash
python tests/scripts/run_regression_tests.py --coverage
```

## Test Categories

### 1. Unit Tests
Test individual components in isolation.

```bash
pytest tests/unit -m unit
```

**Location**: `tests/unit/`
**Target**: 95%+ coverage for critical modules

### 2. Integration Tests
Test module interactions and data flow.

```bash
pytest tests/integration -m integration
```

**Location**: `tests/integration/`
**Target**: 90%+ coverage for critical paths

### 3. E2E Tests
Test complete user workflows using BDD.

```bash
behave tests/features
```

**Location**: `tests/features/`
**Target**: 100% coverage for critical workflows

### 4. Performance Tests
Benchmark processing speed and resource usage.

```bash
pytest tests/performance -m performance
```

**Location**: `tests/performance/`
**Target**: Meet performance benchmarks

### 5. Security Tests
Test input validation and security.

```bash
pytest tests/security -m security
```

**Location**: `tests/security/`
**Target**: 100% coverage for security-critical paths

## Regression Testing

The regression test runner executes all test categories:

```bash
# Full suite with coverage
python tests/scripts/run_regression_tests.py --coverage

# Only unit tests
python tests/scripts/run_regression_tests.py --unit

# Skip slow tests
python tests/scripts/run_regression_tests.py --fast

# Specific category
python tests/scripts/run_regression_tests.py --category integration
```

## Coverage Reports

Generate and view coverage reports:

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# View report
# Windows: start htmlcov/index.html
# Mac/Linux: open htmlcov/index.html
```

## Test Metrics

Test execution metrics are saved to `tests/output/<timestamp>/`:
- Overall test results
- Per-category metrics
- Per-suite metrics
- Failed test details

## Writing Tests

### Unit Test Example

```python
import pytest
from src.modules.your_module import YourClass

@pytest.mark.unit
class TestYourClass:
    def test_your_method(self):
        instance = YourClass()
        result = instance.your_method()
        assert result is not None
```

### Integration Test Example

```python
import pytest
from src.modules.module_a import ClassA
from src.modules.module_b import ClassB

@pytest.mark.integration
class TestModuleIntegration:
    def test_module_interaction(self):
        a = ClassA()
        b = ClassB()
        result = b.process(a.get_data())
        assert result is not None
```

## Test Fixtures

Use shared fixtures from `tests/fixtures/`:

```python
from tests.fixtures.schemas import MINIMAL_SWAGGER_2
from tests.fixtures.mocks import mock_openai_response

def test_with_fixture(mock_openai_response):
    # Use fixture
    pass
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines. See `docs/testing/test_strategy.md` for CI configuration.

## Documentation

- **Test Strategy**: `docs/testing/test_strategy.md`
- **Coverage Matrix**: `docs/testing/test_coverage_matrix.csv`
- **Architecture**: `docs/testing/test_architecture_diagram.md`
- **Visual Diagram**: `docs/testing/test_strategy_diagram.html`

