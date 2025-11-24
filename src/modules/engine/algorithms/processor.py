"""
Schema Processor

This module contains algorithms to process and analyze schema data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


class SchemaProcessor:
    """Processes and analyzes Swagger/OpenAPI schemas."""
    
    def __init__(self, schemas_dir: str = "reference/schemas"):
        """
        Initialize the SchemaProcessor.
        
        Args:
            schemas_dir: Directory where schemas are stored
        """
        self.schemas_dir = Path(schemas_dir)
    
    def load_schema(self, schema_filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a schema from the schemas directory.
        
        Args:
            schema_filename: Name of the schema file to load
            
        Returns:
            Dictionary containing the schema, or None if not found
        """
        schema_path = self.schemas_dir / schema_filename
        
        if not schema_path.exists():
            return None
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                if schema_path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading schema: {e}")
            return None
    
    def list_available_schemas(self) -> List[str]:
        """
        List all available schema files in the schemas directory.
        
        Returns:
            List of schema filenames
        """
        if not self.schemas_dir.exists():
            return []
        
        schema_files = []
        for file in self.schemas_dir.iterdir():
            if file.is_file() and file.suffix in ['.json', '.yaml', '.yml']:
                schema_files.append(file.name)
        
        return sorted(schema_files)
    
    def process_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a schema and extract key information.
        
        This is the main algorithm that processes schema data.
        Override or extend this method to add custom processing logic.
        
        Args:
            schema: The schema dictionary to process
            
        Returns:
            Dictionary containing processed schema information
        """
        processed = {
            'info': schema.get('info', {}),
            'version': schema.get('openapi') or schema.get('swagger'),
            'paths_count': len(schema.get('paths', {})),
            'endpoints': self._extract_endpoints(schema),
            'components': self._extract_components(schema),
            'tags': schema.get('tags', []),
        }
        
        return processed
    
    def _extract_endpoints(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract endpoint information from schema.
        
        Args:
            schema: The schema dictionary
            
        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        paths = schema.get('paths', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoints.append({
                        'path': path,
                        'method': method.upper(),
                        'operation_id': details.get('operationId'),
                        'summary': details.get('summary'),
                        'tags': details.get('tags', [])
                    })
        
        return endpoints
    
    def _extract_components(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract components information from schema.
        
        Args:
            schema: The schema dictionary
            
        Returns:
            Dictionary with components information
        """
        # Handle both OpenAPI 3.x and Swagger 2.0
        components = schema.get('components', {})
        definitions = schema.get('definitions', {})
        
        # OpenAPI 3.x uses components
        if components:
            return {
                'schemas_count': len(components.get('schemas', {})),
                'responses_count': len(components.get('responses', {})),
                'parameters_count': len(components.get('parameters', {})),
                'security_schemes_count': len(components.get('securitySchemes', {})),
                'request_bodies_count': len(components.get('requestBodies', {})),
                'headers_count': len(components.get('headers', {})),
                'examples_count': len(components.get('examples', {})),
                'links_count': len(components.get('links', {})),
                'callbacks_count': len(components.get('callbacks', {}))
            }
        # Swagger 2.0 uses definitions, parameters, responses at root
        else:
            root_params = schema.get('parameters', {})
            root_responses = schema.get('responses', {})
            security_defs = schema.get('securityDefinitions', {})
            
            return {
                'schemas_count': len(definitions),
                'responses_count': len(root_responses),
                'parameters_count': len(root_params),
                'security_schemes_count': len(security_defs),
                'request_bodies_count': 0,
                'headers_count': 0,
                'examples_count': 0,
                'links_count': 0,
                'callbacks_count': 0
            }
    
    def process_schema_file(self, schema_filename: str) -> Optional[Dict[str, Any]]:
        """
        Load and process a schema file.
        
        Args:
            schema_filename: Name of the schema file to process
            
        Returns:
            Processed schema information, or None if loading failed
        """
        schema = self.load_schema(schema_filename)
        if schema is None:
            return None
        
        return self.process_schema(schema)

