"""
Tests for the BRD Loader module.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path

from src.modules.brd.brd_loader import BRDLoader
from src.modules.brd.brd_schema import BRDSchema


class TestBRDLoader:
    """Test cases for BRDLoader class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def loader(self, temp_dir):
        """Create a BRDLoader instance with temporary directory."""
        return BRDLoader(brd_dir=temp_dir)
    
    def test_loader_default_directory(self):
        """Test BRDLoader uses correct default directory."""
        loader = BRDLoader()
        assert "reference/brd/output" in str(loader.brd_dir)
    
    @pytest.fixture
    def sample_brd_data(self):
        """Sample BRD data for testing."""
        return {
            "brd_id": "BRD-001",
            "title": "Test BRD",
            "description": "Test description",
            "api_name": "Test API",
            "api_version": "1.0.0",
            "created_date": "2024-01-01T00:00:00",
            "requirements": [
                {
                    "requirement_id": "REQ-001",
                    "title": "Test Requirement",
                    "description": "Test",
                    "endpoint_path": "/users/{id}",
                    "endpoint_method": "GET",
                    "priority": "high",
                    "status": "pending",
                    "test_scenarios": [
                        {
                            "scenario_id": "SCEN-001",
                            "scenario_name": "Test Scenario",
                            "description": "Test",
                            "test_steps": ["Given step", "When step"],
                            "expected_result": "Success",
                            "priority": "high",
                            "tags": ["positive"]
                        }
                    ],
                    "acceptance_criteria": ["Criterion 1"],
                    "related_endpoints": []
                }
            ],
            "metadata": {}
        }
    
    def test_loader_initialization(self, temp_dir):
        """Test BRDLoader initialization."""
        loader = BRDLoader(brd_dir=temp_dir)
        assert loader.brd_dir == Path(temp_dir)
        assert loader.brd_dir.exists()
    
    def test_save_and_load_brd(self, loader, sample_brd_data):
        """Test saving and loading a BRD file."""
        # Create BRD schema from data
        from src.modules.brd.brd_loader import BRDLoader
        loader_instance = BRDLoader(brd_dir=str(loader.brd_dir))
        brd = loader_instance._parse_brd_data(sample_brd_data)
        
        # Save BRD
        filepath = loader.save_brd_to_file(brd, "test_brd")
        assert filepath.exists()
        assert filepath.name == "test_brd.json"
        
        # Load BRD
        loaded_brd = loader.load_brd_from_file("test_brd")
        assert loaded_brd is not None
        assert loaded_brd.brd_id == "BRD-001"
        assert loaded_brd.title == "Test BRD"
        assert len(loaded_brd.requirements) == 1
    
    def test_list_available_brds(self, loader, sample_brd_data):
        """Test listing available BRD files."""
        # Create a BRD file
        loader_instance = BRDLoader(brd_dir=str(loader.brd_dir))
        brd = loader_instance._parse_brd_data(sample_brd_data)
        loader.save_brd_to_file(brd, "test_brd_1")
        loader.save_brd_to_file(brd, "test_brd_2")
        
        # List BRDs
        brds = loader.list_available_brds()
        assert len(brds) == 2
        assert "test_brd_1" in brds
        assert "test_brd_2" in brds
    
    def test_load_nonexistent_brd(self, loader):
        """Test loading a non-existent BRD file."""
        result = loader.load_brd_from_file("nonexistent")
        assert result is None
    
    def test_load_brd_without_extension(self, loader, sample_brd_data):
        """Test loading BRD file without .json extension."""
        loader_instance = BRDLoader(brd_dir=str(loader.brd_dir))
        brd = loader_instance._parse_brd_data(sample_brd_data)
        loader.save_brd_to_file(brd, "test_brd")
        
        # Load without extension
        loaded_brd = loader.load_brd_from_file("test_brd")
        assert loaded_brd is not None
        assert loaded_brd.brd_id == "BRD-001"

