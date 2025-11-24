# BRD Document Input

This directory contains raw Business Requirement Document (BRD) files in various formats that will be converted to structured BRD schemas.

## Supported Document Formats

Place your BRD documents here in any of these formats:

- **PDF** (`.pdf`) - PDF documents containing BRD requirements
- **Word Documents** (`.doc`, `.docx`) - Microsoft Word documents
- **Text Files** (`.txt`) - Plain text documents
- **CSV Files** (`.csv`) - Comma-separated value files
- **Markdown** (`.md`) - Markdown formatted documents

## How It Works

1. Place your BRD document in this `input/` folder
2. Run the BRD parser tool (via main.py or directly)
3. The system will use LLM to parse and extract requirements from your document
4. The parsed BRD schema will be saved as JSON in `../output/` folder
5. The generated schema can then be used for test scenario generation

## Document Requirements

For best results, your BRD documents should contain:
- API endpoint information (paths and HTTP methods)
- Test requirements and scenarios
- Acceptance criteria
- Priority levels (if applicable)

The LLM parser will extract this information and convert it to the structured BRD schema format.

## Example Workflow

```bash
# 1. Place your BRD document here
#    e.g., my_api_requirements.pdf

# 2. Run the tool and select "Parse BRD document"
#    The tool will:
#    - Read the document from this folder
#    - Parse it using LLM
#    - Generate BRD schema JSON
#    - Save to ../output/my_api_requirements_brd.json
```

## Notes

- Large documents may be truncated to fit LLM token limits
- Document parsing quality depends on document structure and formatting
- For best results, use well-structured documents with clear sections
- The parser works best with documents that explicitly mention API endpoints
