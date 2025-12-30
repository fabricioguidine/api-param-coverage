# Example Output: Weather.gov API - Complete E2E Flow

This folder contains a **complete end-to-end execution example** from running the tool with the weather.gov API schema. This demonstrates the full workflow and all artifacts produced by a single execution.

## 📋 Overview

This example demonstrates a complete execution workflow including:
- ✅ Schema download and processing
- ✅ BRD (Business Requirement Document) generation from Swagger
- ✅ BRD validation against the schema
- ✅ Cross-reference analysis (BRD vs Swagger)
- ✅ Gherkin test scenario generation via LLM
- ✅ CSV export of test scenarios
- ✅ Analytics and metrics collection
- ✅ Algorithm execution reports

## 📁 Artifacts

All files use the format: `<timestamp>-<name>.<ext>`

| File | Description |
|------|-------------|
| `20251230_140457-scenarios.csv` | Generated Gherkin test scenarios in CSV format |
| `20251230_140457-analytics.txt` | Analytics and metrics from LLM executions |
| `20251230_140457-validation.txt` | BRD validation report comparing BRD with Swagger schema |
| `20251230_140457-validator_brdvalidator.txt` | BRD validator algorithm execution report |
| `20251230_140457-cross_reference_schemacrossreference.txt` | Cross-reference algorithm execution report |
| `weather_gov_api_brd.json` | Generated BRD schema file (can be reused) |

## 🎯 Execution Details

- **API**: weather.gov API
- **Schema URL**: https://api.weather.gov/openapi.json
- **OpenAPI Version**: 3.0.0
- **Total Endpoints**: 59
- **BRD Requirements**: 3
- **BRD Coverage**: 5.08% (3 endpoints covered by BRD)
- **Execution Timestamp**: 2025-12-30 14:04:57

## 📊 Output Structure

```
example_weather_api/
├── 20251230_140457-scenarios.csv                                      # Test scenarios (CSV)
├── 20251230_140457-analytics.txt                                      # LLM execution metrics
├── 20251230_140457-validation.txt                                     # BRD validation report
├── 20251230_140457-validator_brdvalidator.txt                        # Validator algorithm report
├── 20251230_140457-cross_reference_schemacrossreference.txt         # Cross-reference algorithm report
├── weather_gov_api_brd.json                                          # Generated BRD schema
└── README.md                                                          # This file
```

## 🔍 What This Example Shows

1. **Complete Workflow**: All steps from schema download to CSV generation
2. **BRD Generation**: Automatically generated BRD from Swagger schema using LLM
3. **Validation**: BRD validated against the Swagger schema
4. **Cross-Reference**: BRD requirements matched with Swagger endpoints
5. **Test Scenarios**: Gherkin scenarios generated for BRD-covered endpoints
6. **Analytics**: Detailed metrics on LLM calls, complexity analysis, and execution times
7. **Reports**: Algorithm-specific reports showing execution details

## 📝 Notes

- This is a **real example** generated from the weather.gov API
- All files are timestamped for easy identification
- The BRD file (`weather_gov_api_brd.json`) can be reused for future runs
- All artifacts from a single execution are in this directory
- Files follow the format: `<timestamp>-<name>.<ext>`

## 🚀 How to Use This Example

1. **Review the BRD**: Check `weather_gov_api_brd.json` to see how requirements are structured
2. **Examine Scenarios**: Open `20251230_140457-scenarios.csv` to see generated test scenarios
3. **Check Analytics**: Review `20251230_140457-analytics.txt` for execution metrics
4. **Validate Output**: See `20251230_140457-validation.txt` for validation results
5. **Understand Cross-Reference**: Check `20251230_140457-cross_reference_schemacrossreference.txt` for coverage analysis

## 📚 Related Documentation

- Main README: `../../README.md`
- Output Structure: `../README.md`
- BRD Schema Format: `../../src/modules/brd/brd_schema.py`

---

**Generated**: 2025-12-30 14:04:57  
**Tool Version**: 1.0.0  
**Example Label**: Complete E2E workflow demonstration
