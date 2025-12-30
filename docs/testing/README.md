# Testing Framework Documentation

This directory contains comprehensive testing strategy and documentation for the API Parameter Coverage tool.

## Files

- **test_strategy.md**: Complete test strategy with 525+ test cases
- **test_coverage_matrix.csv**: Detailed tracking matrix for all tests
- **test_architecture_diagram.md**: Technical architecture and test flow
- **test_strategy_diagram.html**: Interactive visual diagram

## Quick Start

See the main [README.md](../../README.md) for testing instructions.

## Test Structure

```
tests/
├── unit/              # Unit tests (350+ tests, 95% coverage target)
├── integration/       # Integration tests (100 tests, 90% coverage target)
├── e2e/              # E2E tests (30 scenarios, 100% critical paths)
├── performance/       # Performance benchmarks (20 tests)
├── security/          # Security tests (10 tests, 100% coverage)
└── fixtures/          # Test fixtures and mocks
```

## Running Tests

```bash
# Run all tests
python tests/scripts/run_regression_tests.py

# Run with coverage
python tests/scripts/run_regression_tests.py --coverage

# Run specific category
python tests/scripts/run_regression_tests.py --category unit
```

## Coverage Goals

- **Overall**: 95%+ coverage
- **Critical Modules**: 95%+ (swagger, engine/algorithms, brd)
- **High Priority**: 90%+ (engine/llm, brd_generator)
- **Medium Priority**: 85%+ (engine/analytics, cli)

