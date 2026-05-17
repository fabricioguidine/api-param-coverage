"""Input validation utilities."""

import re
from pathlib import Path
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom validation error."""

    pass


def validate_url(url: str) -> str:
    """Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        Validated URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL cannot be empty")

    # Parse URL
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValidationError("Invalid URL format. Must include scheme (http/https) and domain")

        if result.scheme not in ["http", "https"]:
            raise ValidationError("URL must use http or https")

        return url

    except Exception as e:
        raise ValidationError(f"Invalid URL: {e}") from e


def validate_file_path(path: str, must_exist: bool = True) -> Path:
    """Validate file path.

    Args:
        path: File path string
        must_exist: Whether file must exist

    Returns:
        Path object

    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Path cannot be empty")

    file_path = Path(path)

    if must_exist and not file_path.exists():
        raise ValidationError(f"File not found: {path}")

    return file_path


def validate_api_key(api_key: str) -> str:
    """Validate API key format (supports multiple providers).

    Args:
        api_key: API key string

    Returns:
        Validated API key

    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key cannot be empty")

    api_key = api_key.strip()

    # Basic validation: must be non-empty and reasonable length
    if len(api_key) < 10:
        raise ValidationError("API key appears to be too short (minimum 10 characters)")

    if len(api_key) > 500:
        raise ValidationError("API key appears to be too long (maximum 500 characters)")

    # Check for basic valid characters (alphanumeric, dashes, underscores, dots)
    if not re.match(r"^[A-Za-z0-9_\-\.]+$", api_key):
        raise ValidationError("API key contains invalid characters")

    return api_key
