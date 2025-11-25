"""
Tests for the BRD Parser module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.modules.brd.brd_parser import BRDParser
from src.modules.brd.brd_schema import BRDSchema


class TestBRDParser:
    """Test cases for BRDParser class."""
    
    @pytest.fixture
    def temp_input_dir(self):
        """Create a temporary input directory."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def parser(self, temp_input_dir, temp_output_dir):
        """Create a BRDParser instance with temporary directories."""
        return BRDParser(
            api_key="test-key",
            model="gpt-4",
            input_dir=temp_input_dir,
            output_dir=temp_output_dir
        )
    
    def test_parser_initialization(self, temp_input_dir, temp_output_dir):
        """Test BRDParser initialization."""
        parser = BRDParser(
            input_dir=temp_input_dir,
            output_dir=temp_output_dir
        )
        
        assert parser.input_dir == Path(temp_input_dir)
        assert parser.output_dir == Path(temp_output_dir)
        assert parser.input_dir.exists()
        assert parser.output_dir.exists()
    
    def test_parser_default_directories(self):
        """Test BRDParser uses correct default directories."""
        parser = BRDParser()
        # Handle both Windows and Unix path separators
        input_str = str(parser.input_dir).replace("\\", "/")
        output_str = str(parser.output_dir).replace("\\", "/")
        assert "input_transformator" in input_str
        assert "input_schema" in output_str
    
    def test_list_available_documents(self, parser, temp_input_dir):
        """Test listing available documents."""
        # Create test documents
        test_files = [
            "test.pdf",
            "test.txt",
            "test.csv",
            "test.doc",
            "test.json"  # Should be excluded
        ]
        
        for filename in test_files:
            file_path = Path(temp_input_dir) / filename
            file_path.touch()
        
        documents = parser.list_available_documents()
        
        # Should include supported formats but not JSON
        assert "test.txt" in documents
        assert "test.csv" in documents
        assert "test.pdf" in documents
        assert "test.json" not in documents  # JSON should be in output, not input
    
    def test_parse_nonexistent_document(self, parser):
        """Test parsing a non-existent document."""
        result = parser.parse_document("nonexistent.txt")
        assert result is None
    
    def test_parse_unsupported_format(self, parser, temp_input_dir):
        """Test parsing an unsupported file format."""
        test_file = Path(temp_input_dir) / "test.xyz"
        test_file.write_text("test content")
        
        result = parser.parse_document("test.xyz")
        assert result is None
    
    def test_parse_json_in_input_directory(self, parser, temp_input_dir):
        """Test that JSON files in input directory are rejected."""
        test_file = Path(temp_input_dir) / "test.json"
        test_file.write_text('{"test": "data"}')
        
        result = parser.parse_document("test.json")
        assert result is None  # Should reject JSON in input directory
    
    def test_extract_text_content_txt(self, parser, temp_input_dir):
        """Test text extraction from TXT file."""
        test_file = Path(temp_input_dir) / "test.txt"
        test_content = "This is a test document\nWith multiple lines\nAnd some content"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = parser._extract_text_content(test_file, '.txt')
        assert content == test_content
    
    def test_extract_text_content_markdown(self, parser, temp_input_dir):
        """Test text extraction from Markdown file."""
        test_file = Path(temp_input_dir) / "test.md"
        test_content = "# Test Document\n\nThis is **markdown** content"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = parser._extract_text_content(test_file, '.md')
        assert content == test_content
    
    def test_extract_text_content_csv(self, parser, temp_input_dir):
        """Test text extraction from CSV file."""
        test_file = Path(temp_input_dir) / "test.csv"
        test_file.write_text("col1,col2,col3\nval1,val2,val3\nval4,val5,val6", encoding='utf-8')
        
        content = parser._extract_text_content(test_file, '.csv')
        assert content is not None
        assert "col1" in content
        assert "val1" in content
    
    def test_extract_text_content_encoding_error(self, parser, temp_input_dir):
        """Test handling of encoding errors in text files."""
        test_file = Path(temp_input_dir) / "test.txt"
        # Write binary data that can't be decoded as UTF-8
        test_file.write_bytes(b'\xff\xfe\x00\x01')
        
        content = parser._extract_text_content(test_file, '.txt')
        # Should handle error gracefully
        assert content is None or isinstance(content, str)
    
    def test_extract_text_content_pdf_missing_library(self, parser, temp_input_dir, monkeypatch):
        """Test PDF extraction when PyPDF2 is not installed."""
        test_file = Path(temp_input_dir) / "test.pdf"
        test_file.write_bytes(b'%PDF-1.4 fake pdf content')
        
        # Mock ImportError
        import sys
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'PyPDF2':
                raise ImportError("No module named 'PyPDF2'")
            return original_import(name, *args, **kwargs)
        
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        content = parser._extract_text_content(test_file, '.pdf')
        assert content is None
    
    def test_extract_text_content_word_missing_library(self, parser, temp_input_dir, monkeypatch):
        """Test Word extraction when python-docx is not installed."""
        test_file = Path(temp_input_dir) / "test.docx"
        test_file.write_bytes(b'PK\x03\x04 fake docx content')
        
        # Mock ImportError
        import sys
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == 'docx':
                raise ImportError("No module named 'docx'")
            return original_import(name, *args, **kwargs)
        
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        content = parser._extract_text_content(test_file, '.docx')
        assert content is None
    
    def test_parse_document_absolute_path(self, parser, temp_input_dir):
        """Test parsing document using absolute path."""
        test_file = Path(temp_input_dir) / "test.txt"
        test_content = "Test content for absolute path"
        test_file.write_text(test_content, encoding='utf-8')
        
        # Parse using absolute path - now uses BRDTransformer
        # Without API key, transformer will fail, so result should be None
        result = parser.parse_document(str(test_file))
        # Should attempt to read the file even if transformation fails
        assert result is None  # Transformation fails without API key
    
    def test_parse_document_file_not_found(self, parser):
        """Test parsing non-existent file."""
        result = parser.parse_document("/nonexistent/path/file.txt")
        assert result is None
    
    def test_list_available_documents_empty_directory(self, parser, temp_input_dir):
        """Test listing documents in empty directory."""
        documents = parser.list_available_documents()
        assert documents == []
    
    def test_list_available_documents_mixed_formats(self, parser, temp_input_dir):
        """Test listing documents with mixed supported/unsupported formats."""
        test_files = [
            "test.txt",
            "test.pdf",
            "test.xyz",  # Unsupported
            "test.json",  # Should be excluded
            "test.csv",
            "test.md"
        ]
        
        for filename in test_files:
            file_path = Path(temp_input_dir) / filename
            file_path.touch()
        
        documents = parser.list_available_documents()
        
        assert "test.txt" in documents
        assert "test.pdf" in documents
        assert "test.csv" in documents
        assert "test.md" in documents
        assert "test.xyz" not in documents
        assert "test.json" not in documents
    
    def test_parser_without_api_key(self, temp_input_dir, temp_output_dir):
        """Test parser initialization without API key."""
        parser = BRDParser(
            api_key=None,
            input_dir=temp_input_dir,
            output_dir=temp_output_dir
        )
        
        assert parser.api_key is None
        assert parser.llm_prompter is None
    
    def test_parse_document_without_llm_prompter(self, temp_input_dir, temp_output_dir):
        """Test parsing document when LLM prompter is not available."""
        parser = BRDParser(
            api_key=None,  # No API key, so no LLM prompter
            input_dir=temp_input_dir,
            output_dir=temp_output_dir
        )
        
        test_file = Path(temp_input_dir) / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')
        
        result = parser.parse_document("test.txt")
        # Should fail gracefully when LLM is not available
        assert result is None

