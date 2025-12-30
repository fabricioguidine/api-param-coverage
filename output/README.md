# Output Directory

This directory contains all execution outputs from the API Parameter Coverage tool.

## Structure

```
output/
├── example_weather_api/     # Complete E2E execution example
│   ├── <timestamp>-scenarios.csv  # Test scenarios
│   ├── <timestamp>-analytics.txt  # Analytics and metrics
│   ├── <timestamp>-validation.txt # BRD validation reports
│   ├── <timestamp>-*.txt          # Algorithm execution reports
│   ├── <schema>_brd.json          # BRD schema file
│   └── README.md                   # Example documentation
└── README.md                       # This file
```

## Example Output

The `example_weather_api/` folder contains a **complete end-to-end execution example** with all artifacts from a full workflow run. This serves as a reference for:

- Expected output structure
- File naming conventions
- Artifact types and formats
- Complete workflow demonstration

**See `example_weather_api/README.md` for detailed documentation.**

## Run Directories

Each execution run creates a directory with the format:
`<YYYYMMDD_HHMMSS>-<schema_name>/`

Example: `20251230_110000-api_weather_gov_openapi/`

## File Naming

All files use the format: `<timestamp>-<name>.<ext>`
- Scenarios: `<timestamp>-scenarios.csv`
- Analytics: `<timestamp>-analytics.txt`
- Reports: `<timestamp>-<report_type>.txt`
- Validation: `<timestamp>-validation.txt`

## Accessing Results

1. Find your run directory by timestamp or schema name
2. All artifacts from that execution are in that single directory
3. Files are named with timestamps for easy identification

## Cleanup

To remove old runs, you can manually delete directories or use the output manager's cleanup functionality.

**Note**: The `example_weather_api/` directory is preserved as a reference example and should not be deleted.
