"""
Shared Utilities Module

Provides common utility functions used across multiple modules.
"""

from .json_utils import extract_json_from_response
from .constants import (
    DEFAULT_COVERAGE_PERCENTAGE,
    MAX_COVERAGE_PERCENTAGE,
    MIN_COVERAGE_PERCENTAGE,
    DEFAULT_LLM_MODEL,
    SUPPORTED_BRD_FORMATS,
    SUPPORTED_SCHEMA_FORMATS
)

from .llm_provider import detect_provider_from_key, get_api_key_and_provider, setup_api_key, get_provider_info

__all__ = [
    'extract_json_from_response',
    'DEFAULT_COVERAGE_PERCENTAGE',
    'MAX_COVERAGE_PERCENTAGE',
    'MIN_COVERAGE_PERCENTAGE',
    'DEFAULT_LLM_MODEL',
    'SUPPORTED_BRD_FORMATS',
    'SUPPORTED_SCHEMA_FORMATS',
    'detect_provider_from_key',
    'get_api_key_and_provider',
    'setup_api_key',
    'get_provider_info'
]


