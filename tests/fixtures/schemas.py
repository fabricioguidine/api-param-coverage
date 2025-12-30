"""
Schema Test Fixtures

Sample Swagger/OpenAPI schemas for testing.
"""

# Minimal Swagger 2.0 schema
MINIMAL_SWAGGER_2 = {
    "swagger": "2.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/test": {
            "get": {
                "summary": "Test endpoint",
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                }
            }
        }
    }
}

# Small Swagger 2.0 schema (5-10 endpoints)
SMALL_SWAGGER_2 = {
    "swagger": "2.0",
    "info": {
        "title": "Small Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/users": {
            "get": {
                "summary": "Get users",
                "responses": {"200": {"description": "Success"}}
            },
            "post": {
                "summary": "Create user",
                "responses": {"201": {"description": "Created"}}
            }
        },
        "/users/{id}": {
            "get": {
                "summary": "Get user",
                "parameters": [{"name": "id", "in": "path", "type": "string"}],
                "responses": {"200": {"description": "Success"}}
            },
            "put": {
                "summary": "Update user",
                "parameters": [{"name": "id", "in": "path", "type": "string"}],
                "responses": {"200": {"description": "Success"}}
            },
            "delete": {
                "summary": "Delete user",
                "parameters": [{"name": "id", "in": "path", "type": "string"}],
                "responses": {"204": {"description": "Deleted"}}
            }
        }
    }
}

# OpenAPI 3.0 schema
OPENAPI_3_0 = {
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/test": {
            "get": {
                "summary": "Test endpoint",
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                }
            }
        }
    }
}

# Complex schema with nested structures
COMPLEX_SCHEMA = {
    "swagger": "2.0",
    "info": {
        "title": "Complex API",
        "version": "1.0.0"
    },
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["id", "name"]
        }
    },
    "paths": {
        "/users": {
            "get": {
                "summary": "Get users",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/User"}
                        }
                    }
                }
            }
        }
    }
}

