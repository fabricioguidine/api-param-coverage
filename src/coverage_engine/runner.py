"""coverage_engine.runner
Legacy shim so tests can monkeypatch OUT_DIR / OUT_CSV
and call generate_bdd(spec_path) with only one arg.
"""

import os
import json
from modules.scenario_generator import runner as _runner
from modules.scenario_generator import utils as _utils

OUT_DIR = os.path.join(os.getcwd(), "outbound")
OUT_CSV = os.path.join(OUT_DIR, "bdd_scenarios.csv")

def generate_bdd(spec_path: str) -> str:
    """
    One-arg interface expected by tests.

    Steps:
      - read spec json
      - _runner._collect_rows(...)
      - write via _runner._write_csv_rows(...) to OUT_CSV
      - return OUT_CSV
    """
    with open(spec_path, encoding="utf-8") as f:
        data = json.load(f)

    _utils.ensure_dir(os.path.dirname(OUT_CSV))
    rows = _runner._collect_rows(data)
    return _runner._write_csv_rows(rows, OUT_CSV)
