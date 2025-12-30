"""
Pytest configuration and fixtures for tests/config directory.

This file imports fixtures from the main tests/conftest.py
to ensure they're available when running tests with -c tests/config/pytest.ini
"""

import sys
from pathlib import Path

# Add parent directory to path to import from tests/conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all fixtures from main conftest
from conftest import *  # noqa: F401, F403


