"""
Tests for the Configuration Manager module.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
import json
import yaml

from src.modules.config.config_manager import ConfigManager, AppConfig, AlgorithmConfig, PathsConfig, LLMConfig


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_yaml_config(self, temp_dir):
        """Create a sample YAML config file."""
        config_path = Path(temp_dir) / "config.yaml"
        config_data = {
            'environment': 'testing',
            'algorithm': {
                'chunk_size': 20,
                'chunking_threshold': 25,
                'max_tokens': 4000
            },
            'llm': {
                'model': 'gpt-3.5-turbo',
                'temperature': 0.8
            },
            'paths': {
                'output_dir': 'test_output'
            },
            'debug': True
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        return config_path
    
    @pytest.fixture
    def sample_json_config(self, temp_dir):
        """Create a sample JSON config file."""
        config_path = Path(temp_dir) / "config.json"
        config_data = {
            'environment': 'testing',
            'algorithm': {
                'chunk_size': 15,
                'max_tokens': 5000
            },
            'llm': {
                'model': 'gpt-4-turbo'
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        return config_path
    
    def test_config_manager_defaults(self):
        """Test ConfigManager with default configuration."""
        manager = ConfigManager()
        
        assert manager.config.environment == 'development'
        assert manager.config.algorithm.chunk_size == 12
        assert manager.config.llm.model == 'gpt-4'
        assert isinstance(manager.config, AppConfig)
    
    def test_config_manager_with_yaml_file(self, sample_yaml_config):
        """Test ConfigManager loading YAML config file."""
        manager = ConfigManager(config_file=str(sample_yaml_config))
        
        assert manager.config.environment == 'testing'
        assert manager.config.algorithm.chunk_size == 20
        assert manager.config.algorithm.chunking_threshold == 25
        assert manager.config.algorithm.max_tokens == 4000
        assert manager.config.llm.model == 'gpt-3.5-turbo'
        assert manager.config.llm.temperature == 0.8
        assert manager.config.paths.output_dir == 'test_output'
        assert manager.config.debug is True
    
    def test_config_manager_with_json_file(self, sample_json_config):
        """Test ConfigManager loading JSON config file."""
        manager = ConfigManager(config_file=str(sample_json_config))
        
        assert manager.config.environment == 'testing'
        assert manager.config.algorithm.chunk_size == 15
        assert manager.config.algorithm.max_tokens == 5000
        assert manager.config.llm.model == 'gpt-4-turbo'
    
    def test_config_manager_environment_override(self, temp_dir):
        """Test environment-specific configuration."""
        # Create environment-specific config
        env_dir = Path(temp_dir) / "config"
        env_dir.mkdir()
        env_config_path = env_dir / "testing.yaml"
        
        env_config = {
            'algorithm': {
                'chunk_size': 30
            },
            'debug': True
        }
        with open(env_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(env_config, f)
        
        # Change to temp_dir and test
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            manager = ConfigManager(environment='testing')
            assert manager.config.algorithm.chunk_size == 30
            assert manager.config.debug is True
        finally:
            os.chdir(original_cwd)
    
    def test_config_manager_environment_variables(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key-123')
        monkeypatch.setenv('LLM_MODEL', 'gpt-3.5-turbo')
        monkeypatch.setenv('CHUNK_SIZE', '25')
        monkeypatch.setenv('OUTPUT_DIR', '/custom/output')
        monkeypatch.setenv('DEBUG', 'true')
        
        manager = ConfigManager()
        
        assert manager.config.llm.api_key == 'test-key-123'
        assert manager.config.llm.model == 'gpt-3.5-turbo'
        assert manager.config.algorithm.chunk_size == 25
        assert manager.config.paths.output_dir == '/custom/output'
        assert manager.config.debug is True
    
    def test_get_method_dot_notation(self):
        """Test get method with dot notation."""
        manager = ConfigManager()
        
        assert manager.get('llm.model') == 'gpt-4'
        assert manager.get('algorithm.chunk_size') == 12
        assert manager.get('paths.output_dir') == 'output'
        assert manager.get('nonexistent.key', 'default') == 'default'
    
    def test_save_config_yaml(self, temp_dir):
        """Test saving configuration to YAML file."""
        manager = ConfigManager()
        output_path = Path(temp_dir) / "saved_config.yaml"
        
        saved_path = manager.save_config(output_path, format='yaml')
        
        assert saved_path.exists()
        assert saved_path.suffix == '.yaml'
        
        # Verify saved content
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)
            assert 'algorithm' in saved_data
            assert 'llm' in saved_data
            # API key should be None in saved config
            assert saved_data['llm']['api_key'] is None
    
    def test_save_config_json(self, temp_dir):
        """Test saving configuration to JSON file."""
        manager = ConfigManager()
        output_path = Path(temp_dir) / "saved_config.json"
        
        saved_path = manager.save_config(output_path, format='json')
        
        assert saved_path.exists()
        assert saved_path.suffix == '.json'
        
        # Verify saved content
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            assert 'algorithm' in saved_data
            assert 'llm' in saved_data
    
    def test_create_default_config(self, temp_dir):
        """Test creating default configuration file."""
        manager = ConfigManager()
        output_path = Path(temp_dir) / "default_config.yaml"
        
        created_path = manager.create_default_config(output_path)
        
        assert created_path.exists()
        
        # Verify it can be loaded
        new_manager = ConfigManager(config_file=str(created_path))
        assert new_manager.config.algorithm.chunk_size == 12
        assert new_manager.config.llm.model == 'gpt-4'
    
    def test_config_properties(self):
        """Test config property accessors."""
        manager = ConfigManager()
        
        assert isinstance(manager.algorithm, AlgorithmConfig)
        assert isinstance(manager.paths, PathsConfig)
        assert isinstance(manager.llm, LLMConfig)
        
        assert manager.algorithm.chunk_size == 12
        assert manager.paths.output_dir == 'output'
        assert manager.llm.model == 'gpt-4'
    
    def test_config_merge(self, sample_yaml_config):
        """Test configuration merging."""
        manager = ConfigManager(config_file=str(sample_yaml_config))
        
        # Should have file values
        assert manager.config.algorithm.chunk_size == 20
        
        # Should have defaults for unspecified values
        assert manager.config.algorithm.retry_attempts == 3  # default
        assert manager.config.paths.schemas_dir == 'reference/schemas'  # default
    
    def test_config_with_nonexistent_file(self):
        """Test ConfigManager with nonexistent config file."""
        manager = ConfigManager(config_file='nonexistent_config.yaml')
        
        # Should use defaults
        assert manager.config.environment == 'development'
        assert manager.config.algorithm.chunk_size == 12


