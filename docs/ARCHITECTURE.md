# Architecture Documentation

System architecture and design documentation for the API Parameter Coverage & Test Scenario Generator.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Module Architecture](#module-architecture)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Technology Stack](#technology-stack)

## System Overview

The API Parameter Coverage & Test Scenario Generator is a Python-based tool that:

1. Downloads and processes OpenAPI/Swagger schemas
2. Integrates with Business Requirement Documents (BRD)
3. Uses LLM to generate test scenarios
4. Exports results in multiple formats
5. Provides comprehensive analytics

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Entry Point                       │
│                         (main.py)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│ Schema Tool  │ │   Engine    │ │    BRD     │
│   Module     │ │   Module    │ │  Module    │
└───────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Output & Analytics       │
        └───────────────────────────────┘
```

## Architecture Diagram

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI Utils  │  │   Workflow   │  │    Config    │          │
│  │   Module     │  │   Module     │  │   Manager    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼─────────┐  ┌───────▼────────┐
│  Schema Tool   │  │      Engine       │  │      BRD       │
│    Module      │  │      Module       │  │     Module     │
├────────────────┤  ├───────────────────┤  ├────────────────┤
│                │  │                   │  │                │
│ SchemaFetcher  │  │  SchemaProcessor  │  │  BRDLoader     │
│ SchemaValidator│  │  SchemaAnalyzer   │  │  BRDParser     │
│                │  │  LLMPrompter      │  │  BRDValidator  │
│                │  │  CSVGenerator     │  │  BRDGenerator  │
│                │  │                   │  │  CrossRef.     │
│                │  │  MetricsCollector │  │                │
│                │  │  CoverageAnalyzer │  │                │
└────────────────┘  └───────────────────┘  └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Utils Module   │
                    ├──────────────────┤
                    │  JSON Utils      │
                    │  Constants       │
                    └──────────────────┘
```

### Data Flow Diagram

```
User Input (Schema URL)
        │
        ▼
┌───────────────┐
│ SchemaFetcher │ ──► Download & Validate
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Processor   │ ──► Process Schema
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Analyzer    │ ──► Analyze Endpoints
└───────┬───────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌───────────────┐
│ BRD Handler   │  │  Coverage     │
│ (Load/Gen/    │  │  Filter       │
│  Parse)       │  │               │
└───────┬───────┘  └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
         ┌────────────────┐
         │  LLMPrompter   │ ──► Generate Gherkin
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ CSVGenerator   │ ──► Export CSV
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │   Analytics    │ ──► Generate Reports
         └────────────────┘
```

## Module Architecture

### Schema Tool Module

**Purpose**: Handle schema downloading and validation.

**Components**:
- `SchemaFetcher`: Downloads schemas from URLs
- `SchemaValidator`: Validates and normalizes schemas

**Responsibilities**:
- HTTP requests for schema downloading
- Schema format validation (JSON/YAML)
- Schema version detection (Swagger 2.0, OpenAPI 3.x)
- Schema normalization

### Engine Module

**Purpose**: Core processing and analysis.

**Sub-modules**:

#### Algorithms
- `SchemaProcessor`: Processes raw schema data
- `SchemaAnalyzer`: Analyzes schema for test traceability
- `CSVGenerator`: Converts Gherkin to CSV

#### Analytics
- `MetricsCollector`: Collects execution metrics
- `AlgorithmTracker`: Tracks algorithm execution
- `Aggregator`: Aggregates analytics across runs
- `Dashboard`: Generates dashboard reports

#### Coverage
- `CoverageAnalyzer`: Analyzes test coverage

#### LLM
- `LLMPrompter`: Handles LLM interactions

### BRD Module

**Purpose**: Business Requirement Document management.

**Components**:
- `BRDSchema`: Data structures for BRD
- `BRDLoader`: Load/save BRD schemas
- `BRDParser`: Parse BRD documents (PDF, Word, etc.)
- `BRDValidator`: Validate BRD against Swagger
- `BRDGenerator`: Generate BRD from Swagger
- `SchemaCrossReference`: Cross-reference BRD with Swagger

### Utils Module

**Purpose**: Shared utilities and constants.

**Components**:
- `json_utils`: JSON extraction utilities
- `constants`: Shared constants

### Workflow Module

**Purpose**: Workflow orchestration (extracted from main.py).

**Components**:
- `coverage_handler`: Coverage filtering logic

### CLI Module

**Purpose**: Command-line interface utilities.

**Components**:
- `cli_utils`: Progress bars, status updates, interactive selection

### Config Module

**Purpose**: Configuration management.

**Components**:
- `ConfigManager`: Loads and manages configuration

## Data Flow

### 1. Schema Processing Flow

```
URL Input
  │
  ▼
SchemaFetcher.fetch_schema()
  │
  ▼
SchemaValidator.validate_schema()
  │
  ▼
SchemaProcessor.process_schema_file()
  │
  ▼
SchemaAnalyzer.analyze_schema_file()
  │
  ▼
Analysis Data (Dict)
```

### 2. BRD Processing Flow

```
BRD Input (File/Document/Generation)
  │
  ├─► BRDLoader.load_brd_from_file()
  ├─► BRDParser.parse_document()
  └─► BRDGenerator.generate_brd_from_swagger()
  │
  ▼
BRDSchema Object
  │
  ▼
BRDValidator.validate_brd_against_swagger()
  │
  ▼
SchemaCrossReference.filter_endpoints_by_brd()
  │
  ▼
Filtered Analysis Data
```

### 3. Test Generation Flow

```
Filtered Analysis Data
  │
  ▼
LLMPrompter.create_prompt()
  │
  ▼
LLMPrompter.send_prompt()
  │
  ▼
Gherkin Scenarios (String)
  │
  ▼
CSVGenerator.generate_csv()
  │
  ▼
CSV File
  │
  ▼
CSVGenerator.generate_csv()
  │
  ▼
Multiple Export Files
```

### 4. Analytics Flow

```
Algorithm Execution
  │
  ▼
MetricsCollector.collect_algorithm_metrics()
  │
  ▼
MetricsCollector.save_algorithm_report()
  │
  ▼
Analytics Report (JSON/Text)
  │
  ▼
AnalyticsAggregator.aggregate_runs()
  │
  ▼
AnalyticsDashboard.generate_dashboard_report()
  │
  ▼
Dashboard Report
```

## Design Patterns

### 1. Factory Pattern

Used in module initialization:

```python
# ConfigManager creates instances based on configuration
config = ConfigManager()
processor = SchemaProcessor(config=config)
```

### 2. Strategy Pattern

Used for different export formats:

```python
# CSVGenerator exports scenarios to CSV format
csv_generator.generate_csv(gherkin_content, schema_name)
```

### 3. Template Method Pattern

Used in workflow orchestration:

```python
# Main workflow follows a template with customizable steps
def main():
    # Step 1: Download schema (template)
    # Step 2: Process schema (template)
    # Step 3: Handle BRD (customizable)
    # Step 4: Generate scenarios (template)
```

### 4. Observer Pattern

Used in analytics collection:

```python
# MetricsCollector observes algorithm execution
metrics_collector.collect_algorithm_metrics(...)
```

### 5. Singleton Pattern

Used for configuration management:

```python
# ConfigManager is initialized once and reused
config_manager = ConfigManager()
```

## Technology Stack

### Core Technologies

- **Python 3.8+**: Main programming language
- **OpenAI API**: LLM integration for test generation
- **PyYAML**: YAML parsing for schemas and configs
- **requests**: HTTP requests for schema downloading

### Key Libraries

- **python-dotenv**: Environment variable management
- **PyPDF2**: PDF document parsing
- **python-docx**: Word document parsing
- **pytest**: Testing framework
- **tqdm**: Progress bars
- **colorama**: Colored console output

### Data Formats

- **JSON**: Schema storage, BRD schemas, configuration
- **YAML**: Schema storage, configuration
- **CSV**: Test scenario export

## File Organization

### Output Structure

```
output/
├── <timestamp>_<schema_name>/
│   ├── gherkin_scenarios_<timestamp>.csv
│   └── analytics/
│       ├── algorithm_report_<algorithm>_<timestamp>.txt
│       └── llm_execution_metrics_<timestamp>.txt
```

### Reference Data Structure

```
reference/
├── schemas/              # Downloaded schemas
├── brd/
│   ├── input/           # BRD documents (PDF, Word, etc.)
│   └── output/          # BRD schemas (JSON)
└── dummy_data/
    └── scripts/         # Example scripts
```

## Extension Points

### 1. Custom Export Formats

Extend `CSVGenerator` to add new CSV export options.

### 2. Custom LLM Providers

Implement provider interface to add new LLM services.

### 3. Custom BRD Formats

Extend `BRDParser` to support new document formats.

### 4. Custom Analytics

Extend `MetricsCollector` to track additional metrics.

## Performance Considerations

1. **Chunking**: Large schemas are processed in chunks to stay within LLM token limits
2. **Caching**: Consider implementing caching for repeated operations
3. **Parallel Processing**: Independent operations can be parallelized
4. **Lazy Loading**: Data is loaded only when needed

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Input Validation**: All inputs are validated before processing
3. **File Paths**: User-provided paths are validated
4. **Error Messages**: Don't expose sensitive information in error messages

## Future Enhancements

1. **Plugin System**: Allow plugins for custom formats and providers
2. **API Server**: REST API for programmatic access
3. **Web UI**: Browser-based interface
4. **Database Integration**: Store results in database
5. **CI/CD Integration**: Command-line mode for automation


