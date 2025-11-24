"""
JSON Utilities

Provides common JSON parsing and extraction functions.
"""

import re
from typing import Optional


def extract_json_from_response(response: str) -> Optional[str]:
    """
    Extract JSON from LLM response (may be wrapped in markdown code blocks).
    
    Args:
        response: The LLM response string that may contain JSON
        
    Returns:
        Extracted JSON string, or the original response if no JSON found
    """
    if not response:
        return None
    
    # Try to find JSON in code blocks (```json ... ``` or ``` ... ```)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON object directly (starts with { and ends with })
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # Return as-is, let parser handle it
    return response


