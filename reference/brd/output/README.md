# BRD Schema Output

This directory contains generated BRD (Business Requirement Document) schema files in JSON format.

## Schema Files

BRD schema files are automatically generated from:
1. **Document Parsing**: When BRD documents (PDF, Word, TXT, CSV) are parsed from `../input/`
2. **LLM Generation**: When BRD schemas are generated from Swagger schemas

## Schema Format

All BRD schema files follow the JSON format defined in `../input/README.md`.

## File Naming

Generated BRD schemas are named based on:
- Source document name (for parsed documents)
- Swagger schema name (for generated schemas)
- Format: `<name>_brd.json`

## Usage

These schema files are automatically loaded by the BRD Loader when you select "Load existing BRD file" in the main workflow.

## Manual Creation

You can also manually create BRD schema files here following the format specified in `../input/README.md`.

## Notes

- All files in this directory should be valid JSON
- Files are automatically ignored by git (see `.gitignore`)
- Schema files are used to filter test scope during scenario generation

