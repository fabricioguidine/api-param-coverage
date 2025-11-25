"""
BRD Parser

Parses BRD documents from various formats (PDF, Word, TXT, CSV, etc.) and converts them to BRD schema format using LLM.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from .brd_schema import BRDSchema, BRDRequirement, BRDTestScenario, RequirementPriority, RequirementStatus
from ..engine.llm import LLMPrompter
from ..utils import extract_json_from_response
from ..utils.constants import SUPPORTED_BRD_FORMATS


class BRDParser:
    """Parses BRD documents from various formats and converts to BRD schema."""
    
    SUPPORTED_FORMATS = SUPPORTED_BRD_FORMATS
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", provider: str = "openai", input_dir: str = "reference/brd/input", output_dir: str = "reference/brd/output"):
        """
        Initialize the BRD Parser.
        
        Args:
            api_key: LLM API key
            model: LLM model to use
            provider: LLM provider ('openai', 'anthropic', 'google', 'azure')
            input_dir: Directory where BRD documents are stored
            output_dir: Directory where parsed BRD schemas will be saved
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm_prompter = LLMPrompter(model=model, api_key=api_key, provider=provider) if api_key else None
    
    def parse_document(self, filename: str) -> Optional[BRDSchema]:
        """
        Parse a BRD document from various formats and convert to BRD schema.
        The document should be in the input directory.
        
        Args:
            filename: Name of the BRD document file (in input directory)
            
        Returns:
            BRDSchema object, or None if parsing fails
        """
        # Try to find file in input directory first
        file_path_obj = self.input_dir / filename
        
        # If not found, try as absolute path
        if not file_path_obj.exists():
            file_path_obj = Path(filename)
        
        if not file_path_obj.exists():
            print(f"✗ Error: File not found: {filename}")
            print(f"   Searched in: {self.input_dir}")
            print(f"   Also checked as absolute path: {Path(filename)}")
            print(f"   Tip: Ensure the file exists or provide the full path.")
            return None
        
        print(f"📄 Reading document from: {file_path_obj}")
        
        file_ext = file_path_obj.suffix.lower()
        
        if file_ext not in self.SUPPORTED_FORMATS:
            print(f"✗ Error: Unsupported file format: {file_ext}")
            print(f"   Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}")
            print(f"   Tip: Convert your document to one of the supported formats.")
            return None
        
        # If already JSON, it should be in output directory, not input
        # Redirect to loader instead
        if file_ext == '.json':
            print("⚠ JSON files should be in reference/brd/output/, not input/")
            print("   Use 'Load existing BRD file' option instead.")
            return None
        
        # Extract text content based on format
        content = self._extract_text_content(file_path_obj, file_ext)
        
        if not content:
            print(f"✗ Failed to extract content from {file_path_obj}")
            return None
        
        # Use LLM to parse and convert to BRD schema
        brd = self._parse_with_llm(content, file_path_obj.name)
        
        # Save parsed BRD schema to output directory
        if brd:
            from .brd_loader import BRDLoader
            loader = BRDLoader(brd_dir=str(self.output_dir))
            output_filename = file_path_obj.stem + "_brd"
            output_path = loader.save_brd_to_file(brd, output_filename)
            print(f"✓ Parsed BRD schema saved to: {output_path}")
        
        return brd
    
    def _extract_text_content(self, file_path: Path, file_ext: str) -> Optional[str]:
        """Extract text content from various file formats."""
        try:
            if file_ext == '.txt' or file_ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_ext == '.csv':
                import csv
                content_lines = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        content_lines.append(', '.join(row))
                return '\n'.join(content_lines)
            
            elif file_ext == '.pdf':
                try:
                    import PyPDF2
                    content = []
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            content.append(page.extract_text())
                    return '\n'.join(content)
                except ImportError:
                    print("⚠ PyPDF2 not installed. Install with: pip install PyPDF2")
                    return None
            
            elif file_ext in ['.doc', '.docx']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = []
                    for paragraph in doc.paragraphs:
                        content.append(paragraph.text)
                    return '\n'.join(content)
                except ImportError:
                    print("⚠ python-docx not installed. Install with: pip install python-docx")
                    return None
            
        except Exception as e:
            print(f"⚠ Error extracting content: {e}")
            return None
        
        return None
    
    def list_available_documents(self) -> List[str]:
        """
        List all available BRD documents in the input directory.
        Excludes JSON files (which should be in output directory).
        
        Returns:
            List of document filenames
        """
        if not self.input_dir.exists():
            return []
        
        documents = []
        for file in self.input_dir.iterdir():
            if file.is_file():
                file_ext = file.suffix.lower()
                # Exclude JSON files - they should be in output directory
                if file_ext in self.SUPPORTED_FORMATS and file_ext != '.json':
                    documents.append(file.name)
        
        return sorted(documents)
    
    def _parse_with_llm(self, content: str, filename: str) -> Optional[BRDSchema]:
        """Use LLM to parse document content and convert to BRD schema."""
        if not self.llm_prompter:
            error_msg = (
                "BRD parsing requires an OpenAI API key. "
                "Please provide an API key via OPENAI_API_KEY environment variable "
                "or pass it to BRDParser constructor."
            )
            print(f"✗ Error: {error_msg}")
            return None
        
        print(f"📄 Parsing BRD document: {filename}...")
        
        # Truncate content if too long (LLM token limits)
        max_chars = 15000  # Conservative limit
        if len(content) > max_chars:
            print(f"⚠ Document is large ({len(content)} chars). Using first {max_chars} characters...")
            content = content[:max_chars] + "\n\n[... document truncated ...]"
        
        prompt = self._create_parsing_prompt(content, filename)
        response = self.llm_prompter.send_prompt(prompt)
        
        if not response:
            return None
        
        # Extract JSON from response
        brd_json = extract_json_from_response(response)
        
        if not brd_json:
            return None
        
        # Parse JSON into BRDSchema
        return self._parse_llm_brd_response(brd_json)
    
    def _create_parsing_prompt(self, content: str, filename: str) -> str:
        """Create prompt for LLM to parse BRD document."""
        prompt = f"""You are an expert in parsing Business Requirement Documents (BRD) and converting them to structured schemas.

Given the following BRD document content, extract the requirements and convert them to a structured BRD schema in JSON format.

Document: {filename}

Content:
{content}

INSTRUCTIONS:
1. Analyze the document and extract all business requirements related to API testing
2. For each requirement, identify:
   - The API endpoint path (e.g., "/users/{id}")
   - The HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
   - Test scenarios and steps
   - Priority level (critical, high, medium, low)
   - Acceptance criteria

3. Create a structured BRD schema following this exact JSON format:
{{
  "brd_id": "BRD-001",
  "title": "Extracted from document title or create appropriate title",
  "description": "Summary of the BRD",
  "api_name": "API name from document or 'Unknown'",
  "api_version": "Version if available",
  "created_date": "Current date in ISO format",
  "requirements": [
    {{
      "requirement_id": "REQ-001",
      "title": "Requirement title",
      "description": "Detailed description",
      "endpoint_path": "/endpoint/path",
      "endpoint_method": "GET",
      "priority": "high",
      "status": "pending",
      "test_scenarios": [
        {{
          "scenario_id": "SCEN-001",
          "scenario_name": "Scenario name",
          "description": "What this scenario tests",
          "test_steps": [
            "Given some precondition",
            "When an action is performed",
            "Then an expected result occurs"
          ],
          "expected_result": "Expected outcome",
          "priority": "high",
          "tags": ["positive", "smoke"]
        }}
      ],
      "acceptance_criteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "related_endpoints": []
    }}
  ],
  "metadata": {{
    "source_file": "{filename}",
    "parsed_date": "ISO date"
  }}
}}

IMPORTANT:
- Extract ALL requirements from the document
- If endpoint information is not explicit, infer from context or use "/unknown" as placeholder
- Ensure all test steps follow Gherkin format (Given/When/Then)
- Assign appropriate priorities based on document content
- Include all test scenarios mentioned in the document
- If the document format is unclear, make reasonable inferences

Return ONLY valid JSON, no additional text or markdown formatting:
"""
        return prompt
    
    
    def _parse_llm_brd_response(self, brd_json: str) -> Optional[BRDSchema]:
        """Parse LLM-generated JSON into BRDSchema object."""
        try:
            data = json.loads(brd_json)
        except json.JSONDecodeError as e:
            print(f"⚠ Error parsing BRD JSON: {e}")
            print(f"   Response preview: {brd_json[:200]}...")
            return None
        
        # Parse requirements
        requirements = []
        for req_data in data.get('requirements', []):
            test_scenarios = []
            for scenario_data in req_data.get('test_scenarios', []):
                try:
                    priority = RequirementPriority(scenario_data.get('priority', 'medium').lower())
                except ValueError:
                    priority = RequirementPriority.MEDIUM
                
                scenario = BRDTestScenario(
                    scenario_id=scenario_data.get('scenario_id', ''),
                    scenario_name=scenario_data.get('scenario_name', ''),
                    description=scenario_data.get('description', ''),
                    test_steps=scenario_data.get('test_steps', []),
                    expected_result=scenario_data.get('expected_result', ''),
                    priority=priority,
                    tags=scenario_data.get('tags', [])
                )
                test_scenarios.append(scenario)
            
            try:
                req_priority = RequirementPriority(req_data.get('priority', 'medium').lower())
            except ValueError:
                req_priority = RequirementPriority.MEDIUM
            
            try:
                req_status = RequirementStatus(req_data.get('status', 'pending').lower())
            except ValueError:
                req_status = RequirementStatus.PENDING
            
            requirement = BRDRequirement(
                requirement_id=req_data.get('requirement_id', ''),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                endpoint_path=req_data.get('endpoint_path', ''),
                endpoint_method=req_data.get('endpoint_method', ''),
                priority=req_priority,
                status=req_status,
                test_scenarios=test_scenarios,
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                related_endpoints=req_data.get('related_endpoints', [])
            )
            requirements.append(requirement)
        
        from datetime import datetime
        
        brd = BRDSchema(
            brd_id=data.get('brd_id', 'BRD-PARSED-001'),
            title=data.get('title', 'Parsed BRD Document'),
            description=data.get('description', ''),
            api_name=data.get('api_name', 'Unknown'),
            api_version=data.get('api_version', ''),
            created_date=data.get('created_date', datetime.now().isoformat()),
            requirements=requirements,
            metadata=data.get('metadata', {})
        )
        
        return brd
    
    def list_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return list(self.SUPPORTED_FORMATS.keys())

