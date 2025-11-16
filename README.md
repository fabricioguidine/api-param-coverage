# Swagger Schema Processor & Test Scenario Generator

A comprehensive Python tool for downloading, analyzing, and generating test scenarios from OpenAPI/Swagger schemas using LLM-powered Gherkin test generation.

## Features

- 🔄 **Dynamic Schema Support**: Handles all SmartBear/OpenAPI schema types (Swagger 2.0, OpenAPI 3.0, OpenAPI 3.1)
- 📥 **Schema Download**: Automatically downloads schemas from URLs (JSON/YAML)
- 🔍 **Schema Analysis**: Extracts detailed test traceability information
- 🤖 **LLM Integration**: Generates comprehensive Gherkin test scenarios using OpenAI GPT-4
- 📊 **CSV Export**: Exports test scenarios to CSV format for test management tools
- ✅ **Validation**: Comprehensive input validation and error handling
- 🧪 **Test Coverage**: Full test suite with pytest
- 📦 **Smart Chunking**: Automatically handles large schemas by processing in chunks

## Project Structure

```
testing/
├── src/
│   └── modules/
│       ├── swagger_tool/          # Schema downloading and validation
│       │   ├── schema_fetcher.py
│       │   └── schema_validator.py
│       └── engine/                # Processing and LLM generation
│           ├── algorithms/        # Schema processing algorithms
│           │   ├── processor.py
│           │   ├── analyzer.py
│           │   └── csv_generator.py
│           └── llm/              # LLM prompting
│               └── prompter.py
├── tests/                         # Test suite
├── data/
│   └── schemas/                  # Downloaded schemas storage
├── output/                        # Generated CSV files
├── main.py                       # Main entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd testing
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-api-key-here
```

**Important**: Never commit your API key to the repository. The `.env` file is already in `.gitignore`.

## Usage

### Basic Usage

Run the main script:

```bash
python main.py
```

The program will:
1. Prompt for a Swagger/OpenAPI schema URL
2. Download and validate the schema
3. Process and analyze the schema
4. Generate Gherkin test scenarios via LLM (with automatic chunking for large schemas)
5. Save results to CSV in the `output/` directory

### Example

```bash
$ python main.py
======================================================================
Swagger Schema Processor & Test Scenario Generator
======================================================================

Enter Swagger/OpenAPI schema URL: https://petstore.swagger.io/v2/swagger.json

======================================================================
Step 1: Downloading schema...
======================================================================
✓ Detected: SWAGGER 2.0 - Swagger Petstore
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
Step 4: Generating Gherkin test scenarios via LLM...
======================================================================
🤖 Sending prompt to gpt-4...
✓ Gherkin scenarios generated

======================================================================
Step 5: Saving to CSV...
======================================================================
✓ CSV saved: output/petstore_swagger_io_v2_swagger-20251116_123456.csv

======================================================================
Summary
======================================================================
Schema: petstore_swagger_io_v2_swagger.json
API: Swagger Petstore
Endpoints: 20
Output: output/petstore_swagger_io_v2_swagger-20251116_123456.csv

✓ Processing complete!
```

## Supported Schema Types

The tool automatically detects and handles:

- **Swagger 2.0** (JSON/YAML)
- **OpenAPI 3.0.0** (JSON/YAML)
- **OpenAPI 3.1.0** (JSON/YAML)
- **Partial schemas** (with warnings)
- **Schemas with missing optional fields** (normalized automatically)

## Output Format

CSV files are saved in the `output/` directory with the format:
```
<swaggerName>-<timestamp>.csv
```

CSV columns:
- `Feature`: Gherkin feature name
- `Scenario`: Scenario name
- `Tags`: Scenario tags
- `Given`: Given steps
- `When`: When steps
- `Then`: Then steps
- `All Steps`: All steps combined

## Large Schema Handling

