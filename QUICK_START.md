# Quick Start Guide

## Running the Project Manually

### 1. Basic Execution

```bash
# From project root
python main.py
```

The tool will guide you through:
1. Entering a Swagger/OpenAPI schema URL (or use default example)
2. Processing and analyzing the schema
3. Handling BRD (load existing, generate new, or parse from document)
4. Generating test scenarios
5. Exporting to CSV format

### 2. Running Tests

```bash
# Run regression test suite
python tests/scripts/run_regression_tests.py --coverage

# Run specific test category
python tests/scripts/run_regression_tests.py --unit
python tests/scripts/run_regression_tests.py --integration

# Run pytest directly
pytest -c tests/config/pytest.ini

# Run behave (BDD tests)
behave -c tests/config/behave.ini tests/features
```

### 3. Environment Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key:**
   - Create `.env` file in project root
   - Add: `LLM_API_KEY=your-llm-api-key-here`
   - The provider is auto-detected from key format (Groq: `gsk_...`, OpenAI: `sk-...`, etc.)
   - The tool will prompt you on first run if not set

### 4. Project Structure

```
api-param-coverage/
├── main.py                    # Main entry point
├── src/                       # Source code
├── tests/                     # All test-related files
│   ├── config/                # Test configuration
│   ├── scripts/               # Test runners
│   ├── docs/                  # Test documentation
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── ...
├── output/                    # Execution outputs
└── docs/                      # Project documentation
```

### 5. Common Commands

```bash
# Run main application
python main.py

# Run all tests with coverage
python tests/scripts/run_regression_tests.py --coverage

# Run quick tests (skip slow)
python tests/scripts/run_regression_tests.py --fast

# Run specific test file
pytest -c tests/config/pytest.ini tests/unit/swagger/test_schema_fetcher.py
```

## Troubleshooting

- **Import errors**: Make sure you're running from project root
- **Config not found**: Use `-c tests/config/pytest.ini` flag for pytest
- **API key issues**: Check `.env` file or set `OPENAI_API_KEY` environment variable

