"""
Tests for the CSVGenerator module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.modules.engine.algorithms.csv_generator import CSVGenerator


class TestCSVGenerator:
    """Test cases for CSVGenerator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create a CSVGenerator instance with temporary directory."""
        return CSVGenerator(output_dir=temp_dir)
    
    @pytest.fixture
    def sample_gherkin(self):
        """Sample Gherkin content."""
        return """Feature: Test API

  Scenario: Get user by ID
    Given I have a valid user ID "123"
    When I send a GET request to "/users/{id}"
    Then I should receive a 200 OK response
    And the response should contain user data

  Scenario: Get user with invalid ID
    Given I have an invalid user ID "999"
    When I send a GET request to "/users/{id}"
    Then I should receive a 404 Not Found response
"""
    
    def test_parse_gherkin_basic(self, generator, sample_gherkin):
        """Test parsing basic Gherkin content."""
        csv_data = generator.parse_gherkin_to_csv_data(sample_gherkin)
        
        assert len(csv_data) == 2
        assert csv_data[0]["Feature"] == "Test API"
        assert "Get user by ID" in csv_data[0]["Scenario"]
        assert "Given" in csv_data[0]["Given"]
    
    def test_parse_gherkin_empty(self, generator):
        """Test parsing empty Gherkin content."""
        csv_data = generator.parse_gherkin_to_csv_data("")
        assert len(csv_data) == 0
    
    def test_parse_gherkin_with_markdown(self, generator):
        """Test parsing Gherkin wrapped in markdown code blocks."""
        gherkin_with_markdown = """```gherkin
Feature: Test API

  Scenario: Test
    Given the API is available
    When I make a request
    Then I get a response
```
"""
        csv_data = generator.parse_gherkin_to_csv_data(gherkin_with_markdown)
        assert len(csv_data) > 0
    
    def test_save_to_csv(self, generator):
        """Test saving data to CSV."""
        data = [
            {
                "Feature": "Test",
                "Scenario": "Test scenario",
                "Tags": "",
                "Given": "Given step",
                "When": "When step",
                "Then": "Then step",
                "All Steps": "All steps"
            }
        ]
        
        filepath = generator.save_to_csv(data, "test")
        
        assert Path(filepath).exists()
        assert "gherkin_scenarios_test_" in filepath
        assert filepath.endswith(".csv")
    
    def test_save_to_csv_empty_data(self, generator):
        """Test saving empty data raises error."""
        with pytest.raises(ValueError, match="No data to write"):
            generator.save_to_csv([], "test")
    
    def test_gherkin_to_csv(self, generator, sample_gherkin):
        """Test converting Gherkin to CSV."""
        filepath = generator.gherkin_to_csv(sample_gherkin, "test_api")
        
        assert Path(filepath).exists()
        assert "gherkin_scenarios_test_api_" in filepath
        
        # Verify CSV has content
        with open(filepath, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 1  # Header + at least one data row
    
    def test_gherkin_to_csv_empty_content(self, generator):
        """Test handling empty Gherkin content."""
        filepath = generator.gherkin_to_csv("", "test")
        
        assert Path(filepath).exists()
        # Should create a row with error message
        with open(filepath, 'r') as f:
            content = f.read()
            assert "No Scenarios Generated" in content or "Empty Response" in content
    
    def test_clean_gherkin_content(self, generator):
        """Test cleaning markdown from Gherkin content."""
        content = "```gherkin\nFeature: Test\n```"
        cleaned = generator._clean_gherkin_content(content)
        
        assert "```" not in cleaned
        assert "Feature: Test" in cleaned

