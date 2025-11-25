"""
Schema Analyzer

Analyzes OpenAPI/Swagger schemas to extract structured information
for building test traceability matrices.
"""

import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import re
import yaml


class SchemaAnalyzer:
    """Analyzes OpenAPI/Swagger schemas for test traceability matrix generation."""
    
    def __init__(self, schemas_dir: str = "schemas"):
        """
        Initialize the SchemaAnalyzer.
        
        Args:
            schemas_dir: Directory where schemas are stored
        """
        self.schemas_dir = Path(schemas_dir)
        self._resolved_refs: Dict[str, Any] = {}
        self._visited_refs: Set[str] = set()
    
    def analyze_schema_file(self, schema_filename: str) -> Dict[str, Any]:
        """
        Load and analyze a schema file.
        
        Args:
            schema_filename: Name of the schema file to analyze
            
        Returns:
            Structured analysis result in the required JSON format
        """
        schema_path = self.schemas_dir / schema_filename
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_filename}")
        
        # Load schema
        with open(schema_path, 'r', encoding='utf-8') as f:
            if schema_path.suffix in ['.yaml', '.yml']:
                schema = yaml.safe_load(f)
            else:
                schema = json.load(f)
        
        return self.analyze_schema(schema)
    
    def analyze_schema_to_json(self, schema: Dict[str, Any], indent: int = 2) -> str:
        """
        Analyze schema and return as formatted JSON string.
        
        Args:
            schema: The schema dictionary to analyze
            indent: JSON indentation level
            
        Returns:
            Formatted JSON string
        """
        result = self.analyze_schema(schema)
        return json.dumps(result, indent=indent, ensure_ascii=False)
    
    def analyze_schema_file_to_json(self, schema_filename: str, indent: int = 2) -> str:
        """
        Load, analyze schema file and return as formatted JSON string.
        
        Args:
            schema_filename: Name of the schema file to analyze
            indent: JSON indentation level
            
        Returns:
            Formatted JSON string
        """
        result = self.analyze_schema_file(schema_filename)
        return json.dumps(result, indent=indent, ensure_ascii=False)
    
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an OpenAPI/Swagger schema.
        
        Args:
            schema: The schema dictionary to analyze
            
        Returns:
            Structured analysis result in the required JSON format
        """
        # Reset state
        self._resolved_refs = {}
        self._visited_refs = set()
        
        # Resolve all $ref references first
        self._resolve_all_refs(schema)
        
        # Extract endpoints
        endpoints = []
        paths = schema.get('paths', {})
        
        for path, path_item in paths.items():
            # Handle both OpenAPI 3.x and Swagger 2.0 path item structure
            if not isinstance(path_item, dict):
                continue
            
            # Get common parameters for this path (OpenAPI 3.x and Swagger 2.0)
            common_params = path_item.get('parameters', [])
            
            # Process each HTTP method
            for method, operation in path_item.items():
                # Skip non-HTTP method keys (like $ref, summary, description, servers, etc.)
                if method.startswith('$') or method.lower() in ['summary', 'description', 'servers', 'parameters']:
                    continue
                
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                    if isinstance(operation, dict):
                        endpoint_data = self._analyze_endpoint(
                            path, method.upper(), operation, common_params, schema
                        )
                        endpoints.append(endpoint_data)
        
        return {"endpoints": endpoints}
    
    def _resolve_all_refs(self, schema: Dict[str, Any]) -> None:
        """Resolve all $ref references in the schema."""
        # Handle both OpenAPI 3.x and Swagger 2.0
        components = schema.get('components', {})
        definitions = schema.get('definitions', {})
        
        # OpenAPI 3.x uses components
        if components:
            # Store all component schemas
            if 'schemas' in components:
                for name, schema_def in components['schemas'].items():
                    self._resolved_refs[f"#/components/schemas/{name}"] = schema_def
            
            # Store parameters
            if 'parameters' in components:
                for name, param_def in components['parameters'].items():
                    self._resolved_refs[f"#/components/parameters/{name}"] = param_def
            
            # Store responses
            if 'responses' in components:
                for name, response_def in components['responses'].items():
                    self._resolved_refs[f"#/components/responses/{name}"] = response_def
            
            # Store request bodies
            if 'requestBodies' in components:
                for name, body_def in components['requestBodies'].items():
                    self._resolved_refs[f"#/components/requestBodies/{name}"] = body_def
        
        # Swagger 2.0 uses definitions, parameters, responses at root level
        if definitions:
            for name, schema_def in definitions.items():
                self._resolved_refs[f"#/definitions/{name}"] = schema_def
        
        # Swagger 2.0 parameters
        root_params = schema.get('parameters', {})
        if root_params:
            for name, param_def in root_params.items():
                self._resolved_refs[f"#/parameters/{name}"] = param_def
        
        # Swagger 2.0 responses
        root_responses = schema.get('responses', {})
        if root_responses:
            for name, response_def in root_responses.items():
                self._resolved_refs[f"#/responses/{name}"] = response_def
    
    def _resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a $ref reference."""
        if ref in self._resolved_refs:
            return self._resolved_refs[ref]
        
        # Handle local references
        if ref.startswith('#/'):
            parts = ref.split('/')[1:]
            # Try to resolve from components
            if len(parts) >= 3 and parts[0] in ['components', 'definitions']:
                ref_key = f"#/{'/'.join(parts)}"
                if ref_key in self._resolved_refs:
                    return self._resolved_refs[ref_key]
        
        return None
    
    def _analyze_endpoint(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any],
        common_params: List[Dict[str, Any]],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze a single endpoint."""
        # Combine operation parameters with common path parameters
        operation_params = operation.get('parameters', [])
        all_params = common_params + operation_params
        
        # Analyze parameters
        parameters = []
        
        # Path parameters (from path template)
        path_param_names = set(re.findall(r'\{([^}]+)\}', path))
        for param_name in path_param_names:
            # Find parameter definition
            param_def = self._find_parameter(all_params, param_name, 'path')
            if param_def:
                param_data = self._analyze_parameter(param_def, 'path', schema)
                parameters.append(param_data)
        
        # Query, header, cookie parameters
        for param in all_params:
            param_def = self._resolve_parameter(param, schema)
            location = param_def.get('in', 'query')
            
            if location in ['query', 'header', 'cookie']:
                param_data = self._analyze_parameter(param_def, location, schema)
                parameters.append(param_data)
        
        # Request body - OpenAPI 3.x uses requestBody
        request_body = operation.get('requestBody', {})
        if request_body:
            body_params = self._analyze_request_body(request_body, schema)
            parameters.extend(body_params)
        
        # Swagger 2.0 uses body parameter with 'in': 'body'
        for param in all_params:
            param_def = self._resolve_parameter(param, schema)
            if param_def.get('in') == 'body':
                # Swagger 2.0 body parameter
                body_schema = param_def.get('schema', {})
                if '$ref' in body_schema:
                    body_schema = self._resolve_ref(body_schema['$ref']) or body_schema
                
                body_params = self._extract_schema_properties(
                    body_schema, 'body', schema, prefix=''
                )
                parameters.extend(body_params)
        
        # Response schemas (2xx only)
        responses = operation.get('responses', {})
        response_params = self._analyze_responses(responses, schema)
        parameters.extend(response_params)
        
        return {
            "path": path,
            "method": method,
            "parameters": parameters
        }
    
    def _find_parameter(
        self,
        params: List[Dict[str, Any]],
        name: str,
        location: str
    ) -> Optional[Dict[str, Any]]:
        """Find a parameter by name and location."""
        for param in params:
            param_def = param
            if '$ref' in param:
                param_def = self._resolve_ref(param['$ref'])
            
            if param_def and param_def.get('name') == name and param_def.get('in') == location:
                return param_def
        
        return None
    
    def _resolve_parameter(self, param: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a parameter, handling $ref references."""
        if '$ref' in param:
            resolved = self._resolve_ref(param['$ref'])
            if resolved:
                return resolved
        return param
    
    def _analyze_parameter(
        self,
        param: Dict[str, Any],
        location: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze a single parameter."""
        # Get schema
        param_schema = param.get('schema', {})
        if '$ref' in param_schema:
            param_schema = self._resolve_ref(param_schema['$ref']) or param_schema
        
        # Extract constraints
        constraints = self._extract_constraints(param_schema)
        
        # Compute iteration count
        iteration_count = self._compute_iteration_count(param_schema, constraints)
        
        # Generate notes
        notes = self._generate_notes(param_schema, constraints, location)
        
        return {
            "location": location,
            "name": param.get('name', 'unknown'),
            "type": self._get_type(param_schema),
            "required": param.get('required', False),
            "constraints": constraints,
            "iterationCount": iteration_count,
            "notes": notes
        }
    
    def _analyze_request_body(
        self,
        request_body: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze request body and extract all parameters."""
        parameters = []
        
        # OpenAPI 3.x uses 'content'
        if 'content' in request_body:
            content = request_body.get('content', {})
            for content_type, content_schema in content.items():
                body_schema = content_schema.get('schema', {})
                if '$ref' in body_schema:
                    body_schema = self._resolve_ref(body_schema['$ref']) or body_schema
                
                # Extract all properties from body schema
                body_params = self._extract_schema_properties(
                    body_schema, 'body', schema, prefix=''
                )
                parameters.extend(body_params)
        
        # Swagger 2.0 uses 'schema' directly in body parameter
        elif 'schema' in request_body:
            body_schema = request_body.get('schema', {})
            if '$ref' in body_schema:
                body_schema = self._resolve_ref(body_schema['$ref']) or body_schema
            
            body_params = self._extract_schema_properties(
                body_schema, 'body', schema, prefix=''
            )
            parameters.extend(body_params)
        
        return parameters
    
    def _analyze_responses(
        self,
        responses: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze response schemas (2xx only)."""
        parameters = []
        
        for status_code, response_def in responses.items():
            if not status_code.startswith('2'):
                continue
            
            # Resolve $ref if present
            if '$ref' in response_def:
                response_def = self._resolve_ref(response_def['$ref']) or response_def
            
            content = response_def.get('content', {})
            for content_type, content_schema in content.items():
                response_schema = content_schema.get('schema', {})
                if '$ref' in response_schema:
                    response_schema = self._resolve_ref(response_schema['$ref']) or response_schema
                
                # Extract all properties from response schema
                response_params = self._extract_schema_properties(
                    response_schema, 'response', schema, prefix=f'response_{status_code}_'
                )
                parameters.extend(response_params)
        
        return parameters
    
    def _extract_schema_properties(
        self,
        schema: Dict[str, Any],
        location: str,
        root_schema: Dict[str, Any],
        prefix: str = '',
        depth: int = 0
    ) -> List[Dict[str, Any]]:
        """Recursively extract all properties from a schema object."""
        parameters = []
        
        if depth > 10:  # Prevent infinite recursion
            return parameters
        
        # Resolve $ref
        if '$ref' in schema:
            schema = self._resolve_ref(schema['$ref']) or schema
        
        # Handle object type
        if schema.get('type') == 'object' or 'properties' in schema:
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                full_name = f"{prefix}{prop_name}" if prefix else prop_name
                
                # Resolve $ref in property schema
                if isinstance(prop_schema, dict) and '$ref' in prop_schema:
                    prop_schema = self._resolve_ref(prop_schema['$ref']) or prop_schema
                
                constraints = self._extract_constraints(prop_schema)
                iteration_count = self._compute_iteration_count(prop_schema, constraints)
                notes = self._generate_notes(prop_schema, constraints, location)
                
                parameters.append({
                    "location": location,
                    "name": full_name,
                    "type": self._get_type(prop_schema),
                    "required": prop_name in required_fields,
                    "constraints": constraints,
                    "iterationCount": iteration_count,
                    "notes": notes
                })
                
                # Recurse into nested objects
                if prop_schema.get('type') == 'object' or 'properties' in prop_schema:
                    nested = self._extract_schema_properties(
                        prop_schema, location, root_schema, f"{full_name}.", depth + 1
                    )
                    parameters.extend(nested)
        
        # Handle array type
        elif schema.get('type') == 'array':
            items_schema = schema.get('items', {})
            if '$ref' in items_schema:
                items_schema = self._resolve_ref(items_schema['$ref']) or items_schema
            
            constraints = self._extract_constraints(schema)
            iteration_count = self._compute_iteration_count(schema, constraints)
            notes = self._generate_notes(schema, constraints, location)
            
            parameters.append({
                "location": location,
                "name": prefix.rstrip('.') if prefix else "array_item",
                "type": "array",
                "required": True,  # Arrays are typically required if present
                "constraints": constraints,
                "iterationCount": iteration_count,
                "notes": notes
            })
            
            # Recurse into array items if they're objects
            if items_schema.get('type') == 'object' or 'properties' in items_schema:
                nested = self._extract_schema_properties(
                    items_schema, location, root_schema, f"{prefix}[]", depth + 1
                )
                parameters.extend(nested)
        
        return parameters
    
    def _extract_constraints(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all constraints from a schema."""
        constraints = {}
        
        if not isinstance(schema, dict):
            return constraints
        
        # Enum
        if 'enum' in schema:
            constraints['enum'] = schema['enum']
        
        # Pattern
        if 'pattern' in schema:
            constraints['pattern'] = schema['pattern']
        
        # String constraints
        if 'minLength' in schema:
            constraints['minLength'] = schema['minLength']
        if 'maxLength' in schema:
            constraints['maxLength'] = schema['maxLength']
        
        # Number constraints
        if 'minimum' in schema:
            constraints['min'] = schema['minimum']
        if 'maximum' in schema:
            constraints['max'] = schema['maximum']
        if 'exclusiveMinimum' in schema:
            constraints['exclusiveMin'] = schema['exclusiveMinimum']
        if 'exclusiveMaximum' in schema:
            constraints['exclusiveMax'] = schema['exclusiveMaximum']
        
        # Array constraints
        if 'minItems' in schema:
            constraints['minItems'] = schema['minItems']
        if 'maxItems' in schema:
            constraints['maxItems'] = schema['maxItems']
        
        # Format
        if 'format' in schema:
            constraints['format'] = schema['format']
        
        return constraints
    
    def _get_type(self, schema: Dict[str, Any]) -> str:
        """Get the data type from schema."""
        if not isinstance(schema, dict):
            return "unknown"
        
        schema_type = schema.get('type', 'string')
        
        # Handle array
        if schema_type == 'array':
            return 'array'
        
        # Handle object
        if schema_type == 'object' or 'properties' in schema:
            return 'object'
        
        return schema_type
    
    def _compute_iteration_count(
        self,
        schema: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Any:
        """Compute the iteration domain count for a parameter."""
        # Enum: count enum values
        if 'enum' in constraints:
            return len(constraints['enum'])
        
        # Boolean: 2 values
        schema_type = schema.get('type', 'string')
        if schema_type == 'boolean':
            return 2
        
        # Number with min/max
        if schema_type in ['integer', 'number']:
            if 'min' in constraints and 'max' in constraints:
                min_val = constraints['min']
                max_val = constraints['max']
                # Handle exclusive bounds
                if constraints.get('exclusiveMin'):
                    min_val += 1
                if constraints.get('exclusiveMax'):
                    max_val -= 1
                return max_val - min_val + 1
            elif 'min' in constraints or 'max' in constraints:
                return "bounded"
        
        # Pattern/regex: classify input space
        if 'pattern' in constraints:
            pattern = constraints['pattern']
            # Simple classification
            if pattern == '^[a-zA-Z0-9]+$':
                return "alphanumeric"
            elif '^' in pattern and '$' in pattern:
                return "strict"
            else:
                return "partial"
        
        # Array with minItems/maxItems
        if schema_type == 'array':
            if 'minItems' in constraints and 'maxItems' in constraints:
                return constraints['maxItems'] - constraints['minItems'] + 1
            elif 'minItems' in constraints or 'maxItems' in constraints:
                return "bounded"
        
        # Object: recurse (simplified - return unbounded for now)
        if schema_type == 'object' or 'properties' in schema:
            return "unbounded"
        
        # Free text or unknown
        if schema_type == 'string':
            if 'minLength' in constraints or 'maxLength' in constraints:
                return "bounded"
            return "unbounded"
        
        return "unknown"
    
    def _generate_notes(
        self,
        schema: Dict[str, Any],
        constraints: Dict[str, Any],
        location: str
    ) -> str:
        """Generate notes for test design."""
        notes = []
        
        # Required field notes
        if location == 'path':
            notes.append("Path parameter - always required")
        
        # Constraint notes
        if 'enum' in constraints:
            notes.append(f"Enum with {len(constraints['enum'])} values")
        
        if 'pattern' in constraints:
            notes.append(f"Pattern constraint: {constraints['pattern']}")
        
        if 'minLength' in constraints or 'maxLength' in constraints:
            min_len = constraints.get('minLength', 0)
            max_len = constraints.get('maxLength', 'unlimited')
            notes.append(f"Length: {min_len}-{max_len}")
        
        if 'min' in constraints or 'max' in constraints:
            min_val = constraints.get('min', 'unbounded')
            max_val = constraints.get('max', 'unbounded')
            notes.append(f"Range: {min_val}-{max_val}")
        
        # Format notes
        if 'format' in constraints:
            notes.append(f"Format: {constraints['format']}")
        
        # Edge cases
        if not constraints:
            notes.append("No constraints - consider boundary and negative testing")
        
        return "; ".join(notes) if notes else "Standard parameter"

