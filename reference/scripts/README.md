# Scripts

This directory contains utility scripts for running specific examples and test scenarios.

## Available Scripts

### `run_weather_api.py`

Runs the tool with the weather.gov API schema and a pre-configured BRD schema.

**Usage:**
```bash
# From project root
python reference/scripts/run_weather_api.py
```

**What it does:**
- Downloads the weather.gov OpenAPI schema
- Loads or generates a BRD schema
- Cross-references BRD with Swagger
- Generates Gherkin test scenarios
- Saves results to CSV
- Generates analytics reports

**Requirements:**
- `OPENAI_API_KEY` must be set in `.env` file
- Internet connection for downloading schema



