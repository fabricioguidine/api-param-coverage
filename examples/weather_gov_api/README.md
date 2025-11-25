# Weather.gov API Example

This is the default example demonstrating the API Parameter Coverage & Test Scenario Generator tool.

## Files

- **`schema.json`**: OpenAPI 3.0 schema for the National Weather Service API (weather.gov)
  - Source: https://api.weather.gov/openapi.json
  - Contains endpoints for weather alerts, forecasts, observations, and more

- **`brd.json`**: Pre-generated BRD (Business Requirement Document) schema
  - Defines test requirements for critical weather endpoints
  - Includes test scenarios, acceptance criteria, and priority levels
  - Focuses on alerts, forecasts, and observations endpoints

## Running This Example

```bash
# From project root
python scripts/run_weather_api.py
```

This will:
1. Load the schema from `schema.json`
2. Load the BRD from `brd.json`
3. Cross-reference BRD requirements with Swagger endpoints
4. Generate Gherkin test scenarios
5. Save results to `output/<timestamp>-<schema_name>/`

## Example Output Structure

After running, you'll find:
```
output/
└── <timestamp>-api_weather_gov_openapi/
    ├── scenarios/
    │   └── <timestamp>_*_scenarios.csv
    ├── analytics/
    │   └── <timestamp>_*.txt
    ├── validation/
    │   └── <timestamp>_brd_validation_report.txt
    └── reports/
        └── <timestamp>_*_algorithm_*.txt
```

## BRD Requirements

The included BRD focuses on:
- **Active Weather Alerts** (`/alerts/active`) - Critical priority
- **Alert Counts** (`/alerts/active/count`) - High priority
- **Single Alert Retrieval** (`/alerts/{id}`) - High priority
- **Gridpoint Forecasts** (`/gridpoints/{wfo}/{x},{y}/forecast`) - High priority
- **Station Observations** (`/stations/{stationId}/observations`) - Medium priority

## Notes

- This example demonstrates the complete workflow from schema to test scenarios
- The BRD can be regenerated using the BRDGenerator if needed
- All outputs are timestamped for easy tracking

