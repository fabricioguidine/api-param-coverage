"""
BRD (Business Requirement Document) Module

Handles Business Requirement Document schemas and cross-referencing with Swagger schemas.
"""

from .brd_generator import BRDGenerator
from .brd_loader import BRDLoader
from .brd_parser import BRDParser
from .brd_schema import BRDRequirement, BRDSchema, BRDTestScenario
from .brd_transformer import BRDTransformer
from .brd_validator import BRDValidator
from .schema_cross_reference import SchemaCrossReference

__all__ = [
    "BRDGenerator",
    "BRDLoader",
    "BRDParser",
    "BRDRequirement",
    "BRDSchema",
    "BRDTestScenario",
    "BRDTransformer",
    "BRDValidator",
    "SchemaCrossReference",
]
