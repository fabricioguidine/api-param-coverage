"""
Configuration Manager

Manages configuration from YAML/JSON files with environment-specific settings and customizable algorithm parameters.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv


@dataclass
class AlgorithmConfig:
    """Configuration for algorithm parameters."""
    chunk_size: int = 12
    chunking_threshold: int = 15
    max_tokens: int = 3000
    retry_attempts: int = 3
    timeout_seconds: int = 60


@dataclass
class PathsConfig:
    """Configuration for file paths."""
    schemas_dir: str = "reference/schemas"
    output_dir: str = "output"
    analytics_dir: str = "output/analytics"
    brd_input_dir: str = "reference/brd/input"
    brd_output_dir: str = "reference/brd/output"


@dataclass
class LLMConfig:
    """Configuration for LLM settings."""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 3000
    api_key: Optional[str] = None
    provider: str = "openai"


@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str = "development"
    algorithm: AlgorithmConfig = field(default_factory=AlgorithmConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    debug: bool = False
    verbose: bool = False


class ConfigManager:
    """Manages application configuration from files and environment variables."""
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_file: Path to config file (YAML or JSON). If None, looks for config.yaml or config.json
            environment: Environment name (development, production, testing). If None, uses ENV var or 'development'
        """
        # Load environment variables first
        load_dotenv()
        
        # Determine environment
        self.environment = environment or os.getenv('APP_ENV', 'development')
        
        # Find config file
        if config_file:
            self.config_path = Path(config_file)
        else:
            # Look for config files in order of preference
            config_paths = [
                Path('config.yaml'),
                Path('config.yml'),
                Path('config.json'),
                Path('config', f'{self.environment}.yaml'),
                Path('config', f'{self.environment}.yml'),
                Path('config', f'{self.environment}.json'),
            ]
            
            self.config_path = None
            for path in config_paths:
                if path.exists():
                    self.config_path = path
                    break
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file and environment."""
        # Start with defaults
        config_dict = asdict(AppConfig())
        
        # Load from file if exists
        if self.config_path and self.config_path.exists():
            file_config = self._load_config_file(self.config_path)
            if file_config:
                # Merge file config
                config_dict = self._merge_config(config_dict, file_config)
        
        # Load environment-specific overrides
        env_config = self._load_environment_config()
        if env_config:
            config_dict = self._merge_config(config_dict, env_config)
        
        # Override with environment variables
        config_dict = self._apply_environment_variables(config_dict)
        
        # Convert to AppConfig object
        return self._dict_to_config(config_dict)
    
    def _load_config_file(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from YAML or JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif config_path.suffix == '.json':
                    return json.load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
        return None
    
    def _load_environment_config(self) -> Optional[Dict[str, Any]]:
        """Load environment-specific configuration."""
        env_config_paths = [
            Path('config', f'{self.environment}.yaml'),
            Path('config', f'{self.environment}.yml'),
            Path('config', f'{self.environment}.json'),
        ]
        
        for path in env_config_paths:
            if path.exists():
                return self._load_config_file(path)
        
        return None
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # LLM settings
        if os.getenv('LLM_API_KEY'):
            config['llm']['api_key'] = os.getenv('LLM_API_KEY')
        elif os.getenv('OPENAI_API_KEY'):
            config['llm']['api_key'] = os.getenv('OPENAI_API_KEY')
        if os.getenv('LLM_PROVIDER'):
            config['llm']['provider'] = os.getenv('LLM_PROVIDER')
        if os.getenv('LLM_MODEL'):
            config['llm']['model'] = os.getenv('LLM_MODEL')
        if os.getenv('LLM_MAX_TOKENS'):
            config['llm']['max_tokens'] = int(os.getenv('LLM_MAX_TOKENS'))
        if os.getenv('LLM_TEMPERATURE'):
            config['llm']['temperature'] = float(os.getenv('LLM_TEMPERATURE'))
        
        # Algorithm settings
        if os.getenv('CHUNK_SIZE'):
            config['algorithm']['chunk_size'] = int(os.getenv('CHUNK_SIZE'))
        if os.getenv('CHUNKING_THRESHOLD'):
            config['algorithm']['chunking_threshold'] = int(os.getenv('CHUNKING_THRESHOLD'))
        if os.getenv('MAX_TOKENS'):
            config['algorithm']['max_tokens'] = int(os.getenv('MAX_TOKENS'))
        
        # Path settings
        if os.getenv('SCHEMAS_DIR'):
            config['paths']['schemas_dir'] = os.getenv('SCHEMAS_DIR')
        if os.getenv('OUTPUT_DIR'):
            config['paths']['output_dir'] = os.getenv('OUTPUT_DIR')
        if os.getenv('ANALYTICS_DIR'):
            config['paths']['analytics_dir'] = os.getenv('ANALYTICS_DIR')
        
        # App settings
        if os.getenv('APP_ENV'):
            config['environment'] = os.getenv('APP_ENV')
        if os.getenv('DEBUG'):
            config['debug'] = os.getenv('DEBUG').lower() in ['true', '1', 'yes']
        if os.getenv('VERBOSE'):
            config['verbose'] = os.getenv('VERBOSE').lower() in ['true', '1', 'yes']
        
        return config
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig object."""
        # Convert nested dictionaries to config objects
        if 'algorithm' in config_dict:
            config_dict['algorithm'] = AlgorithmConfig(**config_dict['algorithm'])
        if 'paths' in config_dict:
            config_dict['paths'] = PathsConfig(**config_dict['paths'])
        if 'llm' in config_dict:
            config_dict['llm'] = LLMConfig(**config_dict['llm'])
        
        return AppConfig(**config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports dot notation).
        
        Args:
            key: Configuration key (e.g., 'llm.model' or 'algorithm.chunk_size')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, (AppConfig, AlgorithmConfig, PathsConfig, LLMConfig)):
                value = getattr(value, k, None)
            elif isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def save_config(self, output_path: Optional[Path] = None, format: str = 'yaml') -> Path:
        """
        Save current configuration to file.
        
        Args:
            output_path: Output file path (default: config.yaml in project root)
            format: Output format ('yaml' or 'json')
            
        Returns:
            Path to saved configuration file
        """
        if output_path is None:
            output_path = Path(f'config.{format}')
        
        config_dict = asdict(self.config)
        
        # Remove API key from saved config for security
        if 'llm' in config_dict and 'api_key' in config_dict['llm']:
            config_dict['llm']['api_key'] = None
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if format == 'yaml':
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def create_default_config(self, output_path: Optional[Path] = None) -> Path:
        """
        Create a default configuration file.
        
        Args:
            output_path: Output file path (default: config.yaml)
            
        Returns:
            Path to created configuration file
        """
        default_config = AppConfig()
        return self.save_config(output_path, format='yaml')
    
    @property
    def algorithm(self) -> AlgorithmConfig:
        """Get algorithm configuration."""
        return self.config.algorithm
    
    @property
    def paths(self) -> PathsConfig:
        """Get paths configuration."""
        return self.config.paths
    
    @property
    def llm(self) -> LLMConfig:
        """Get LLM configuration."""
        return self.config.llm


