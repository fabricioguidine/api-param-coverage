"""llm_bdd_generator.py
Compatibility shim for tests.

tests expect:
    from modules.scenario_generator.llm_bdd_generator import generate_bdd_for_endpoint
We'll forward to bdd_scenario_generator.generate_bdd_for_endpoint.
"""

from .bdd_scenario_generator import generate_bdd_for_endpoint  # type: ignore
