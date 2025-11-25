"""
BRD (Business Requirement Document) Module

Handles Business Requirement Document schemas and cross-referencing with Swagger schemas.
"""

from .brd_schema import BRDSchema, BRDRequirement, BRDTestScenario
from .brd_loader import BRDLoader
from .brd_parser import BRDParser
from .schema_cross_reference import SchemaCrossReference
from .brd_generator import BRDGenerator
from .brd_transformer import BRDTransformer
from .brd_validator import BRDValidator

__all__ = ['BRDSchema', 'BRDRequirement', 'BRDTestScenario', 'BRDLoader', 'BRDParser', 'SchemaCrossReference', 'BRDGenerator', 'BRDTransformer', 'BRDValidator']

