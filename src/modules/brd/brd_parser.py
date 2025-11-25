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
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", provider: str = "openai", input_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize the BRD Parser.
        
        Args:
            api_key: LLM API key
            model: LLM model to use
            provider: LLM provider ('openai', 'anthropic', 'google', 'azure')
            input_dir: Directory where BRD documents to transform are stored (default: src/modules/brd/input_transformator)
            output_dir: Directory where parsed BRD schemas will be saved (default: src/modules/brd/input_schema)
        """
        from ..utils.constants import DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR, DEFAULT_BRD_INPUT_SCHEMA_DIR
        
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.input_dir = Path(input_dir or DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR)
        self.output_dir = Path(output_dir or DEFAULT_BRD_INPUT_SCHEMA_DIR)
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
        
        # If already JSON, it should be in input_schema directory, not input_transformator
        # Redirect to loader instead
        if file_ext == '.json':
            print("⚠ JSON files should be in src/modules/brd/input_schema/, not input_transformator/")
            print("   Use 'Load existing BRD file' option instead.")
            return None
        
        # Extract text content based on format
        content = self._extract_text_content(file_path_obj, file_ext)
        
        if not content:
            print(f"✗ Failed to extract content from {file_path_obj}")
            return None
        
        # Use transformer to convert document to BRD schema
        from .brd_transformer import BRDTransformer
        transformer = BRDTransformer(api_key=self.api_key, model=self.model, provider=self.provider)
        
        brd = transformer.transform_to_schema(
            source_data={"content": content, "filename": file_path_obj.name},
            source_type="document"
        )
        
        # Save parsed BRD schema to input_schema directory
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
    
    # _parse_with_llm method removed - now using BRDTransformer
    
    # Parsing methods moved to BRDTransformer for reuse
    
    def list_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return list(self.SUPPORTED_FORMATS.keys())

