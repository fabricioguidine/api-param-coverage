# Output Directory

This directory contains execution outputs organized by timestamp.

## Structure

Each run creates a folder with the format: `<YYYYMMDD_HHMMSS>_<schema_name>/`

```
output/
└── <timestamp>_<schema>/
    ├── analytics/                    # Analytics subfolder for this run
    │   ├── *.txt                     # LLM execution metrics
    │   └── reports/                  # Algorithm-specific reports
    │       └── *_algorithm_*.txt
    ├── *.csv                         # Generated CSV files (Gherkin scenarios)
    └── brd_validation_report_*.txt   # Validation reports
```

## Configuration

You can specify a custom output directory using the `OUTPUT_DIR` environment variable:

```bash
# Linux/Mac
export OUTPUT_DIR=/path/to/output
python main.py

# Windows
set OUTPUT_DIR=C:\path\to\output
python main.py
```

## Example

The folder `20251124_162747_api_weather_gov_openapi.json/` (if exists) is kept as an example of the output structure.

## Notes

- All output folders are automatically ignored by git except the example
- Old runs can be safely deleted to free up space
- Each run folder contains all artifacts from that execution
- Output directory is separate from documentation for better architecture
