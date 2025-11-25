# BRD Input Schema

This directory contains BRD (Business Requirement Document) files that are already in schema format (JSON).

## Usage

Place your BRD schema files (`.json`) in this directory. These files should follow the BRD schema format defined in `brd_schema.py`.

## File Format

BRD schema files must be valid JSON following this structure:

```json
{
  "brd_id": "BRD-001",
  "title": "BRD Title",
  "description": "Description",
  "api_name": "API Name",
  "api_version": "Version",
  "created_date": "ISO date",
  "requirements": [
    {
      "requirement_id": "REQ-001",
      "title": "Requirement title",
      "description": "Description",
      "endpoint_path": "/path",
      "endpoint_method": "GET",
      "priority": "high",
      "status": "pending",
      "test_scenarios": [...],
      "acceptance_criteria": [...],
      "related_endpoints": []
    }
  ],
  "metadata": {}
}
```

## Loading BRD Schemas

Use `BRDLoader` to load BRD schemas from this directory:

```python
from src.modules.brd import BRDLoader

loader = BRDLoader()  # Defaults to this directory
brd = loader.load_brd_from_file("my_brd")
```

## Notes

- Files in this directory are already in the correct schema format
- If you have a document (PDF, Word, TXT, etc.) that needs transformation, place it in `input_transformator/` instead
- Generated BRD schemas from Swagger or documents will be saved here

