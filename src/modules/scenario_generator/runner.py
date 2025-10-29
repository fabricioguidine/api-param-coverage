"""runner.py
Scenario pipeline runner.

Flow:
1. Load spec JSON with apis -> endpoints -> param_space.
2. For each endpoint:
   - Build representative param combinations w/ greedy_min_cover.
   - Call generate_bdd_for_endpoint(...) to create scenario dicts.
3. Write bdd_scenarios.csv with:
   apiName,endpointName,method,path,scenario_id,gherkin_and_curl

Public API:
  OUT_DIR
  OUT_CSV
  generate_bdd(spec_path, output_dir=None) -> path_to_csv
"""

import os
import json
import csv

from . import utils
from .coverage_logic import greedy_min_cover
from .bdd_scenario_generator import generate_bdd_for_endpoint

OUT_DIR = os.path.join(os.getcwd(), "outbound")
OUT_CSV = os.path.join(OUT_DIR, "bdd_scenarios.csv")

def _build_variations(param_space: dict):
    """
    Flatten param_space (headers/query/body) into {param: [values]},
    then pick representative combos using greedy_min_cover.
    """
    flattened = {}
    for section in ("headers", "query", "body"):
        sec_vals = param_space.get(section, {}) or {}
        for field, values in sec_vals.items():
            flattened[f"{section}.{field}"] = values
    return greedy_min_cover(flattened)

def _collect_rows(data: dict) -> list[tuple]:
    """
    Build rows for CSV.

    Each scenario dict from generate_bdd_for_endpoint has:
      scenario_id
      gherkin_and_curl

    We map each scenario dict into:
    (apiName, endpointName, method, path, scenario_id, gherkin_and_curl)
    """
    rows = []
    for api in data.get("apis", []):
        api_name = api.get("apiName")
        for ep in api.get("endpoints", []):
            endpoint_name = ep.get("name") or ep.get("endpointName")
            method = ep.get("method")
            path = ep.get("path")

            variations = _build_variations(ep.get("param_space", {}))
            scenario_dicts = generate_bdd_for_endpoint(
                {
                    "apiName": api_name,
                    "endpointName": endpoint_name,
                    "method": method,
                    "path": path
                },
                variations=variations,
                api_key=None
            )

            for scenario in scenario_dicts:
                rows.append((
                    api_name,
                    endpoint_name,
                    method,
                    path,
                    scenario["scenario_id"],
                    scenario["gherkin_and_curl"],
                ))
    return rows

def _write_csv_rows(rows: list[tuple], csv_path: str) -> str:
    utils.ensure_dir(os.path.dirname(csv_path))
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "apiName",
            "endpointName",
            "method",
            "path",
            "scenario_id",
            "gherkin_and_curl"
        ])
        for r in rows:
            w.writerow(r)
    return csv_path

def generate_bdd(spec_path: str, output_dir: str | None = None) -> str:
    """
    spec_path: path to spec JSON
    output_dir: optional override directory for CSV output

    Returns path to bdd_scenarios.csv.
    """
    with open(spec_path, encoding="utf-8") as f:
        data = json.load(f)

    if output_dir is None:
        csv_out = OUT_CSV
    else:
        utils.ensure_dir(output_dir)
        csv_out = os.path.join(output_dir, "bdd_scenarios.csv")

    rows = _collect_rows(data)
    return _write_csv_rows(rows, csv_out)
