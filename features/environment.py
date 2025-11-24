"""
Behave environment configuration.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def before_all(context):
    """Set up before all scenarios."""
    # Ensure test directories exist
    os.makedirs("data/schemas", exist_ok=True)
    os.makedirs("output", exist_ok=True)


def after_all(context):
    """Clean up after all scenarios."""
    pass


def before_scenario(context, scenario):
    """Set up before each scenario."""
    context.scenario_name = scenario.name


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up any temporary files created during scenario
    pass

