# BRD Input Transformator

This directory contains BRD documents that need to be transformed into BRD schema format.

## Supported Formats

Place your BRD documents here in any of these formats:

- **PDF** (`.pdf`) - PDF documents containing BRD requirements
- **Word Documents** (`.doc`, `.docx`) - Microsoft Word documents
- **Text Files** (`.txt`) - Plain text documents
- **CSV Files** (`.csv`) - Comma-separated value files
- **Markdown** (`.md`) - Markdown formatted documents

## Usage

1. Place your BRD document in this directory
2. Use `BRDParser` to transform it to BRD schema format:

```python
from src.modules.brd import BRDParser

parser = BRDParser(api_key="your-api-key")  # Defaults to this directory
brd = parser.parse_document("my_requirements.pdf")
```

The transformed BRD schema will be saved to `input_schema/` directory.

## Transformation Process

The transformation uses a two-step process:
1. **Document → Intermediate BRD**: Extracts requirements from the document
2. **Intermediate BRD → BRD Schema**: Converts to structured schema format

This process uses LLM (Language Model) to parse and structure the document content.

## Requirements

- `OPENAI_API_KEY` must be set in environment variables
- For PDF parsing: `pip install PyPDF2`
- For Word parsing: `pip install python-docx`

## Notes

- Large documents may be truncated to fit LLM token limits
- Document parsing quality depends on document structure and formatting
- The parser works best with documents that explicitly mention API endpoints
- JSON files should be placed in `input_schema/` directory, not here

