# API Parameter Coverage & Test Scenario Generator

[![CI](https://github.com/fabricioguidine/api-param-coverage/actions/workflows/ci.yml/badge.svg)](https://github.com/fabricioguidine/api-param-coverage/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/fabricioguidine/api-param-coverage/branch/main/graph/badge.svg)](https://codecov.io/gh/fabricioguidine/api-param-coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
![Tests](https://img.shields.io/badge/tests-224%20tests-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-80%25+-green.svg)
![Swagger](https://img.shields.io/badge/Swagger-2.0-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

A comprehensive Python tool for generating test scenarios from OpenAPI/Swagger schemas using LLM-powered analysis and Business Requirement Document (BRD) integration. The tool automatically analyzes API schemas, cross-references them with business requirements, and generates comprehensive Gherkin test scenarios with detailed analytics.

## 🚀 Features

### Core Capabilities
- 🔄 **Multi-Format Schema Support**: Handles Swagger 2.0, OpenAPI 3.0, and OpenAPI 3.1 (JSON/YAML)
- 📥 **Automatic Schema Download**: Fetches schemas from URLs with validation
- 🔍 **Deep Schema Analysis**: Extracts parameters, constraints, and complexity metrics
- 📋 **BRD Integration**: Business Requirement Document support for scope-based testing
- 🤖 **LLM-Powered Generation**: Uses multiple LLM providers (OpenAI, Groq, Anthropic, Google, Azure) for intelligent test scenario generation
- 🎯 **Smart Scope Filtering**: Cross-references BRD with Swagger to test only required endpoints
- 📊 **CSV Export**: Export test scenarios to CSV format
- 📈 **Comprehensive Analytics**: Detailed metrics and reports for every algorithm execution

### Advanced Features
- 📦 **Smart Chunking**: Automatically handles large schemas by processing in chunks
- 🔄 **BRD Generation**: Creates BRD documents from Swagger schemas using heuristic analysis
- 📄 **Document Parsing**: Converts BRD documents (PDF, Word, TXT, CSV) to structured schemas
- 📊 **Algorithm Tracking**: Detailed complexity analysis for each algorithm execution
- ⚡ **Performance Monitoring**: Execution time and resource usage tracking
- 🎨 **Structured Reports**: Separate analytics reports for each algorithm and LLM call
- 📈 **Coverage Analysis**: Analyzes test coverage against BRD requirements
- 📊 **Analytics Dashboard**: Aggregates analytics across runs with trend analysis
- ⚙️ **Configuration Management**: YAML/JSON config files with environment-specific settings

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Modules Overview](#modules-overview)
- [BRD System](#brd-system)
- [Analytics & Reporting](#analytics--reporting)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 💻 Installation

### Prerequisites

- Python 3.9 or higher (tested on 3.9–3.13)
- Runs on Linux, macOS, and Windows
- LLM API key (supports OpenAI, Groq, Anthropic, Google, Azure - auto-detected from key format)
- Internet connection (for schema downloading)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api-param-coverage
   ```

2. **Create a virtual environment**

   Linux / macOS:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # For development (tests, linters, type checking):
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   LLM_API_KEY=your-llm-api-key-here
   ```
   
   The provider is automatically detected from your API key format:
   - **Groq**: `gsk_...` → Uses `llama-3.1-70b-versatile`
   - **OpenAI**: `sk-...` → Uses `gpt-4`
   - **Anthropic**: `sk-ant-...` → Uses `claude-3-sonnet`
   - **Google**: `AIza...` → Uses `gemini-pro`
   - **Azure**: `api-...` → Uses `gpt-4`
   
   **⚠️ Important**: Never commit your API key. The `.env` file is already in `.gitignore`.

5. **Optional: Install document parsing dependencies**
   
   For BRD document parsing (PDF, Word):
   ```bash
   pip install PyPDF2 python-docx
   ```

## 🚀 Quick Start

```bash
python main.py
```

The tool will guide you through:
1. Entering a Swagger/OpenAPI schema URL
2. Processing and analyzing the schema
3. Handling BRD (load existing, generate new, or parse from document)
4. Generating test scenarios
5. Exporting to CSV format

## 📖 Usage Guide

### Basic Workflow

1. **Schema Input**: Provide a Swagger/OpenAPI schema URL (or press Enter to use the default example: `https://api.weather.gov/openapi.json`)
2. **Schema Processing**: The tool downloads, validates, and processes the schema
3. **BRD Handling**: Choose one of three options:
   - **Load Existing BRD**: Select from saved BRD schema files
   - **Generate BRD**: Create a new BRD from the Swagger schema using LLM
   - **Parse BRD Document**: Convert a BRD document (PDF, Word, TXT, CSV) to schema format
4. **Scope Filtering**: Cross-reference BRD with Swagger to filter endpoints
5. **Test Generation**: Generate Gherkin scenarios only for BRD-covered endpoints
6. **Export**: Save results to CSV format
7. **Analytics**: Review detailed analytics and algorithm reports

### Example Session

```bash
$ python main.py
======================================================================
Swagger Schema Processor & Test Scenario Generator
======================================================================

Enter Swagger/OpenAPI schema URL (or press Enter to use example): https://petstore.swagger.io/v2/swagger.json

======================================================================
Step 1: Downloading schema...
======================================================================
Fetching schema from: https://petstore.swagger.io/v2/swagger.json
✓ Detected: SWAGGER 2.0 - Swagger Petstore
✓ Schema downloaded successfully

======================================================================
Step 2: Processing schema...
======================================================================
✓ Schema processed:
  - API: Swagger Petstore
  - Endpoints: 20

======================================================================
Step 3: Analyzing schema for test traceability...
======================================================================
✓ Schema analyzed:
  - Endpoints analyzed: 20

======================================================================
Step 4: Business Requirement Document (BRD)...
======================================================================

Do you have a BRD schema file, or would you like to generate one from the Swagger schema?
1. Load existing BRD file
2. Generate BRD from Swagger schema (using LLM)

Enter choice (1 or 2): 2

📋 Generating BRD from Swagger schema...
✓ BRD generated: API Test Requirements Document
  - Requirements: 15
  - Saved to: src/modules/brd/input_schema/petstore_swagger_io_v2_swagger_brd.json

======================================================================
Step 5: Cross-referencing BRD with Swagger schema...
======================================================================
✓ Cross-reference complete:
  - Total endpoints: 20
  - BRD covered: 15
  - Not covered: 5
  - Coverage: 75.0%
📈 Cross-reference report saved: output/analytics/reports/20241124_133002_cross_reference_schemacrossreference.txt

======================================================================
Step 6: Generating Gherkin test scenarios via LLM...
======================================================================
🤖 Sending prompt to gpt-4...
✓ Gherkin scenarios generated
📊 Analytics saved: output/20241124_133045_schema/analytics/20241124_133045.txt
📈 Algorithm report saved: output/20241124_133045_schema/analytics/reports/llm_prompter_*.txt

======================================================================
Step 7: Saving to CSV...
======================================================================
✓ CSV saved: output/20241124_133045_petstore/petstore_swagger_io_v2_swagger-20241124_133045.csv

======================================================================
Summary
======================================================================
Schema: petstore_swagger_io_v2_swagger.json
API: Swagger Petstore
Total Endpoints: 20
BRD: API Test Requirements Document
BRD Coverage: 75.0%
Tested Endpoints: 15
Output: output/20241124_133045_petstore/petstore_swagger_io_v2_swagger-20241124_133045.csv

✓ Processing complete!
```

## 📋 Example Output

A complete example output is available in `output/example_weather_api/` demonstrating all generated artifacts:
- ✅ Test scenarios in CSV format
- ✅ Generated BRD (Business Requirement Document) JSON
- ✅ Analytics and metrics reports
- ✅ BRD validation reports
- ✅ Algorithm execution reports

See `output/example_weather_api/README.md` for detailed documentation.

## 📁 Project Structure

```
api-param-coverage/
├── src/
│   └── modules/
│       ├── swagger/                                    # Schema downloading and validation
│       │   ├── schema_fetcher.py                       # Downloads schemas from URLs
│       │   └── schema_validator.py                     # Validates and normalizes schemas
│       ├── engine/                                     # Core processing engine
│       │   ├── algorithms/                             # Schema processing algorithms
│       │   │   ├── processor.py                        # Schema processing
│       │   │   ├── analyzer.py                         # Schema analysis and complexity
│       │   │   └── csv_generator.py                    # CSV export
│       │   ├── analytics/                              # Analytics and reporting
│       │   │   ├── metrics_collector.py                # Metrics collection
│       │   │   ├── algorithm_tracker.py                # Algorithm tracking
│       │   │   ├── aggregator.py                       # Analytics aggregation
│       │   │   └── dashboard.py                        # Analytics dashboard
│       │   ├── coverage/                               # Test coverage analysis
│       │   │   └── coverage_analyzer.py                # Coverage analysis
│       │   └── llm/                                    # LLM integration
│       │       └── prompter.py                         # LLM prompting and generation
│       ├── brd/                                        # Business Requirement Document
│       │   ├── brd_schema.py                           # BRD schema definitions
│       │   ├── brd_loader.py                           # BRD file I/O
│       │   ├── brd_parser.py                           # Document parsing (PDF, Word, etc.)
│       │   ├── brd_validator.py                        # BRD validation
│       │   ├── brd_generator.py                        # LLM-based BRD generator
│       │   └── schema_cross_reference.py               # BRD-Swagger cross-reference
├── tests/                                              # Test suite
│   ├── features/                                       # BDD feature files (Behave)
│   │   ├── *.feature                                   # Gherkin feature files
│   │   ├── environment.py                              # Behave environment setup
│   │   └── steps/                                      # Step definitions
│   │       └── *.py                                    # Step implementation files
│   ├── brd/                                            # BRD module tests
│   ├── engine/                                         # Engine module tests
│   ├── swagger/                                        # Swagger module tests
│   └── conftest.py                                     # Pytest configuration
├── docs/                                               # Documentation
│   └── README.md                                       # Documentation guide
├── output/                                             # Execution outputs (at project root)
│   ├── <timestamp>-<schema_name>/                      # Single directory per execution
│   │   ├── <timestamp>-scenarios.csv                    # Test scenarios (CSV)
│   │   ├── <timestamp>-analytics.txt                    # Analytics and metrics
│   │   ├── <timestamp>-validation.txt                   # BRD validation reports
│   │   └── <timestamp>-<algorithm>_<name>.txt          # Algorithm execution reports
│   └── example_weather_api/                            # Example output (weather.gov API)
│       ├── <timestamp>-scenarios.csv                   # Example CSV scenarios
│       ├── <timestamp>-analytics.txt                   # Example analytics
│       ├── <timestamp>-validation.txt                  # Example validation reports
│       ├── <timestamp>-<algorithm>_<name>.txt          # Example algorithm reports
│       └── README.md                                   # Example output documentation
├── main.py                                             # Main entry point
├── requirements.txt                                    # Python dependencies
├── pytest.ini                                          # Pytest configuration
└── README.md                                           # This file
```

## 🔧 Modules Overview

### Schema Processing

| Module | File | Description |
|--------|------|-------------|
| Schema Fetcher | `swagger/schema_fetcher.py` | Downloads schemas from URLs, supports JSON/YAML formats, automatic format detection, error handling and retry logic |
| Schema Validator | `swagger/schema_validator.py` | Detects schema type (Swagger 2.0, OpenAPI 3.0, OpenAPI 3.1), validates schema structure, normalizes schemas, handles partial schemas |
| Schema Processor | `engine/algorithms/processor.py` | Extracts API metadata, processes endpoints and HTTP methods, extracts components (schemas, parameters, responses) |
| Schema Analyzer | `engine/algorithms/analyzer.py` | Deep analysis of schema structure, extracts all parameters, computes iteration domains, handles nested structures and `$ref` references, calculates complexity metrics |

### LLM Integration

| Module | File | Description |
|--------|------|-------------|
| LLM Prompter | `engine/llm/prompter.py` | Creates optimized prompts from schema analysis, integrates with multiple LLM providers, generates Gherkin test scenarios, automatic chunking, token limit management, retry logic |

### BRD System

| Module | File | Description |
|--------|------|-------------|
| BRD Schema | `brd/brd_schema.py` | Defines structured BRD schema format, requirement and test scenario models, priority and status enums, type-safe data structures |
| BRD Loader | `brd/brd_loader.py` | Loads BRD schemas from JSON files, saves BRD schemas, lists available BRD files, validates BRD structure |
| BRD Parser | `brd/brd_parser.py` | Parses BRD documents from multiple formats (PDF, Word, TXT, CSV, Markdown), uses LLM to extract structured data, converts to BRD schema format |
| BRD Generator | `brd/brd_generator.py` | Generates BRD from Swagger schemas, uses heuristic analysis, LLM-powered requirement generation, priority determination, test scenario suggestions |
| Schema Cross-Reference | `brd/schema_cross_reference.py` | Cross-references BRD requirements with Swagger endpoints, filters endpoints by BRD coverage, generates coverage reports, calculates coverage percentages |

### Analytics & Reporting

| Module | File | Description |
|--------|------|-------------|
| Metrics Collector | `engine/analytics/metrics_collector.py` | Collects metrics for LLM API calls, tracks execution time and token usage, analyzes complexity metrics, generates formatted reports |
| Algorithm Tracker | `engine/analytics/algorithm_tracker.py` | Tracks algorithm execution, analyzes input/output complexity, calculates algorithm-specific metrics, generates detailed algorithm reports |
| Analytics Aggregator | `engine/analytics/aggregator.py` | Aggregates analytics data across multiple execution runs, generates summary reports, tracks trends over time |
| Analytics Dashboard | `engine/analytics/dashboard.py` | Generates comprehensive dashboard reports, cost analysis for LLM calls, trend analysis and recommendations, text-based visualization reports |

### Export

| Module | File | Description |
|--------|------|-------------|
| CSV Generator | `engine/algorithms/csv_generator.py` | Parses Gherkin content, converts to structured CSV format, handles markdown code blocks, extracts features, scenarios, and steps |

### Test Coverage Analysis

| Module | File | Description |
|--------|------|-------------|
| Coverage Analyzer | `engine/coverage/coverage_analyzer.py` | Compares generated Gherkin scenarios with BRD requirements, calculates coverage percentage per requirement, identifies missing test scenarios, generates detailed coverage reports, identifies coverage gaps prioritized by requirement priority |

### Configuration Management

| Module | File | Description |
|--------|------|-------------|
| Config | `config.py` | Manages application configuration from environment variables, provides default values, validates configuration settings, handles environment-specific settings |

### Interactive CLI

| Module | File | Description |
|--------|------|-------------|
| CLI Utilities | `cli/cli_utils.py` | Progress Bars (visual progress indicators), Status Updates (real-time status messages), Interactive Selection (validated interactive selection with retry support), Error Recovery (error handling with recovery options), User Confirmation (confirmation prompts with defaults), Formatted Output (consistent formatting for sections, success, errors, warnings, and info messages) |

## 📋 BRD System

### What is a BRD?

A Business Requirement Document (BRD) defines which API endpoints and scenarios should be tested based on business requirements. The tool uses BRD to filter and focus test generation on only the endpoints that matter.

### BRD Schema Format

BRD schema files are stored in `src/modules/brd/input_schema/`. See `src/modules/brd/input_schema/README.md` for the complete schema format.

**Key Components:**
- **Requirements**: List of business requirements
- **Endpoints**: API endpoint paths and methods
- **Test Scenarios**: Specific test cases for each requirement
- **Priority**: Requirement priority (critical, high, medium, low)
- **Acceptance Criteria**: Success criteria for requirements

### BRD Workflow

1. **Create BRD**: Generate from Swagger or parse from document
2. **Validate**: System validates BRD against Swagger schema
3. **Cross-Reference**: Match BRD requirements with Swagger endpoints
4. **Filter**: Only test BRD-covered endpoints
5. **Generate**: Create test scenarios for filtered scope

## 📊 Analytics & Reporting

### Analytics Files

All analytics are saved in `output/<timestamp>_<schema>/analytics/`:

| File Type | File Pattern | Description |
|-----------|--------------|-------------|
| **LLM Execution Metrics** | `YYYYMMDD_HHMMSS.txt` | General LLM call metrics |
| **Algorithm Reports** | `reports/YYYYMMDD_HHMMSS_<type>_<name>.txt` | Detailed algorithm analysis |

### Metrics Tracked

#### LLM Metrics

| Metric | Description |
|--------|-------------|
| Execution time | Time taken for LLM API call |
| Token usage (prompt) | Number of tokens in the prompt |
| Token usage (completion) | Number of tokens in the response |
| Token usage (total) | Total tokens used (prompt + completion) |
| Prompt size | Size of the prompt in characters |
| Response size | Size of the response in characters |
| Model information | LLM model used (e.g., gpt-4, llama-3.1-70b-versatile) |
| Task type | Type of task (analyze, document, validate, gherkin) |

#### Algorithm Metrics

| Metric | Description |
|--------|-------------|
| Algorithm name | Name of the algorithm (e.g., SchemaProcessor, SchemaAnalyzer) |
| Algorithm type | Type/category of the algorithm |
| Input complexity (size) | Size of input data |
| Input complexity (structure) | Structural complexity of input |
| Input complexity (depth) | Depth/nesting level of input data |
| Output complexity (quality) | Quality metrics of output |
| Output complexity (element count) | Number of elements in output |
| Execution time | Time taken for algorithm execution |
| Algorithm-specific complexity metrics | Custom metrics per algorithm type |

#### Complexity Analysis

| Metric | Description |
|--------|-------------|
| Total endpoints analyzed | Total number of API endpoints processed |
| Parameter counts | Count of parameters per endpoint |
| Parameter distributions | Distribution of parameters across endpoints |
| Constraint analysis (enum) | Number of enum constraints |
| Constraint analysis (pattern) | Number of pattern constraints |
| Constraint analysis (bounded/unbounded) | Analysis of bounded vs unbounded parameters |
| Iteration domain counts | Count of iteration domains for test generation |
| Coverage percentages | Percentage of endpoints covered by tests |

### Report Structure

Each algorithm report includes the following sections:

| Section | Description |
|---------|-------------|
| **Algorithm Information** | Name, type, execution time |
| **Input Analysis** | Complexity metrics for input data (size, structure, depth) |
| **Output Analysis** | Quality and complexity of output (quality metrics, element count) |
| **Algorithm-Specific Metrics** | Custom metrics per algorithm (e.g., endpoints processed, parameters extracted) |
| **LLM Analysis** (if applicable) | Token usage, prompt metrics, response metrics, model information |

## ⚙️ Configuration

### Configuration Files

The tool supports YAML and JSON configuration files for flexible settings management:

**Configuration File Priority:**
1. Environment-specific config: `config/{environment}.yaml` (e.g., `config/production.yaml`)
2. Main config file: `config.yaml` or `config.json`
3. Environment variables (highest priority, overrides files)
4. Default values (if nothing is configured)

**Example Configuration (`config.yaml`):**
```yaml
environment: development

algorithm:
  chunk_size: 12
  chunking_threshold: 15
  max_tokens: 3000
  retry_attempts: 3

paths:
  schemas_dir: schemas
  output_dir: output
  analytics_dir: output/analytics

llm:
  model: gpt-4
  temperature: 0.7
  max_tokens: 3000

debug: false
verbose: false
```

**Environment-Specific Configuration:**
- Set `APP_ENV` environment variable to use environment-specific configs
- Example: `APP_ENV=production` loads `config/production.yaml`
- See `config/development.yaml.example` and `config/production.yaml.example` for examples

### Environment Variables

| Variable | Description | Required | Overrides Config |
|----------|-------------|----------|------------------|
| `LLM_API_KEY` | LLM API key (supports multiple providers - auto-detected) | Yes | Yes |
| `APP_ENV` | Environment name (development, production, testing) | No | Yes |
| `LLM_MODEL` | LLM model to use | No | Yes |
| `LLM_MAX_TOKENS` | Maximum response tokens | No | Yes |
| `LLM_TEMPERATURE` | LLM temperature setting | No | Yes |
| `CHUNK_SIZE` | Endpoints per chunk | No | Yes |
| `CHUNKING_THRESHOLD` | Endpoints before chunking | No | Yes |
| `OUTPUT_DIR` | Output directory path | No | Yes |
| `SCHEMAS_DIR` | Schema storage directory | No | Yes |
| `DEBUG` | Enable debug mode | No | Yes |
| `VERBOSE` | Enable verbose output | No | Yes |

### Default Settings

| Setting | Default Value | Description |
|---------|---------------|-------------|
| Schema storage | Temporary | Schemas are downloaded to a temporary directory and cleaned up after processing |
| CSV output directory | `output/<timestamp>-<filename>/` | Generated CSV files location |
| Analytics directory | `output/<timestamp>-<filename>/analytics/` | Analytics files location |
| BRD directory | `src/modules/brd/input_schema/` | BRD schema files location |
| LLM model | Auto-detected | LLM model (auto-detected from API key: Groq uses llama-3.1-70b-versatile, OpenAI uses gpt-4, Anthropic uses claude-3-sonnet, etc.) |
| Max tokens | `3000` | Maximum response tokens |
| Temperature | `0.7` | LLM temperature setting |

### Supported Schema Types

- **Swagger 2.0** (JSON/YAML)
- **OpenAPI 3.0.0** (JSON/YAML)
- **OpenAPI 3.1.0** (JSON/YAML)
- Partial schemas (with warnings)
- Schemas with missing optional fields (normalized)

## 🧪 Testing

The suite is hermetic and cross-platform: it uses synthetic OpenAPI/Swagger
fixtures, writes only to pytest `tmp_path`, mocks the network, and never calls a
live LLM. The CI workflow runs it on Linux, macOS, and Windows across Python
3.9–3.13. Tests requiring network/LLM are marked and excluded by default in CI
via `-m "not llm and not network and not slow and not performance"`.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run only the hermetic, CI-equivalent selection
pytest -m "not llm and not network and not slow and not performance"

# Run the end-to-end pipeline suite (process -> analyze -> coverage -> CSV)
pytest tests/e2e -v

# Run specific test file
pytest tests/test_analyzer.py

# Run specific test class
pytest tests/test_llm_prompter.py::TestLLMPrompter

# Run UI/UX tests
pytest tests/unit/cli/test_cli_utils.py -v
pytest tests/unit/cli/test_cli_utils.py::TestUserInputValidation -v
pytest tests/unit/cli/test_cli_utils.py::TestInteractiveSelectionMenus -v
pytest tests/unit/cli/test_cli_utils.py::TestProgressIndicators -v
pytest tests/unit/cli/test_cli_utils.py::TestStatusMessages -v
pytest tests/unit/cli/test_cli_utils.py::TestErrorHandlingRecovery -v

# Run UI/UX BDD tests
behave tests/features/ui_ux_*.feature

# Run automated UI flow tests
```

### Cross-Platform Compatibility

The tool and its tests run identically on Linux, macOS, and Windows:

- All filesystem paths are built with `pathlib`; no hardcoded separators or
  `/tmp` / drive-letter paths. Run/output directories are created on demand.
- Every text file is opened with `encoding="utf-8"`.
- `main.py` guards console output by calling `sys.stdout/sys.stderr.reconfigure(encoding="utf-8")`
  when available, so the Unicode status glyphs (`✓`, `⚠`, `→`, …) do not crash a
  non-UTF-8 Windows console.
- Schema downloads use OS-managed temporary directories (`tempfile`).

### Test Coverage

The project includes comprehensive tests for:

- ✅ Schema fetching and validation
- ✅ Schema processing and analysis
- ✅ LLM prompting and validation
- ✅ CSV generation
- ✅ CSV export
- ✅ BRD schema operations
- ✅ BRD parsing and generation
- ✅ Schema cross-referencing
- ✅ Analytics and metrics collection
- ✅ **UI/UX terminal interactions** (61 unit tests, 30+ BDD scenarios)

### UI/UX Testing

Comprehensive terminal interaction testing covering all user-facing components:

| Category | Unit Tests | BDD Scenarios | Features Tested |
|----------|------------|---------------|-----------------|
| **User Input Validation** | 15 | 6 | • URL validation (valid/invalid formats, schemes)<br>• Coverage percentage validation (range, non-numeric)<br>• API key validation (format, length, characters)<br>• Empty input handling with defaults |
| **Interactive Selection Menus** | 9 | 7 | • Menu display with numbered options<br>• Option selection and validation<br>• Invalid input handling (letters, out-of-range)<br>• Cancel functionality<br>• Empty list handling |
| **Progress Indicators** | 7 | 5 | • Progress bar display with percentage and ETA<br>• Status messages in progress bars<br>• Chunk progress for LLM operations<br>• Completion handling |
| **Status Messages** | 11 | 6 | • Info, success, warning, error messages<br>• Symbol visibility (ℹ, ✓, ⚠, ✗)<br>• Multi-line output formatting<br>• Status history tracking |
| **Error Handling & Recovery** | 7 | 6 | • Network timeout handling<br>• Custom recovery options<br>• Keyboard interrupt (Ctrl+C)<br>• Missing dependency errors<br>• Default recovery options |

**Test Statistics:**
- **Total Unit Tests**: 61 tests
- **Total BDD Scenarios**: 30+ scenarios
- **CLI Utilities Coverage**: 89%
- **Validators Coverage**: 81%

See [UI/UX Testing Documentation](tests/docs/UI_UX_TESTING.md) for complete details.

### Test Files

| File | Feature |
|------|---------|
| `test_schema_fetcher.py` | Schema downloading tests |
| `test_schema_validator.py` | Schema validation tests |
| `test_processor.py` | Schema processing tests |
| `test_analyzer.py` | Schema analysis tests |
| `test_llm_prompter.py` | LLM integration tests |
| `test_csv_generator.py` | CSV generation tests |
| `test_brd_*.py` | BRD module tests |
| `test_coverage_analyzer.py` | Coverage analysis tests |
| `test_cli_utils.py` | **UI/UX terminal interaction tests (61 tests)** |

## 📤 Output Format

### CSV Files

CSV files are saved in `output/<timestamp>-<filename>/` with format: `<filename>-<timestamp>.csv`

**Columns:**
- `Feature`: Gherkin feature name
- `Scenario`: Scenario name
- `Tags`: Scenario tags (comma-separated)
- `Given`: Given steps (semicolon-separated)
- `When`: When steps (semicolon-separated)
- `Then`: Then steps (semicolon-separated)
- `All Steps`: All steps combined

### Analytics Reports

**LLM Execution Metrics** (`output/<timestamp>-<filename>/analytics/*.txt`):
- Execution information
- API information
- Schema statistics
- Complexity analysis
- Prompt metrics
- API usage (actual tokens)
- Response metrics

**Algorithm Reports** (`output/<timestamp>-<filename>/analytics/reports/*_algorithm_*.txt`):
- Algorithm information
- Input complexity analysis
- Output complexity analysis
- Algorithm-specific metrics
- LLM call analysis (if applicable)

## 🔍 Troubleshooting

| Issue | Symptoms | Solutions |
|-------|----------|-----------|
| **Empty CSV Files** | CSV files contain only placeholders or are empty | 1. Verify `LLM_API_KEY` is set correctly in `.env`<br>2. Check network connectivity to LLM API<br>3. Verify schema has analyzable endpoints<br>4. Review console output for error messages |
| **Schema Validation Errors** | Warnings about missing fields or invalid structure | • Missing optional fields are normalized automatically<br>• Partial schemas may generate warnings but still work<br>• Check error messages for specific issues<br>• Verify schema matches OpenAPI/Swagger specification |
| **LLM Generation Failures** | Rate limits, invalid API key, insufficient quota, empty endpoints, token limits | • Check API key validity in `.env` file (verify `LLM_API_KEY` is set)<br>• Verify your LLM provider account has credits<br>• Review token usage in analytics reports<br>• Consider using smaller schema subsets<br>• Wait and retry (automatic retry included) |
| **BRD Parsing Issues** | BRD parsing fails or produces incomplete results | • Ensure document format is supported<br>• Install required dependencies (PyPDF2, python-docx)<br>• Check document structure and formatting<br>• Review LLM parsing logs in analytics |
| **Token Limit Errors** | "context_length_exceeded" errors | • Tool automatically chunks large schemas<br>• If errors persist, schema may be extremely large<br>• Consider using `gpt-4-turbo` with larger context window<br>• Review chunk size settings |

## 📚 Additional Resources

### Documentation

- **BRD Schema Format**: `src/modules/brd/input_schema/README.md`

### Dependencies

See `requirements.txt` for complete dependency list.

**Core Dependencies:**
- `requests`: HTTP requests for schema downloading
- `pyyaml`: YAML parsing
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management

**Optional Dependencies:**
- `PyPDF2`: PDF document parsing
- `python-docx`: Word document parsing

## 📄 License

This project is provided as-is for testing and development purposes.
