"""
Tests for the BRD Parser module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

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
        assert "reference/brd/input" in input_str
        assert "reference/brd/output" in output_str
    
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

