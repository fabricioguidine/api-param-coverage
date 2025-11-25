"""
Schema Fetcher Module

This module handles downloading and saving Swagger/OpenAPI schemas from URLs.
"""

import json
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import yaml
from .schema_validator import SchemaValidator


class SchemaFetcher:
    """Handles fetching and saving Swagger/OpenAPI schemas."""
    
    def __init__(self, schemas_dir: Optional[str] = None):
        """
        Initialize the SchemaFetcher.
        
        Args:
            schemas_dir: Directory where schemas will be saved (required, typically a temp directory)
        """
        if schemas_dir is None:
            import tempfile
            schemas_dir = tempfile.mkdtemp(prefix="api_param_coverage_")
        self.schemas_dir = Path(schemas_dir)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_schema(self, url: str) -> Optional[dict]:
        """
        Fetch a Swagger/OpenAPI schema from a URL.
        
        Args:
            url: URL to the Swagger/OpenAPI schema
            
        Returns:
            Dictionary containing the schema, or None if fetch failed
        """
        try:
            # Set headers to accept both JSON and YAML
            headers = {
                'Accept': 'application/json, application/yaml, text/yaml, */*'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Detect content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Try to parse as JSON first
            try:
                schema = response.json()
                # Validate and normalize
                validator = SchemaValidator()
                is_valid, error = validator.validate_schema(schema)
                if is_valid:
                    schema = validator.normalize_schema(schema)
                    schema_info = validator.get_schema_info(schema)
                    print(f"✓ Detected: {schema_info['type'].upper()} {schema_info['version']} - {schema_info['title']}")
                    return schema
                else:
                    print(f"⚠ Schema validation warning: {error}")
                    # Still return it, but warn
                    return validator.normalize_schema(schema)
            except json.JSONDecodeError:
                # If not JSON, try YAML
                try:
                    yaml_result = yaml.safe_load(response.text)
                    # Check if YAML parsing returned a dictionary (valid schema)
                    if isinstance(yaml_result, dict):
                        # Validate and normalize
                        validator = SchemaValidator()
                        is_valid, error = validator.validate_schema(yaml_result)
                        if is_valid:
                            yaml_result = validator.normalize_schema(yaml_result)
                            schema_info = validator.get_schema_info(yaml_result)
                            print(f"✓ Detected: {schema_info['type'].upper()} {schema_info['version']} - {schema_info['title']}")
                            return yaml_result
                        else:
                            print(f"⚠ Schema validation warning: {error}")
                            return validator.normalize_schema(yaml_result)
                    else:
                        print("Error: Schema is neither valid JSON nor YAML")
                        return None
                except yaml.YAMLError as e:
                    print(f"Error: Invalid YAML format - {e}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching schema: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing schema: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def save_schema(self, schema: dict, url: str, format: str = "json") -> Optional[str]:
        """
        Save a schema to disk.
        
        Args:
            schema: The schema dictionary to save
            url: Original URL (used to generate filename)
            format: Format to save in ('json' or 'yaml')
            
        Returns:
            Path to saved file, or None if save failed
        """
        try:
            # Generate filename from URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace(".", "_")
            path_parts = parsed_url.path.strip("/").replace("/", "_")
            
            if path_parts:
                filename = f"{domain}_{path_parts}"
            else:
                filename = domain
            
            # Add extension
            if format.lower() == "yaml":
                filename += ".yaml"
            else:
                filename += ".json"
            
            filepath = self.schemas_dir / filename
            
            # Save the schema
            with open(filepath, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(schema, f, indent=2, ensure_ascii=False)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error saving schema: {e}")
            return None
    
    def download_and_save(self, url: str, format: str = "json") -> Optional[str]:
        """
        Download a schema from URL and save it.
        
        Args:
            url: URL to the Swagger/OpenAPI schema
            format: Format to save in ('json' or 'yaml')
            
        Returns:
            Path to saved file, or None if operation failed
        """
        print(f"Fetching schema from: {url}")
        schema = self.fetch_schema(url)
        
        if schema is None:
            return None
        
        print(f"Saving schema...")
        filepath = self.save_schema(schema, url, format)
        
        if filepath:
            print(f"Schema saved to: {filepath}")
        
        return filepath

