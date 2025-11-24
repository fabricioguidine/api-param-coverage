# Documentation and Execution Outputs

This directory contains project documentation and execution outputs organized by timestamp.

## Structure

```
docs/
├── latex/                         # LaTeX monography files
├── <YYYYMMDD_HHMMSS>_<schema>/    # Execution run folders
│   ├── csv/                       # Generated CSV files with Gherkin scenarios
│   └── analytics/                 # Analytics and metrics for this run
│       ├── *.txt                  # LLM execution metrics
│       └── reports/                # Algorithm-specific reports
│           └── *_algorithm_*.txt   # Detailed algorithm analysis
├── PROJECT_STATUS.md              # Project status
└── NEXT_STEPS.md                  # Roadmap
```

## Execution Runs

Each time you run the tool, a new folder is created with the format:
`<YYYYMMDD_HHMMSS>_<schema_name>/`

This folder contains all artifacts from that execution:
- **CSV files**: Gherkin test scenarios in CSV format
- **Analytics**: LLM execution metrics and performance data
- **Reports**: Detailed algorithm analysis reports

## Benefits

- **Clear organization**: Each run has its own timestamped folder
- **Easy tracking**: Find all files from a specific execution quickly
- **Simple cleanup**: Delete old runs by removing their folders
- **Better traceability**: Timestamp shows exactly when each run occurred

## Example

```
docs/
├── 20251124_140913_api_weather_gov_openapi.json/
│   ├── csv/
│   │   └── api_weather_gov_openapi.json-20251124_141012.csv
│   └── analytics/
│       ├── 20251124_141012.txt
│       └── reports/
│           └── 20251124_141012_llm_prompter_llmprompter.txt
└── 20251124_150000_petstore_api/
    ├── csv/
    └── analytics/
```

## Notes

- Folders are automatically created when you run the tool
- All output files are organized within their respective run folders
- Old runs can be safely deleted to free up space
- Documentation files (README.md, PROJECT_STATUS.md, etc.) are kept separate

