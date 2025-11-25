"""
Schema Validator

Validates and detects OpenAPI/Swagger schema types and versions.
"""

from typing import Dict, Any, Optional, Tuple
import re


class SchemaValidator:
    """Validates and detects OpenAPI/Swagger schema types."""
    
    # Supported OpenAPI/Swagger versions
    SWAGGER_2_0 = "2.0"
    OPENAPI_3_0 = "3.0.0"
    OPENAPI_3_1 = "3.1.0"
    
    def __init__(self):
        """Initialize the SchemaValidator."""
        pass
    
    def detect_schema_type(self, schema: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Detect the schema type and version.
        
        Args:
            schema: The schema dictionary
            
        Returns:
            Tuple of (schema_type, version) where:
            - schema_type: 'swagger', 'openapi', or 'unknown'
            - version: version string or None
        """
        if not isinstance(schema, dict):
            return ('unknown', None)
        
        # Check for OpenAPI 3.x
        if 'openapi' in schema:
            version = schema.get('openapi', '')
            # Normalize version (handle 3.0, 3.0.0, 3.1, 3.1.0, etc.)
            if version.startswith('3.0'):
                return ('openapi', '3.0.0')
            elif version.startswith('3.1'):
                return ('openapi', '3.1.0')
            elif version.startswith('3.'):
                return ('openapi', version)
            else:
                return ('openapi', version)
        
        # Check for Swagger 2.0
        if 'swagger' in schema:
            version = schema.get('swagger', '')
            if version.startswith('2.'):
                return ('swagger', '2.0')
            else:
                return ('swagger', version)
        
        # Try to infer from structure
        if 'paths' in schema and 'info' in schema:
            # Has OpenAPI/Swagger structure but no version field
            # Assume OpenAPI 3.0 if has 'components', Swagger 2.0 if has 'definitions'
            if 'components' in schema:
                return ('openapi', '3.0.0')
            elif 'definitions' in schema:
                return ('swagger', '2.0')
            else:
                return ('openapi', '3.0.0')  # Default to OpenAPI 3.0
        
        return ('unknown', None)
    
    def validate_schema(self, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate that a schema is a valid OpenAPI/Swagger schema.
        
        Args:
            schema: The schema dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(schema, dict):
            return (False, "Schema must be a dictionary/object")
        
        # Check for required top-level fields
        if 'paths' not in schema:
            return (False, "Schema missing required 'paths' field")
        
        if 'info' not in schema:
            return (False, "Schema missing required 'info' field")
        
        # Validate info object
        info = schema.get('info', {})
        if not isinstance(info, dict):
            return (False, "'info' must be an object")
        
        # Validate paths object
        paths = schema.get('paths', {})
        if not isinstance(paths, dict):
            return (False, "'paths' must be an object")
        
        # Check schema type
        schema_type, version = self.detect_schema_type(schema)
        if schema_type == 'unknown':
            return (False, "Could not detect schema type (missing 'openapi' or 'swagger' field)")
        
        return (True, None)
    
    def normalize_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize schema to handle variations in structure.
        
        Args:
            schema: The schema dictionary to normalize
            
        Returns:
            Normalized schema dictionary
        """
        normalized = schema.copy()
        
        # Ensure info exists
        if 'info' not in normalized:
            normalized['info'] = {}
        
        # Ensure paths exists
        if 'paths' not in normalized:
            normalized['paths'] = {}
        
        # Normalize OpenAPI 3.x structure
        schema_type, version = self.detect_schema_type(normalized)
        
        if schema_type == 'openapi':
            # Ensure components exists
            if 'components' not in normalized:
                normalized['components'] = {}
            
            # Normalize components structure
            components = normalized.get('components', {})
            for component_type in ['schemas', 'responses', 'parameters', 'examples', 
                                  'requestBodies', 'headers', 'securitySchemes', 'links', 'callbacks']:
                if component_type not in components:
                    components[component_type] = {}
        
        elif schema_type == 'swagger':
            # Ensure definitions exists for Swagger 2.0
            if 'definitions' not in normalized:
                normalized['definitions'] = {}
            
            # Ensure parameters exists
            if 'parameters' not in normalized:
                normalized['parameters'] = {}
            
            # Ensure responses exists
            if 'responses' not in normalized:
                normalized['responses'] = {}
        
        return normalized
    
    def get_schema_info(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract schema information.
        
        Args:
            schema: The schema dictionary
            
        Returns:
            Dictionary with schema information
        """
        schema_type, version = self.detect_schema_type(schema)
        is_valid, error = self.validate_schema(schema)
        
        info = schema.get('info', {})
        paths = schema.get('paths', {})
        
        # Count endpoints
        endpoint_count = 0
        for path_item in paths.values():
            if isinstance(path_item, dict):
                for method in path_item.keys():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                        endpoint_count += 1
        
        return {
            'type': schema_type,
            'version': version,
            'is_valid': is_valid,
            'error': error,
            'title': info.get('title', 'Unknown'),
            'version_info': info.get('version', 'Unknown'),
            'description': info.get('description', ''),
            'endpoint_count': endpoint_count,
            'path_count': len(paths),
            'has_components': 'components' in schema or 'definitions' in schema,
            'has_security': 'securityDefinitions' in schema or 'securitySchemes' in schema.get('components', {}),
        }

