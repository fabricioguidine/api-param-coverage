# Example Output: Weather.gov API

This folder contains example output from running the tool with the weather.gov API schema, demonstrating the new organized output structure.

## Contents

- **scenarios/**: Generated Gherkin test scenarios in CSV format
  - **`<timestamp>_*_scenarios.csv`**: CSV files with test scenarios (timestamped)
- **analytics/**: Analytics and metrics from the execution
  - **`<timestamp>_*.txt`**: LLM execution metrics (timestamped)
- **validation/**: BRD validation reports
  - **`<timestamp>_brd_validation_report.txt`**: Validation report comparing BRD with Swagger schema
- **reports/**: Algorithm-specific reports
  - **`<timestamp>_*_algorithm_*.txt`**: Algorithm execution reports (timestamped)

## How to Generate This Output

Use the main tool with the weather.gov API (or any Swagger/OpenAPI URL):

```bash
python main.py
# Enter URL: https://api.weather.gov/openapi.json
```

## Output Structure

This example demonstrates the new organized output structure with timestamped subfolders:

```
example_weather_api/
├── scenarios/                       # CSV scenarios folder
│   └── <timestamp>_*_scenarios.csv # CSV file with Gherkin scenarios (timestamped)
├── analytics/                       # Analytics folder
│   └── <timestamp>_*.txt          # LLM execution metrics (timestamped)
├── validation/                      # Validation reports folder
│   └── <timestamp>_brd_validation_report.txt
└── reports/                         # Algorithm reports folder
    ├── <timestamp>_*_algorithm_*.txt
    └── <timestamp>_cross_reference_*.txt
```

## Notes

- All files are prefixed with timestamps for chronological tracking
- Each type of output has its own labeled subfolder
- The structure makes it easy to find and manage execution artifacts
- This is a real execution example, not a simplified mock
