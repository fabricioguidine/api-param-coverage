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
        Extracted JSON string, or None if no valid JSON found
    """
    if not response:
        return None
    
    # Remove leading/trailing whitespace
    response = response.strip()
    
    # If response already looks like JSON (starts with {), try to find the complete JSON object
    if response.startswith('{'):
        # Find the matching closing brace
        brace_count = 0
        for i, char in enumerate(response):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return response[:i+1]
    
    # Try to find JSON in code blocks (```json ... ``` or ``` ... ```)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON object directly (starts with { and ends with })
    # Use a more precise pattern that finds balanced braces
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # Return None if no JSON found (don't return invalid text)
    return None


