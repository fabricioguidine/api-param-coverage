"""
Constants

Shared constants used across the application.
"""

# Coverage percentage constants
DEFAULT_COVERAGE_PERCENTAGE = 100.0
MAX_COVERAGE_PERCENTAGE = 100.0
MIN_COVERAGE_PERCENTAGE = 1.0

# LLM constants
DEFAULT_LLM_MODEL = "gpt-4"
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 3000

# Path constants
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_BRD_INPUT_SCHEMA_DIR = "src/modules/brd/input_schema"
DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR = "src/modules/brd/input_transformator"

# File format constants
SUPPORTED_BRD_FORMATS = {
    '.txt': 'text',
    '.csv': 'csv',
    '.pdf': 'pdf',
    '.doc': 'word',
    '.docx': 'word',
    '.md': 'markdown',
    '.json': 'json'
}

SUPPORTED_SCHEMA_FORMATS = ['json', 'yaml', 'yml']

# HTTP method priority scores
HTTP_METHOD_PRIORITY = {
    'POST': 100.0,
    'PUT': 100.0,
    'DELETE': 100.0,
    'GET': 50.0,
    'PATCH': 30.0,
    'HEAD': 20.0,
    'OPTIONS': 10.0
}

# Parameter scoring constants
PARAM_COMPLEXITY_MULTIPLIER = 5.0
PARAM_COMPLEXITY_MAX = 50.0
REQUIRED_PARAM_MULTIPLIER = 3.0

# Token estimation
CHARS_PER_TOKEN = 4  # Approximate characters per token for English text
MAX_TOKENS_FOR_RESPONSE = 3000
GPT4_TOKEN_LIMIT = 8192


