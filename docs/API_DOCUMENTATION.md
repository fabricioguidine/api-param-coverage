# API Documentation

Complete API reference for the API Parameter Coverage & Test Scenario Generator.

## Table of Contents

1. [Schema Tool Module](#schema-tool-module)
2. [Engine Module](#engine-module)
3. [BRD Module](#brd-module)
4. [BRD Generator Module](#brd-generator-module)
5. [Config Module](#config-module)
6. [CLI Module](#cli-module)
7. [Utils Module](#utils-module)
8. [Workflow Module](#workflow-module)

## Schema Tool Module

### SchemaFetcher

Downloads and saves Swagger/OpenAPI schemas from URLs.

#### Methods

##### `__init__(schemas_dir: str = "reference/schemas")`

Initialize the Schema Fetcher.

**Parameters**:
- `schemas_dir` (str): Directory to save downloaded schemas

##### `fetch_schema(url: str) -> Optional[dict]`

Fetch schema from URL.

**Parameters**:
- `url` (str): Schema URL

**Returns**:
- `Optional[dict]`: Schema dictionary or None if error

**Raises**:
- `ValueError`: If URL is invalid
- `requests.exceptions.RequestException`: If download fails

##### `download_and_save(url: str, format: str = "json") -> Optional[str]`

Download schema and save to file.

**Parameters**:
- `url` (str): Schema URL
- `format` (str): Output format ("json" or "yaml")

**Returns**:
- `Optional[str]`: Path to saved file or None if error

### SchemaValidator

Validates and normalizes Swagger/OpenAPI schemas.

#### Methods

##### `validate_schema(schema: dict) -> Tuple[bool, Optional[str]]`

Validate schema structure.

**Parameters**:
- `schema` (dict): Schema dictionary

**Returns**:
- `Tuple[bool, Optional[str]]`: (is_valid, error_message)

##### `normalize_schema(schema: dict) -> dict`

Normalize schema to standard format.

**Parameters**:
- `schema` (dict): Schema dictionary

**Returns**:
- `dict`: Normalized schema

## Engine Module

### SchemaProcessor

Processes raw schema data into structured format.

#### Methods

##### `process_schema_file(filename: str) -> Optional[Dict[str, Any]]`

Process schema file.

**Parameters**:
- `filename` (str): Schema filename

**Returns**:
- `Optional[Dict[str, Any]]`: Processed data or None

### SchemaAnalyzer

Analyzes schemas for test traceability.

#### Methods

##### `analyze_schema_file(filename: str) -> Optional[Dict[str, Any]]`

Analyze schema file.

**Parameters**:
- `filename` (str): Schema filename

**Returns**:
- `Optional[Dict[str, Any]]`: Analysis data or None

### LLMPrompter

Handles LLM prompting and response generation.

#### Methods

##### `__init__(model: Optional[str] = None, api_key: Optional[str] = None, analytics_dir: Optional[str] = None)`

Initialize LLM Prompter.

**Parameters**:
- `model` (Optional[str]): LLM model name
- `api_key` (Optional[str]): API key
- `analytics_dir` (Optional[str]): Analytics directory

##### `create_prompt(processed_data: Dict[str, Any], task: str = "analyze", analysis_data: Optional[Dict[str, Any]] = None) -> str`

Create prompt from processed schema data.

**Parameters**:
- `processed_data` (Dict[str, Any]): Processed schema data
- `task` (str): Task type ("analyze", "gherkin", etc.)
- `analysis_data` (Optional[Dict[str, Any]]): Analysis data for Gherkin generation

**Returns**:
- `str`: Formatted prompt

##### `send_prompt(prompt: str) -> Optional[str]`

Send prompt to LLM and get response.

**Parameters**:
- `prompt` (str): Prompt string

**Returns**:
- `Optional[str]`: LLM response or None if error

**Raises**:
- `ValueError`: If prompt is invalid

### CSVGenerator

Generates CSV output from Gherkin scenarios.

#### Methods

##### `__init__(output_dir: str = "output")`

Initialize CSV Generator.

**Parameters**:
- `output_dir` (str): Output directory

##### `generate_csv(gherkin_content: str, schema_name: str) -> Optional[Path]`

Generate CSV from Gherkin content.

**Parameters**:
- `gherkin_content` (str): Gherkin scenarios string
- `schema_name` (str): Schema name for filename

**Returns**:
- `Optional[Path]`: Path to CSV file or None

### MetricsCollector

Exports scenarios to multiple formats.

#### Methods

##### `__init__(output_dir: str = "output")`

Initialize Multi-Format Exporter.

**Parameters**:
- `output_dir` (str): Output directory

##### `export_to_jira(scenarios: List[Dict[str, Any]], filename: Optional[str] = None) -> Path`

Export to JIRA format (CSV).

**Parameters**:
- `scenarios` (List[Dict[str, Any]]): Scenario data
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to exported file

##### `export_to_testrail(scenarios: List[Dict[str, Any]], filename: Optional[str] = None) -> Path`

Export to TestRail format (CSV).

**Parameters**:
- `scenarios` (List[Dict[str, Any]]): Scenario data
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to exported file

##### `export_to_azure_devops(scenarios: List[Dict[str, Any]], filename: Optional[str] = None) -> Path`

Export to Azure DevOps format (CSV).

**Parameters**:
- `scenarios` (List[Dict[str, Any]]): Scenario data
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to exported file

##### `export_to_json(scenarios: List[Dict[str, Any]], filename: Optional[str] = None) -> Path`

Export to JSON format.

**Parameters**:
- `scenarios` (List[Dict[str, Any]]): Scenario data
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to exported file

##### `export_to_html(scenarios: List[Dict[str, Any]], filename: Optional[str] = None) -> Path`

Export to HTML report.

**Parameters**:
- `scenarios` (List[Dict[str, Any]]): Scenario data
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to exported file

### MetricsCollector

Collects and saves analytics metrics.

#### Methods

##### `__init__(analytics_dir: Optional[str] = None)`

Initialize Metrics Collector.

**Parameters**:
- `analytics_dir` (Optional[str]): Analytics directory

##### `collect_algorithm_metrics(algorithm_name: str, algorithm_type: str, input_data: Dict[str, Any], output_data: Dict[str, Any], execution_time: float, complexity_metrics: Optional[Dict[str, Any]] = None, llm_call: bool = False, llm_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Collect algorithm execution metrics.

**Parameters**:
- `algorithm_name` (str): Algorithm name
- `algorithm_type` (str): Algorithm type
- `input_data` (Dict[str, Any]): Input data metrics
- `output_data` (Dict[str, Any]): Output data metrics
- `execution_time` (float): Execution time in seconds
- `complexity_metrics` (Optional[Dict[str, Any]]): Complexity metrics
- `llm_call` (bool): Whether LLM was called
- `llm_metrics` (Optional[Dict[str, Any]]): LLM-specific metrics

**Returns**:
- `Dict[str, Any]`: Collected metrics

##### `save_algorithm_report(metrics: Dict[str, Any]) -> Optional[Path]`

Save algorithm report to file.

**Parameters**:
- `metrics` (Dict[str, Any]): Metrics dictionary

**Returns**:
- `Optional[Path]`: Path to saved report or None

## BRD Module

### BRDLoader

Loads and saves BRD schemas.

#### Methods

##### `__init__(brd_dir: str = "reference/brd/output")`

Initialize BRD Loader.

**Parameters**:
- `brd_dir` (str): BRD directory

##### `load_brd_from_file(filename: str) -> Optional[BRDSchema]`

Load BRD schema from file.

**Parameters**:
- `filename` (str): BRD filename (with or without .json)

**Returns**:
- `Optional[BRDSchema]`: BRD schema or None if error

##### `list_available_brds() -> List[str]`

List available BRD files.

**Returns**:
- `List[str]`: List of BRD filenames

##### `save_brd_to_file(brd: BRDSchema, filename: Optional[str] = None) -> Path`

Save BRD schema to file.

**Parameters**:
- `brd` (BRDSchema): BRD schema object
- `filename` (Optional[str]): Output filename

**Returns**:
- `Path`: Path to saved file

### BRDParser

Parses BRD documents from various formats.

#### Methods

##### `__init__(api_key: Optional[str] = None, model: str = "gpt-4", input_dir: str = "reference/brd/input", output_dir: str = "reference/brd/output")`

Initialize BRD Parser.

**Parameters**:
- `api_key` (Optional[str]): OpenAI API key
- `model` (str): LLM model
- `input_dir` (str): Input directory for documents
- `output_dir` (str): Output directory for schemas

##### `parse_document(filename: str) -> Optional[BRDSchema]`

Parse BRD document to schema.

**Parameters**:
- `filename` (str): Document filename

**Returns**:
- `Optional[BRDSchema]`: BRD schema or None if error

##### `list_available_documents() -> List[str]`

List available BRD documents.

**Returns**:
- `List[str]`: List of document filenames

### BRDValidator

Validates BRD schemas against Swagger.

#### Methods

##### `__init__(analytics_dir: Optional[str] = None)`

Initialize BRD Validator.

**Parameters**:
- `analytics_dir` (Optional[str]): Analytics directory

##### `validate_brd_against_swagger(brd: BRDSchema, analysis_data: Dict[str, Any]) -> Dict[str, Any]`

Validate BRD against Swagger analysis.

**Parameters**:
- `brd` (BRDSchema): BRD schema
- `analysis_data` (Dict[str, Any]): Swagger analysis data

**Returns**:
- `Dict[str, Any]`: Validation report

### SchemaCrossReference

Cross-references BRD with Swagger schema.

#### Methods

##### `__init__(analytics_dir: Optional[str] = None)`

Initialize Schema Cross-Reference.

**Parameters**:
- `analytics_dir` (Optional[str]): Analytics directory

##### `filter_endpoints_by_brd(analysis_data: Dict[str, Any], brd: BRDSchema) -> Dict[str, Any]`

Filter endpoints based on BRD.

**Parameters**:
- `analysis_data` (Dict[str, Any]): Swagger analysis data
- `brd` (BRDSchema): BRD schema

**Returns**:
- `Dict[str, Any]`: Filtered analysis data

##### `get_brd_coverage_report(analysis_data: Dict[str, Any], brd: BRDSchema) -> Dict[str, Any]`

Get BRD coverage report.

**Parameters**:
- `analysis_data` (Dict[str, Any]): Swagger analysis data
- `brd` (BRDSchema): BRD schema

**Returns**:
- `Dict[str, Any]`: Coverage report

## BRD Generator Module

### BRDGenerator

Generates BRD schemas from Swagger using LLM.

#### Methods

##### `__init__(api_key: Optional[str] = None, model: str = "gpt-4", analytics_dir: Optional[str] = None)`

Initialize BRD Generator.

**Parameters**:
- `api_key` (Optional[str]): OpenAI API key
- `model` (str): LLM model
- `analytics_dir` (Optional[str]): Analytics directory

##### `generate_brd_from_swagger(processed_data: Dict[str, Any], analysis_data: Dict[str, Any], schema_filename: str, coverage_percentage: float = 100.0) -> Optional[BRDSchema]`

Generate BRD from Swagger schema.

**Parameters**:
- `processed_data` (Dict[str, Any]): Processed schema data
- `analysis_data` (Dict[str, Any]): Analysis data
- `schema_filename` (str): Schema filename
- `coverage_percentage` (float): Coverage percentage (1-100)

**Returns**:
- `Optional[BRDSchema]`: Generated BRD schema or None

## Configuration

Configuration is managed through environment variables and default constants defined in `src/modules/utils/constants.py`.

### Available Constants

- `DEFAULT_LLM_MODEL`: Default LLM model (default: "gpt-4")
- `DEFAULT_LLM_TEMPERATURE`: Default temperature (default: 0.7)
- `DEFAULT_LLM_MAX_TOKENS`: Default max tokens (default: 3000)
- `DEFAULT_SCHEMAS_DIR`: Default schemas directory (default: "reference/schemas")
- `DEFAULT_OUTPUT_DIR`: Default output directory (default: "output")
- `DEFAULT_BRD_INPUT_DIR`: Default BRD input directory (default: "reference/brd/input")
- `DEFAULT_BRD_OUTPUT_DIR`: Default BRD output directory (default: "reference/brd/output")

### Environment Variables

All constants can be overridden via environment variables:
- `LLM_MODEL`: Override default LLM model
- `LLM_TEMPERATURE`: Override default temperature
- `LLM_MAX_TOKENS`: Override default max tokens
- `SCHEMAS_DIR`: Override default schemas directory
- `OUTPUT_DIR`: Override default output directory

##### `save_config(filepath: Path, format: str = "yaml")`

Save configuration to file.

**Parameters**:
- `filepath` (Path): Output file path
- `format` (str): File format ("yaml" or "json")

## CLI Module

### ProgressBar

Displays progress bars for long operations.

#### Methods

##### `__init__(total: int, description: str = "Processing")`

Initialize Progress Bar.

**Parameters**:
- `total` (int): Total number of items
- `description` (str): Progress description

##### `update(n: int = 1, postfix: Optional[str] = None)`

Update progress.

**Parameters**:
- `n` (int): Number of items completed
- `postfix` (Optional[str]): Additional text to display

### StatusUpdater

Displays dynamic status messages.

#### Methods

##### `__init__(initial_message: str = "Starting...", level: str = "info")`

Initialize Status Updater.

**Parameters**:
- `initial_message` (str): Initial status message
- `level` (str): Status level ("info", "success", "error", "warning")

##### `update(message: str, level: str = "info")`

Update status message.

**Parameters**:
- `message` (str): Status message
- `level` (str): Status level

### InteractiveSelector

Provides interactive list selection.

#### Methods

##### `select_from_list(items: List[Any], prompt: str = "Select an item", display_func: Optional[Callable[[Any], str]] = None, allow_cancel: bool = False) -> Optional[Any]`

Select item from list interactively.

**Parameters**:
- `items` (List[Any]): List of items
- `prompt` (str): Prompt message
- `display_func` (Optional[Callable[[Any], str]]): Function to format items
- `allow_cancel` (bool): Allow canceling selection

**Returns**:
- `Optional[Any]`: Selected item or None if canceled

## Utils Module

### extract_json_from_response

Extract JSON from LLM response.

#### Function

##### `extract_json_from_response(response: str) -> Optional[str]`

Extract JSON from response (may be wrapped in markdown).

**Parameters**:
- `response` (str): LLM response string

**Returns**:
- `Optional[str]`: Extracted JSON or original response

## Workflow Module

### apply_coverage_filter

Apply coverage percentage filter to endpoints.

#### Function

##### `apply_coverage_filter(analysis_data: Dict[str, Any], coverage_percentage: float = 100.0) -> Tuple[Dict[str, Any], Dict[str, Any]]`

Filter endpoints by coverage percentage.

**Parameters**:
- `analysis_data` (Dict[str, Any]): Schema analysis data
- `coverage_percentage` (float): Coverage percentage (1-100)

**Returns**:
- `Tuple[Dict[str, Any], Dict[str, Any]]`: (filtered_data, coverage_report)

### apply_brd_filter

Apply BRD-based filtering to endpoints.

#### Function

##### `apply_brd_filter(analysis_data: Dict[str, Any], brd: BRDSchema) -> Tuple[Dict[str, Any], Dict[str, Any]]`

Filter endpoints based on BRD.

**Parameters**:
- `analysis_data` (Dict[str, Any]): Schema analysis data
- `brd` (BRDSchema): BRD schema

**Returns**:
- `Tuple[Dict[str, Any], Dict[str, Any]]`: (filtered_data, coverage_report)

## Data Structures

### BRDSchema

BRD schema data structure.

**Fields**:
- `brd_id` (str): Unique BRD identifier
- `title` (str): BRD title
- `description` (str): BRD description
- `api_name` (str): API name
- `api_version` (str): API version
- `created_date` (str): Creation date (ISO format)
- `requirements` (List[BRDRequirement]): List of requirements
- `metadata` (Dict[str, Any]): Additional metadata

### BRDRequirement

BRD requirement data structure.

**Fields**:
- `requirement_id` (str): Unique requirement identifier
- `title` (str): Requirement title
- `description` (str): Requirement description
- `endpoint_path` (str): API endpoint path
- `endpoint_method` (str): HTTP method
- `priority` (RequirementPriority): Priority level
- `status` (RequirementStatus): Status
- `test_scenarios` (List[BRDTestScenario]): Test scenarios
- `acceptance_criteria` (List[str]): Acceptance criteria
- `related_endpoints` (List[str]): Related endpoints

### BRDTestScenario

BRD test scenario data structure.

**Fields**:
- `scenario_id` (str): Unique scenario identifier
- `scenario_name` (str): Scenario name
- `description` (str): Scenario description
- `test_steps` (List[str]): Test steps (Gherkin format)
- `expected_result` (str): Expected result
- `priority` (RequirementPriority): Priority level
- `tags` (List[str]): Scenario tags

## Enums

### RequirementPriority

Priority levels for requirements.

**Values**:
- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

### RequirementStatus

Status values for requirements.

**Values**:
- `PENDING`
- `IN_PROGRESS`
- `COMPLETED`
- `BLOCKED`


