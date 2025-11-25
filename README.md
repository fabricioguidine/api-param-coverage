# API Parameter Coverage & Test Scenario Generator

A comprehensive Python tool for generating test scenarios from OpenAPI/Swagger schemas using LLM-powered analysis and Business Requirement Document (BRD) integration. The tool automatically analyzes API schemas, cross-references them with business requirements, and generates comprehensive Gherkin test scenarios with detailed analytics.

## 🚀 Features

### Core Capabilities
- 🔄 **Multi-Format Schema Support**: Handles Swagger 2.0, OpenAPI 3.0, and OpenAPI 3.1 (JSON/YAML)
- 📥 **Automatic Schema Download**: Fetches schemas from URLs with validation
- 🔍 **Deep Schema Analysis**: Extracts parameters, constraints, and complexity metrics
- 📋 **BRD Integration**: Business Requirement Document support for scope-based testing
- 🤖 **LLM-Powered Generation**: Uses OpenAI GPT-4 for intelligent test scenario generation
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

- Python 3.8 or higher
- OpenAI API key (for LLM features)
- Internet connection (for schema downloading)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api-param-coverage
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```
   
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

1. **Schema Input**: Provide a Swagger/OpenAPI schema URL
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

Enter Swagger/OpenAPI schema URL: https://petstore.swagger.io/v2/swagger.json

======================================================================
Step 1: Downloading schema...
======================================================================
✓ Schema downloaded: data/schemas/petstore_swagger_io_v2_swagger.json

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
  - Saved to: reference/brd/input/petstore_swagger_io_v2_swagger_brd.json

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

## 📁 Project Structure

```
api-param-coverage/
├── src/
│   └── modules/
│       ├── swagger/                   # Schema downloading and validation
│       │   ├── schema_fetcher.py      # Downloads schemas from URLs
│       │   └── schema_validator.py    # Validates and normalizes schemas
│       ├── engine/                    # Core processing engine
│       │   ├── algorithms/            # Schema processing algorithms
│       │   │   ├── processor.py       # Schema processing
│       │   │   ├── analyzer.py        # Schema analysis and complexity
│       │   │   ├── csv_generator.py   # CSV export
│       │   ├── analytics/             # Analytics and reporting
│       │   │   ├── metrics_collector.py      # Metrics collection
│       │   │   ├── algorithm_tracker.py      # Algorithm tracking
│       │   │   ├── aggregator.py     # Analytics aggregation
│       │   │   └── dashboard.py      # Analytics dashboard
│       │   ├── coverage/              # Test coverage analysis
│       │   │   └── coverage_analyzer.py  # Coverage analysis
│       │   └── llm/                   # LLM integration
│       │       └── prompter.py        # LLM prompting and generation
│       ├── brd/                       # Business Requirement Document
│       │   ├── brd_schema.py          # BRD schema definitions
│       │   ├── brd_loader.py          # BRD file I/O
│       │   ├── brd_parser.py          # Document parsing (PDF, Word, etc.)
│       │   ├── brd_validator.py       # BRD validation
│       │   └── schema_cross_reference.py  # BRD-Swagger cross-reference
│       ├── brd_generator/             # BRD generation
│       │   └── brd_generator.py      # LLM-based BRD generator
├── tests/                             # Test suite
│   ├── test_schema_fetcher.py
│   ├── test_schema_validator.py
│   ├── test_processor.py
│   ├── test_analyzer.py
│   ├── test_llm_prompter.py
│   ├── test_csv_generator.py
│   ├── test_brd_schema.py
│   ├── test_brd_loader.py
│   └── test_schema_cross_reference.py
├── reference/                         # Reference data and templates
│   ├── schemas/                      # Downloaded schemas
│   ├── brd/
│   │   ├── input/                     # BRD documents (PDF, Word, TXT, CSV)
│   │   │   └── README.md              # BRD document input guide
│   │   └── output/                    # Generated BRD schemas (JSON)
│   │       └── README.md              # BRD schema format documentation
│   └── dummy_data/                   # Example data and scripts
│       └── scripts/                   # Example utility scripts
├── docs/                              # Documentation
│   ├── PROJECT_STATUS.md              # Project status
│   ├── NEXT_STEPS.md                  # Roadmap
│   └── README.md                      # Documentation guide
├── output/                            # Execution outputs (at project root)
│   ├── <timestamp>-<filename>/       # Execution run folders
│   │   ├── scenarios/                 # CSV scenarios subfolder
│   │   │   └── <timestamp>_*_scenarios.csv
│   │   ├── analytics/                 # Analytics subfolder
│   │   │   └── <timestamp>_*.txt      # LLM execution metrics
│   │   ├── validation/                # Validation reports subfolder
│   │   │   └── <timestamp>_brd_validation_report.txt
│   │   └── reports/                   # Algorithm reports subfolder
│   │       └── <timestamp>_*_algorithm_*.txt
│   └── example_weather_api/           # Example output (weather.gov API)
│       ├── scenarios/                  # Example CSV scenarios
│       ├── analytics/                  # Example analytics
│       ├── validation/                  # Example validation reports
│       ├── reports/                     # Example algorithm reports
│       └── README.md                   # Example output documentation
├── main.py                            # Main entry point
├── reference/                         # Reference data and templates
│   ├── schemas/                      # Downloaded schemas
│   ├── brd/
│   │   ├── input/                     # BRD documents (PDF, Word, TXT, CSV)
│   │   │   └── README.md              # BRD document input guide
│   │   └── output/                    # Generated BRD schemas (JSON)
│   │       └── README.md              # BRD schema format documentation
│   └── scripts/                       # Example utility scripts
│       ├── README.md                  # Scripts documentation
│       └── run_weather_api.py         # Weather API example script
├── requirements.txt                   # Python dependencies
├── pytest.ini                         # Pytest configuration
└── README.md                          # This file
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
| BRD Generator | `brd_generator/brd_generator.py` | Generates BRD from Swagger schemas, uses heuristic analysis, LLM-powered requirement generation, priority determination, test scenario suggestions |
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

