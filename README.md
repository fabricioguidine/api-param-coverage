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
- 📊 **Multiple Export Formats**: CSV export for test management tools
- 📈 **Comprehensive Analytics**: Detailed metrics and reports for every algorithm execution

### Advanced Features
- 📦 **Smart Chunking**: Automatically handles large schemas by processing in chunks
- 🔄 **BRD Generation**: Creates BRD documents from Swagger schemas using heuristic analysis
- 📄 **Document Parsing**: Converts BRD documents (PDF, Word, TXT, CSV) to structured schemas
- 📊 **Algorithm Tracking**: Detailed complexity analysis for each algorithm execution
- ⚡ **Performance Monitoring**: Execution time and resource usage tracking
- 🎨 **Structured Reports**: Separate analytics reports for each algorithm and LLM call

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
5. Exporting to CSV

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
│       ├── swagger_tool/              # Schema downloading and validation
│       │   ├── schema_fetcher.py      # Downloads schemas from URLs
│       │   └── schema_validator.py    # Validates and normalizes schemas
│       ├── engine/                    # Core processing engine
│       │   ├── algorithms/            # Schema processing algorithms
│       │   │   ├── processor.py       # Schema processing
│       │   │   ├── analyzer.py        # Schema analysis and complexity
│       │   │   └── csv_generator.py   # CSV export
│       │   ├── analytics/             # Analytics and reporting
│       │   │   ├── metrics_collector.py      # Metrics collection
│       │   │   └── algorithm_tracker.py      # Algorithm tracking
│       │   └── llm/                   # LLM integration
│       │       └── prompter.py        # LLM prompting and generation
│       ├── brd/                       # Business Requirement Document
│       │   ├── brd_schema.py          # BRD schema definitions
│       │   ├── brd_loader.py          # BRD file I/O
│       │   ├── brd_parser.py          # Document parsing (PDF, Word, etc.)
│       │   └── schema_cross_reference.py  # BRD-Swagger cross-reference
│       └── brd_generator/             # BRD generation
│           └── brd_generator.py      # LLM-based BRD generator
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
├── data/                              # Input data
│   └── schemas/                       # Downloaded schemas storage
├── reference/                         # Reference data and templates
│   └── brd/
│       ├── input/                     # BRD documents (PDF, Word, TXT, CSV)
│       │   └── README.md              # BRD document input guide
│       └── output/                    # Generated BRD schemas (JSON)
│           └── README.md              # BRD schema format documentation
├── docs/                              # Documentation
│   ├── latex/                         # LaTeX monography files
│   ├── PROJECT_STATUS.md              # Project status
│   ├── NEXT_STEPS.md                  # Roadmap
│   └── README.md                      # Documentation guide
├── output/                            # Execution outputs (at project root)
│   └── <timestamp>_<schema>/         # Execution run folders
│       ├── analytics/                 # Analytics subfolder
│       │   ├── *.txt                  # LLM execution metrics
│       │   └── reports/               # Algorithm-specific reports
│       ├── *.csv                      # Generated CSV files (Gherkin scenarios)
│       └── brd_validation_report_*.txt # Validation reports
├── main.py                            # Main entry point
├── scripts/                           # Utility scripts
│   └── run_weather_api.py            # Weather API test script
├── requirements.txt                   # Python dependencies
├── pytest.ini                         # Pytest configuration
└── README.md                          # This file
```

## 🔧 Modules Overview

### Schema Processing

#### Schema Fetcher (`swagger_tool/schema_fetcher.py`)
- Downloads schemas from URLs
- Supports JSON and YAML formats
- Automatic format detection
- Error handling and retry logic

#### Schema Validator (`swagger_tool/schema_validator.py`)
- Detects schema type (Swagger 2.0, OpenAPI 3.0, OpenAPI 3.1)
- Validates schema structure
- Normalizes schemas for processing
- Handles partial or incomplete schemas

#### Schema Processor (`engine/algorithms/processor.py`)
- Extracts API metadata (title, version, description)
- Processes endpoints and HTTP methods
- Extracts components (schemas, parameters, responses)
- Provides structured data for analysis

#### Schema Analyzer (`engine/algorithms/analyzer.py`)
- Deep analysis of schema structure
- Extracts all parameters (path, query, header, body, response)
- Computes iteration domains for test coverage
- Handles nested structures and `$ref` references
- Calculates complexity metrics

### LLM Integration

#### LLM Prompter (`engine/llm/prompter.py`)
- Creates optimized prompts from schema analysis
- Integrates with OpenAI GPT-4
- Generates Gherkin test scenarios
- Automatic chunking for large schemas
- Token limit management
- Retry logic for API errors
- Comprehensive input validation

### BRD System

#### BRD Schema (`brd/brd_schema.py`)
- Defines structured BRD schema format
- Requirement and test scenario models
- Priority and status enums
- Type-safe data structures

#### BRD Loader (`brd/brd_loader.py`)
- Loads BRD schemas from JSON files
- Saves BRD schemas to files
- Lists available BRD files
- Validates BRD structure

#### BRD Parser (`brd/brd_parser.py`)
- Parses BRD documents from multiple formats:
  - PDF (requires PyPDF2)
  - Word documents (requires python-docx)
  - Text files (.txt)
  - CSV files
  - Markdown (.md)
- Uses LLM to extract structured data
- Converts documents to BRD schema format

#### BRD Generator (`brd_generator/brd_generator.py`)
- Generates BRD from Swagger schemas
- Uses heuristic analysis for test planning
- LLM-powered requirement generation
- Priority determination based on HTTP methods
- Test scenario suggestions

#### Schema Cross-Reference (`brd/schema_cross_reference.py`)
- Cross-references BRD requirements with Swagger endpoints
- Filters endpoints by BRD coverage
- Generates coverage reports
- Calculates coverage percentages

### Analytics & Reporting

#### Metrics Collector (`engine/analytics/metrics_collector.py`)
- Collects metrics for LLM API calls
- Tracks execution time and token usage
- Analyzes complexity metrics
- Generates formatted reports

#### Algorithm Tracker (`engine/analytics/algorithm_tracker.py`)
- Tracks algorithm execution
- Analyzes input/output complexity
- Calculates algorithm-specific metrics
- Generates detailed algorithm reports

### Export

#### CSV Generator (`engine/algorithms/csv_generator.py`)
- Parses Gherkin content
- Converts to structured CSV format
- Handles markdown code blocks
- Extracts features, scenarios, and steps

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

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM features | Yes |

### Default Settings

| Setting | Default Value | Description |
|---------|---------------|-------------|
| Schema storage | `data/schemas/` | Downloaded schemas location |
| CSV output directory | `output/<timestamp>_<schema>/` | Generated CSV files location |
| Analytics directory | `output/<timestamp>_<schema>/analytics/` | Analytics files location |
| BRD directory | `reference/brd/output/` | BRD schema files location |
| LLM model | `gpt-4` | OpenAI model to use |
| Max tokens | `3000` | Maximum response tokens |
| Chunk size | `12` | Endpoints per chunk |
| Chunking threshold | `15` | Endpoints before chunking |

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
- ✅ BRD schema operations
- ✅ BRD parsing and generation
- ✅ Schema cross-referencing
- ✅ Analytics and metrics collection

### Test Files

- `test_schema_fetcher.py` - Schema downloading tests
- `test_schema_validator.py` - Schema validation tests
- `test_processor.py` - Schema processing tests
- `test_analyzer.py` - Schema analysis tests
- `test_llm_prompter.py` - LLM integration tests
- `test_csv_generator.py` - CSV generation tests
- `test_brd_*.py` - BRD module tests (to be added)

## 📤 Output Format

### CSV Files

CSV files are saved in `output/<timestamp>_<schema>/` with format: `<schemaName>-<timestamp>.csv`

**Columns:**
- `Feature`: Gherkin feature name
- `Scenario`: Scenario name
- `Tags`: Scenario tags (comma-separated)
- `Given`: Given steps (semicolon-separated)
- `When`: When steps (semicolon-separated)
- `Then`: Then steps (semicolon-separated)
- `All Steps`: All steps combined

### Analytics Reports

**LLM Execution Metrics** (`output/<timestamp>_<schema>/analytics/*.txt`):
- Execution information
- API information
- Schema statistics
- Complexity analysis
- Prompt metrics
- API usage (actual tokens)
- Response metrics

**Algorithm Reports** (`output/<timestamp>_<schema>/analytics/reports/*_algorithm_*.txt`):
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
- `requests` - HTTP requests for schema downloading
- `pyyaml` - YAML parsing
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management

**Optional Dependencies:**
- `PyPDF2` - PDF document parsing
- `python-docx` - Word document parsing

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Follow PEP 8 style guidelines

## 📄 License

This project is provided as-is for testing and development purposes.

## 🆘 Support

For issues or questions:
- Check error messages in console output
- Review test files for usage examples
- Verify schema format matches OpenAPI/Swagger specifications
- Check analytics reports for detailed execution information

---

**Version**: 1.0.0  
**Last Updated**: November 2024
