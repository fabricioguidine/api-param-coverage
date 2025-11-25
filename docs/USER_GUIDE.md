# User Guide

A comprehensive guide for using the API Parameter Coverage & Test Scenario Generator.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [BRD Workflows](#brd-workflows)
5. [Advanced Features](#advanced-features)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for LLM features)
- Internet connection (for schema downloading)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd api-param-coverage

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY='your-api-key-here'
```

### First Run

1. Run the main script:
   ```bash
   python main.py
   ```

2. Enter a Swagger/OpenAPI schema URL when prompted:
   ```
   Enter Swagger/OpenAPI schema URL: https://petstore.swagger.io/v2/swagger.json
   ```

3. Follow the interactive prompts to:
   - Process the schema
   - Handle BRD (Business Requirement Document)
   - Generate test scenarios
   - Export results

## Basic Usage

### Example 1: Simple Schema Processing

**Scenario**: Generate test scenarios for a public API without BRD filtering.

**Steps**:

1. Start the application:
   ```bash
   python main.py
   ```

2. Enter the schema URL:
   ```
   Enter Swagger/OpenAPI schema URL: https://api.example.com/openapi.json
   ```

3. When asked about BRD, choose option 3 (Generate BRD from Swagger):
   ```
   How would you like to handle the Business Requirement Document (BRD)?
   1. Load existing BRD schema file (JSON)
   2. Parse BRD from document (PDF, Word, TXT, CSV)
   3. Generate BRD from Swagger schema (using LLM)
   
   Enter choice: 3
   ```

4. Set coverage percentage (or press Enter for 100%):
   ```
   Coverage percentage (default: 100): 50
   ```

5. The system will:
   - Download and process the schema
   - Generate a BRD with 50% endpoint coverage
   - Generate Gherkin test scenarios
   - Export to CSV format

6. Results will be saved in `output/<timestamp>-<filename>/`

### Example 2: Using Existing BRD

**Scenario**: You have a BRD schema file and want to filter test scenarios based on it.

**Steps**:

1. Place your BRD JSON file in `src/modules/brd/input_schema/`:
   ```bash
   cp my_brd.json src/modules/brd/input_schema/
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Enter schema URL and select option 1 (Load existing BRD):
   ```
   How would you like to handle the Business Requirement Document (BRD)?
   Enter choice: 1
   ```

4. Select your BRD file from the list:
   ```
   Select BRD schema file:
   1. my_brd.json
   2. weather_gov_api_brd.json (if available in src/modules/brd/input_schema/)
   
   Note: The default weather.gov example BRD is in examples/weather_gov_api/brd.json
   
   Enter choice: 1
   ```

5. The system will:
   - Load your BRD
   - Cross-reference it with the Swagger schema
   - Generate test scenarios only for BRD-covered endpoints
   - Show coverage statistics

### Example 3: Parsing BRD from Document

**Scenario**: You have a BRD document (PDF, Word, etc.) that needs to be converted to a schema.

**Steps**:

1. Place your BRD document in `src/modules/brd/input_transformator/`:
   ```bash
   cp requirements.pdf src/modules/brd/input_transformator/
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Enter schema URL and select option 2 (Parse BRD from document):
   ```
   How would you like to handle the Business Requirement Document (BRD)?
   Enter choice: 2
   ```

4. Select your document:
   ```
   Available BRD documents:
   1. requirements.pdf
   
   Select document to parse (number): 1
   ```

5. The system will:
   - Extract text from your document
   - Use LLM to parse and convert to BRD schema
   - Save the schema to `src/modules/brd/input_schema/`
   - Use it for filtering test scenarios

## BRD Workflows

### Workflow 1: Full Coverage Testing

**Use Case**: Test all endpoints in an API.

1. Run application
2. Enter schema URL
3. Choose option 3 (Generate BRD) or skip BRD
4. Set coverage to 100% (default)
5. Generate scenarios for all endpoints

**Output**: CSV file with test scenarios for all endpoints.

### Workflow 2: Priority-Based Testing

**Use Case**: Test only critical endpoints (POST, PUT, DELETE operations).

1. Run application
2. Enter schema URL
3. Choose option 3 (Generate BRD)
4. Set coverage to 30-50% (prioritizes critical operations)
5. System automatically prioritizes POST/PUT/DELETE endpoints

**Output**: CSV file with test scenarios for high-priority endpoints.

### Workflow 3: BRD-Driven Testing

**Use Case**: Test only endpoints specified in business requirements.

1. Prepare BRD schema (JSON) or document (PDF/Word)
2. Run application
3. Load or parse BRD
4. System filters endpoints based on BRD
5. Generate scenarios only for BRD-covered endpoints

**Output**: CSV file with test scenarios matching business requirements.

## Advanced Features

### Coverage Analysis

The system automatically generates coverage reports:

- **BRD Coverage Report**: Shows which endpoints are covered by BRD
- **Test Coverage Report**: Compares generated scenarios with BRD requirements
- **Analytics Reports**: Detailed metrics in `output/<run_id>/analytics/`

## Configuration

### Environment Variables

The tool uses environment variables and default constants for configuration:

```bash
# Required
export OPENAI_API_KEY='your-api-key-here'

# Optional
export LLM_MODEL='gpt-4'
export LLM_TEMPERATURE='0.7'
export LLM_MAX_TOKENS='3000'
export SCHEMAS_DIR='schemas'
export OUTPUT_DIR='output'
```

### Default Settings

All settings use sensible defaults defined in `src/modules/utils/constants.py`. Environment variables override defaults when set.

### Custom File Paths

You can provide custom paths for BRD files:

```
Select BRD schema file:
Enter custom path (or select from list): C:/users/my_brd.json
```

## Troubleshooting

### Common Issues

#### Issue: "OPENAI_API_KEY not found"

**Solution**:
```bash
# Set in environment
export OPENAI_API_KEY='your-key'

# Or create .env file
echo "OPENAI_API_KEY=your-key" > .env
```

#### Issue: "Schema validation warning"

**Solution**: The schema may have minor issues but will still be processed. Check the warning message for details.

#### Issue: "Failed to parse BRD JSON"

**Solution**:
- Ensure BRD file is valid JSON
- Check file encoding (should be UTF-8)
- Validate JSON using a JSON validator

#### Issue: "No endpoints found"

**Solution**:
- Verify the schema URL is accessible
- Check that the schema contains path definitions
- Ensure schema format is Swagger 2.0 or OpenAPI 3.x

#### Issue: "Rate limit exceeded"

**Solution**:
- Wait a few minutes and retry
- Check your OpenAI API quota
- Consider using a different model (e.g., gpt-3.5-turbo)

### Getting Help

- Check the analytics reports in `output/<run_id>/analytics/` for detailed error information
- Review the console output for specific error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Best Practices

1. **Start with Small Coverage**: For large APIs, start with 20-30% coverage to test the workflow
2. **Review Generated BRD**: Always review auto-generated BRDs before using them
3. **Use BRD Validation**: Run BRD validation to check for orphaned requirements
4. **Check Analytics**: Review analytics reports to understand LLM usage and costs
5. **Version Control**: Keep your BRD schemas in version control
6. **Organize Outputs**: Use descriptive schema names for easier output organization

## Next Steps

- Check [Architecture Documentation](ARCHITECTURE.md) for system design
- Review [API Documentation](API_DOCUMENTATION.md) for module details


