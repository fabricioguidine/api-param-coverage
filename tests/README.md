# Tests Module

Comprehensive testing framework for the API Parameter Coverage tool.

## Structure

```
tests/
├── config/                                    # Test configuration files
│   ├── pytest.ini                             # Pytest configuration
│   └── behave.ini                             # Behave (BDD) configuration
├── scripts/                                   # Test runner scripts
│   └── run_regression_tests.py                # Regression test runner
├── docs/                                      # Test documentation
│   └── TESTING_GUIDE.md                       # Quick testing reference
├── unit/                                      # Unit tests (individual components)
├── integration/                               # Integration tests (module interactions)
├── e2e/                                       # E2E test structure
├── performance/                               # Performance benchmarks
├── security/                                  # Security tests
├── fixtures/                                  # Shared fixtures and mocks
├── features/                                  # BDD scenarios (Behave)
├── output/                                    # Test execution outputs
└── conftest.py                                # Pytest configuration and fixtures
```

## Running Tests

### Using the Regression Test Runner

```bash
# From project root
python tests/scripts/run_regression_tests.py

# Run specific categories
python tests/scripts/run_regression_tests.py --unit
python tests/scripts/run_regression_tests.py --integration
python tests/scripts/run_regression_tests.py --coverage
```

### Using Pytest Directly

```bash
# Run all tests
pytest -c tests/config/pytest.ini

# Run specific category
pytest -c tests/config/pytest.ini tests/unit -m unit
pytest -c tests/config/pytest.ini tests/integration -m integration
```

### Using Behave for E2E Tests

```bash
# Run all BDD scenarios
behave -c tests/config/behave.ini tests/features

# Run specific feature
behave -c tests/config/behave.ini tests/features/main_workflow.feature
```

## Configuration

- **pytest.ini**: Located in `tests/config/`, contains pytest settings, markers, and coverage configuration
- **behave.ini**: Located in `tests/config/`, contains Behave settings for BDD tests

## Test Categories

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test module interactions
3. **E2E Tests** (`tests/features/`): Complete user workflows (BDD)
4. **Performance Tests** (`tests/performance/`): Benchmarks and load tests
5. **Security Tests** (`tests/security/`): Input validation and security tests

## Documentation

- **Quick Guide**: `tests/docs/TESTING_GUIDE.md`
- **Comprehensive Strategy**: `docs/testing/test_strategy.md` (500+ test cases)
- **Coverage Matrix**: `docs/testing/test_coverage_matrix.csv`

## Test Coverage

Target: **95%+ code coverage** for critical modules

- Critical modules (swagger, engine/algorithms, brd): 95%+
- High priority (engine/llm, brd_generator): 90%+
- Medium priority (engine/analytics, cli): 85%+

## Writing Tests

See `tests/docs/TESTING_GUIDE.md` for guidelines on writing new tests.


