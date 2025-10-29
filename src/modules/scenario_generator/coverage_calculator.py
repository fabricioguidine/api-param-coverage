"""coverage_calculator.py
Compatibility shim for tests.

tests expect:
    from modules.scenario_generator.coverage_calculator import greedy_min_cover
We'll re-export greedy_min_cover from coverage_logic.
"""

from .coverage_logic import greedy_min_cover  # type: ignore