### Interactive CLI

| Module | File | Description |
|--------|------|-------------|
| CLI Utilities | `cli/cli_utils.py` | Progress Bars (visual progress indicators), Status Updates (real-time status messages), Interactive Selection (validated interactive selection with retry support), Error Recovery (error handling with recovery options), User Confirmation (confirmation prompts with defaults), Formatted Output (consistent formatting for sections, success, errors, warnings, and info messages) |

## 📋 BRD System

### What is a BRD?

A Business Requirement Document (BRD) defines which API endpoints and scenarios should be tested based on business requirements. The tool uses BRD to filter and focus test generation on only the endpoints that matter.

### BRD Schema Format

BRD files are stored in JSON format in `reference/brd/input/`. See `reference/brd/input/README.md` for the complete schema format.

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

All analytics are saved in `docs/<timestamp>_<schema>/`:

- **LLM Execution Metrics** (`YYYYMMDD_HHMMSS.txt`): General LLM call metrics
- **Algorithm Reports** (`reports/YYYYMMDD_HHMMSS_<type>_<name>.txt`): Detailed algorithm analysis

### Metrics Tracked

#### LLM Metrics
- Execution time
- Token usage (prompt, completion, total)
- Prompt and response sizes
- Model information
- Task type

#### Algorithm Metrics
- Algorithm name and type
- Input complexity (size, structure, depth)
- Output complexity (quality, element count)
- Execution time
- Algorithm-specific complexity metrics

#### Complexity Analysis
- Total endpoints analyzed
- Parameter counts and distributions
- Constraint analysis (enum, pattern, bounded/unbounded)
- Iteration domain counts
- Coverage percentages

### Report Structure

Each algorithm report includes:
1. **Algorithm Information**: Name, type, execution time
2. **Input Analysis**: Complexity metrics for input data
3. **Output Analysis**: Quality and complexity of output
4. **Algorithm-Specific Metrics**: Custom metrics per algorithm
5. **LLM Analysis** (if applicable): Token usage and prompt metrics

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
  schemas_dir: reference/schemas
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
| `OPENAI_API_KEY` | OpenAI API key for LLM features | Yes | Yes |
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
| Schema storage | `reference/schemas/` | Downloaded schemas location |
| CSV output directory | `output/<timestamp>-<filename>/` | Generated CSV files location |
| Analytics directory | `output/<timestamp>-<filename>/analytics/` | Analytics files location |
| BRD directory | `reference/brd/output/` | BRD schema files location |
| LLM model | `gpt-4` | OpenAI model to use |
| Max tokens | `3000` | Maximum response tokens |
| Temperature | `0.7` | LLM temperature setting |

### Supported Schema Types

- **Swagger 2.0** (JSON/YAML)
- **OpenAPI 3.0.0** (JSON/YAML)
- **OpenAPI 3.1.0** (JSON/YAML)
- Partial schemas (with warnings)
- Schemas with missing optional fields (normalized)

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py

# Run specific test class
pytest tests/test_llm_prompter.py::TestLLMPrompter
```

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

### Common Issues

#### Empty CSV Files

**Symptoms**: CSV files contain only placeholders or are empty

**Solutions**:
1. Verify `OPENAI_API_KEY` is set correctly in `.env`
2. Check network connectivity to OpenAI API
3. Verify schema has analyzable endpoints
4. Review console output for error messages

#### Schema Validation Errors

**Symptoms**: Warnings about missing fields or invalid structure

**Solutions**:
- Missing optional fields are normalized automatically
- Partial schemas may generate warnings but still work
- Check error messages for specific issues
- Verify schema matches OpenAPI/Swagger specification

#### LLM Generation Failures

**Common Causes**:
- **Rate Limits**: Wait and retry (automatic retry included)
- **Invalid API Key**: Check `.env` file
- **Insufficient Quota**: Check OpenAI account billing
- **Empty Endpoints**: Ensure schema has endpoints
- **Token Limits**: Large schemas are automatically chunked

**Solutions**:
- Check API key validity
- Verify OpenAI account has credits
- Review token usage in analytics reports
- Consider using smaller schema subsets

#### BRD Parsing Issues

**Symptoms**: BRD parsing fails or produces incomplete results

**Solutions**:
- Ensure document format is supported
- Install required dependencies (PyPDF2, python-docx)
- Check document structure and formatting
- Review LLM parsing logs in analytics

#### Token Limit Errors

**Symptoms**: "context_length_exceeded" errors

**Solutions**:
- Tool automatically chunks large schemas
- If errors persist, schema may be extremely large
- Consider using `gpt-4-turbo` with larger context window
- Review chunk size settings

## 📚 Additional Resources

### Documentation

- **BRD Schema Format**: `reference/brd/input/README.md`
- **Project Status**: `docs/PROJECT_STATUS.md`
- **Next Steps**: `docs/NEXT_STEPS.md`

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