For schemas with more than 15 endpoints, the tool automatically:
- **Chunks the processing**: Splits endpoints into groups of 12
- **Processes sequentially**: Each chunk is processed separately
- **Combines results**: All Gherkin scenarios are merged into a single CSV

This ensures the tool stays within GPT-4's token limits (8192 tokens) while handling schemas of any size.

## Testing

The project includes comprehensive tests for all modules:

- `test_schema_fetcher.py` - Tests for schema downloading
- `test_schema_validator.py` - Tests for schema validation and type detection
- `test_processor.py` - Tests for schema processing
- `test_analyzer.py` - Tests for schema analysis
- `test_llm_prompter.py` - Tests for LLM prompting and validation
- `test_csv_generator.py` - Tests for CSV generation

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_schema_fetcher.py

# Run specific test class
pytest tests/test_llm_prompter.py::TestLLMPrompter
```

## Modules

### Schema Fetcher (`swagger_tool/schema_fetcher.py`)
- Downloads schemas from URLs
- Supports JSON and YAML formats
- Validates and normalizes schemas

### Schema Validator (`swagger_tool/schema_validator.py`)
- Detects schema type and version
- Validates schema structure
- Normalizes schemas for processing

### Schema Processor (`engine/algorithms/processor.py`)
- Extracts API information
- Processes endpoints and components
- Provides structured schema data

### Schema Analyzer (`engine/algorithms/analyzer.py`)
- Analyzes schemas for test traceability
- Extracts parameters (path, query, header, body, response)
- Computes iteration domains for test coverage
- Handles nested structures and $ref references

### LLM Prompter (`engine/llm/prompter.py`)
- Creates prompts from schema analysis
- Integrates with OpenAI GPT-4
- Generates Gherkin test scenarios
- Validates inputs and handles errors
- Automatically chunks large schemas

### CSV Generator (`engine/algorithms/csv_generator.py`)
- Parses Gherkin content
- Converts to CSV format
- Handles markdown code blocks
- Creates structured test data

## Error Handling

The tool includes comprehensive error handling:

- **Empty Input Validation**: Raises `ValueError` if inputs are empty
- **Schema Validation**: Validates schema structure before processing
- **LLM Error Handling**: Handles API errors, rate limits, and empty responses
- **Token Limit Management**: Automatically chunks large schemas to stay within limits
- **Graceful Degradation**: Creates placeholder scenarios when generation fails

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for LLM generation)

### Default Settings

- Schema storage: `data/schemas/`
- Output directory: `output/`
- LLM model: `gpt-4`
- Max tokens: `3000` (fits within GPT-4's 8192 token limit)
- Chunk size: `12` endpoints per chunk
- Chunking threshold: `15` endpoints

## Troubleshooting

### Empty CSV Files

If CSV files are empty or contain only placeholders:

1. **Check API Key**: Verify your OpenAI API key is set correctly in `.env`
2. **Check Network**: Ensure you can reach the OpenAI API
3. **Check Schema**: Verify the schema has endpoints to analyze
4. **Check Logs**: Look for error messages in the console output

### Schema Validation Errors

If you see validation warnings:

- The schema might be missing optional fields (will be normalized)
- The schema might be a partial/incomplete schema
- Check the error message for specific issues

### LLM Generation Failures

Common issues:

- **Rate Limits**: Wait and retry (automatic retry logic included)
- **Invalid API Key**: Check your `.env` file
- **Insufficient Quota**: Check your OpenAI account billing
- **Empty Endpoints**: Ensure the schema has analyzable endpoints
- **Token Limits**: Large schemas are automatically chunked

### Token Limit Errors

If you see "context_length_exceeded" errors:

- The tool should automatically chunk large schemas
- If errors persist, the schema may be extremely large
- Consider using a model with larger context window (e.g., `gpt-4-turbo`)

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list

## License

This project is provided as-is for testing and development purposes.

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## Support

For issues or questions:
- Check the error messages in console output
- Review the test files for usage examples
- Verify your schema format matches OpenAPI/Swagger specifications
