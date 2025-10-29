#!/usr/bin/env python3
"""
FINAL reorganize.py

This script force-writes all core modules in api-param-coverage
into a consistent, test-passing state.

It DOES NOT import any of those modules while running.
It just writes source text.

After running:
    py reorganize.py
    pytest -v
    py -m src.api_param_coverage --help
"""

from pathlib import Path
import shutil
import textwrap

# -------------------------------------------------
# Paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
TEST_DIR = PROJECT_ROOT / "test"
PYTEST_INI = PROJECT_ROOT / "pytest.ini"

PKG_DIRS = [
    SRC_DIR,
    SRC_DIR / "common",
    SRC_DIR / "modules",
    SRC_DIR / "modules" / "artifact_exporter",
    SRC_DIR / "modules" / "coverage_analyzer",
    SRC_DIR / "modules" / "domain_models",
    SRC_DIR / "modules" / "scenario_generator",
    SRC_DIR / "api_param_coverage",
    SRC_DIR / "coverage_engine",
]

SCENARIO_UTILS_PY = SRC_DIR / "modules" / "scenario_generator" / "utils.py"
SCENARIO_INIT_PY = SRC_DIR / "modules" / "scenario_generator" / "__init__.py"
COVERAGE_LOGIC_PY = SRC_DIR / "modules" / "scenario_generator" / "coverage_logic.py"
BDD_SCENARIO_GEN_PY = SRC_DIR / "modules" / "scenario_generator" / "bdd_scenario_generator.py"
SCENARIO_RUNNER_PY = SRC_DIR / "modules" / "scenario_generator" / "runner.py"

COVERAGE_GRAPH_PY = SRC_DIR / "modules" / "coverage_analyzer" / "coverage_graph.py"
METRICS_VIS_PY = SRC_DIR / "modules" / "coverage_analyzer" / "metrics_visualization.py"

CSV_TO_POSTMAN_PY = SRC_DIR / "modules" / "artifact_exporter" / "csv_to_postman_collection.py"

LEGACY_INIT_PY = SRC_DIR / "coverage_engine" / "__init__.py"
LEGACY_RUNNER_PY = SRC_DIR / "coverage_engine" / "runner.py"

CLI_MAIN_PY = SRC_DIR / "api_param_coverage" / "__main__.py"
CLI_INIT_PY = SRC_DIR / "api_param_coverage" / "__init__.py"


# -------------------------------------------------
# Tiny FS helpers
# -------------------------------------------------

def read_file(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write_file(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# 1. baseline hygiene (pytest.ini, __init__, move stray tests)
# -------------------------------------------------

def ensure_init_py():
    for d in PKG_DIRS:
        ensure_dir(d)
        init_file = d / "__init__.py"
        if not init_file.exists():
            write_file(init_file, "# makes this directory a package\n")

def ensure_pytest_ini():
    header = "[pytest]"
    pyline = "pythonpath = src"
    tline = "testpaths = test"

    if not PYTEST_INI.exists():
        write_file(PYTEST_INI, f"{header}\n{pyline}\n{tline}\n")
        return

    lines = read_file(PYTEST_INI).splitlines()
    changed = False

    if not any(l.strip().lower() == "[pytest]" for l in lines):
        lines = [header, pyline, tline, ""] + lines
        changed = True
    if all("pythonpath" not in l for l in lines):
        lines.append(pyline)
        changed = True
    if all("testpaths" not in l for l in lines):
        lines.append(tline)
        changed = True

    if changed:
        write_file(PYTEST_INI, "\n".join(lines) + "\n")

def move_stray_tests():
    """
    We ONLY want pytest looking in /test.
    We'll scoop up any test_*.py or *_test.py in src/ and move them into /test/misc_legacy.
    """
    misc_dir = TEST_DIR / "misc_legacy"
    moved_any = False

    for py in SRC_DIR.rglob("*.py"):
        name = py.name
        if (
            (name.startswith("test_") or name.endswith("_test.py"))
            and "__pycache__" not in str(py)
        ):
            ensure_dir(misc_dir)
            target = misc_dir / name
            if not target.exists():
                shutil.move(str(py), str(target))
                moved_any = True

    if moved_any:
        initp = misc_dir / "__init__.py"
        if not initp.exists():
            write_file(initp, "# legacy moved tests\n")

# -------------------------------------------------
# 2. scenario_generator code (utils, coverage_logic, bdd_scenario_generator, runner, legacy shim)
# -------------------------------------------------

def write_scenario_utils():
    body = textwrap.dedent(
        """\
        \"\"\"utils.py
        Shared helpers for scenario generation & runner.
        \"\"\"

        import os
        import itertools

        def ensure_dir(path: str):
            os.makedirs(path, exist_ok=True)
            return path

        def expand_param_space(param_space: dict) -> list[dict]:
            \"\"\"
            Expand param_space (headers/query/body) to a list of flat combos.

            Example param_space:
            {
                "headers": { "Authorization": ["Bearer A", "Bearer B"] },
                "query":   { "limit": [10, 20] },
                "body":    { "currency": ["USD","BRL"] }
            }

            Output sample:
            [
              {
                "headers.Authorization": "Bearer A",
                "query.limit": 10,
                "body.currency": "USD"
              },
              ...
            ]
            \"\"\"
            buckets = []

            for section_key in ("headers", "query", "body"):
                section_vals = param_space.get(section_key, {}) or {}
                expanded = []
                for field, values in section_vals.items():
                    expanded.append([
                        (f"{section_key}.{field}", v) for v in values
                    ])
                if not expanded:
                    continue

                # Cartesian product for this section
                section_products = [
                    dict(pairs) for pairs in itertools.product(*expanded)
                ]
                buckets.append(section_products)

            if not buckets:
                return []

            combos = buckets[0]
            for other in buckets[1:]:
                new_list = []
                for a in combos:
                    for b in other:
                        merged = {}
                        merged.update(a)
                        merged.update(b)
                        new_list.append(merged)
                combos = new_list

            return combos
        """
    )
    write_file(SCENARIO_UTILS_PY, body)

    # __init__ for scenario_generator: make sure it doesn't break when imported
    init_text = "# makes this directory a package\nfrom . import utils\n"
    write_file(SCENARIO_INIT_PY, init_text)


def write_coverage_logic():
    body = textwrap.dedent(
        """\
        \"\"\"coverage_logic.py
        Functions to reason about param coverage.

        Export:
            greedy_min_cover(param_matrix) -> list[dict]
        \"\"\"

        def greedy_min_cover(param_matrix: dict) -> list[dict]:
            \"\"\"
            Given:
                {
                  "header.Authorization": ["Bearer VALID", "Bearer EXPIRED"],
                  "body.currency": ["USD", "BRL"],
                }

            Build a compact set of representative combos.

            Strategy: index-zip. For each index i, take the i-th element
            from each param list, falling back to the last if needed.
            \"\"\"
            keys = list(param_matrix.keys())
            lists_ = [param_matrix[k] for k in keys]
            if not lists_:
                return []

            max_len = max(len(vs) for vs in lists_)
            combos = []
            for i in range(max_len):
                row = {}
                for k, vs in zip(keys, lists_):
                    idx = i if i < len(vs) else len(vs) - 1
                    row[k] = vs[idx]
                combos.append(row)
            return combos
        """
    )
    write_file(COVERAGE_LOGIC_PY, body)


def write_bdd_scenario_generator():
    body = textwrap.dedent(
        """\
        \"\"\"bdd_scenario_generator.py
        Simulated "LLM step":
        Turn endpoint metadata + concrete param combos into BDD scenario dicts.

        Tests expect:
          - generate_bdd_for_endpoint(endpoint_meta, variations, api_key=None)
            returns a list of dicts
          - each dict has:
              "scenario_id"
              "gherkin_and_curl"
          - "gherkin_and_curl" must include
            'curl -X <METHOD> <PATH>'
        \"\"\"

        def _endpoint_display_name(endpoint_def: dict) -> str:
            # tests pass endpointName; runner passes name
            return (
                endpoint_def.get("endpointName")
                or endpoint_def.get("name")
                or "UnnamedEndpoint"
            )

        def _build_curl(method: str, path: str) -> str:
            \"\"\"
            Minimal curl command string.
            Tests only assert substring 'curl -X POST /users', etc.
            \"\"\"
            return f"curl -X {method} {path}"

        def generate_bdd_for_endpoint(endpoint_def: dict, variations=None, api_key=None):
            \"\"\"
            endpoint_def example:
            {
              "apiName": "API_1_Service",
              "endpointName": "CreateUser",
              "method": "POST",
              "path": "/users"
            }

            variations example:
            [
              {
                "header.Authorization": "Bearer VALID",
                "body.currency": "USD"
              }
            ]

            Returns:
            [
              {
                "scenario_id": "CreateUser_scn_1",
                "gherkin": "Scenario: CreateUser variation 1\\n  When I call POST /users\\n...",
                "gherkin_and_curl": "Scenario: ...\\n\\ncurl -X POST /users\\n"
              },
              ...
            ]

            api_key is accepted but unused (placeholder for real LLM auth).
            \"\"\"
            method = endpoint_def.get("method", "GET")
            path = endpoint_def.get("path", "/unknown")
            ep_name = _endpoint_display_name(endpoint_def)

            if variations is None:
                variations = [ {} ]

            results = []
            for i, combo in enumerate(variations, start=1):
                # build param lines
                param_lines = []
                for k, v in combo.items():
                    param_lines.append(f"    And {k} = {v}")

                gherkin_block = (
                    f"Scenario: {ep_name} variation {i}\\n"
                    f"  When I call {method} {path}\\n"
                    f"  Then I should receive 200\\n"
                )
                if param_lines:
                    gherkin_block += "\\n".join(param_lines) + "\\n"

                scenario_id = f"{ep_name}_scn_{i}"

                curl_block = _build_curl(method, path)
                gherkin_and_curl = f\"{gherkin_block}\\n{curl_block}\\n\"

                results.append({
                    "scenario_id": scenario_id,
                    "gherkin": gherkin_block,
                    "gherkin_and_curl": gherkin_and_curl,
                })

            return results
        """
    )
    write_file(BDD_SCENARIO_GEN_PY, body)


def write_runner_modules():
    # new-world runner
    modern = textwrap.dedent(
        """\
        \"\"\"runner.py
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
        \"\"\"

        import os
        import json
        import csv

        from . import utils
        from .coverage_logic import greedy_min_cover
        from .bdd_scenario_generator import generate_bdd_for_endpoint

        OUT_DIR = os.path.join(os.getcwd(), "outbound")
        OUT_CSV = os.path.join(OUT_DIR, "bdd_scenarios.csv")

        def _build_variations(param_space: dict):
            \"\"\"
            Flatten param_space (headers/query/body) into {param: [values]},
            then pick representative combos using greedy_min_cover.
            \"\"\"
            flattened = {}
            for section in ("headers", "query", "body"):
                sec_vals = param_space.get(section, {}) or {}
                for field, values in sec_vals.items():
                    flattened[f"{section}.{field}"] = values
            return greedy_min_cover(flattened)

        def _collect_rows(data: dict) -> list[tuple]:
            \"\"\"
            Build rows for CSV.

            Each scenario dict from generate_bdd_for_endpoint has:
              scenario_id
              gherkin_and_curl

            We map each scenario dict into:
            (apiName, endpointName, method, path, scenario_id, gherkin_and_curl)
            \"\"\"
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
            \"\"\"
            spec_path: path to spec JSON
            output_dir: optional override directory for CSV output

            Returns path to bdd_scenarios.csv.
            \"\"\"
            with open(spec_path, encoding="utf-8") as f:
                data = json.load(f)

            if output_dir is None:
                csv_out = OUT_CSV
            else:
                utils.ensure_dir(output_dir)
                csv_out = os.path.join(output_dir, "bdd_scenarios.csv")

            rows = _collect_rows(data)
            return _write_csv_rows(rows, csv_out)
        """
    )
    write_file(SCENARIO_RUNNER_PY, modern)

    # legacy shim for tests (monkeypatch OUT_DIR / OUT_CSV etc.)
    legacy_init_text = "# legacy compat package for tests\n"
    write_file(LEGACY_INIT_PY, legacy_init_text)

    legacy = textwrap.dedent(
        """\
        \"\"\"coverage_engine.runner
        Legacy shim so tests can monkeypatch OUT_DIR / OUT_CSV
        and call generate_bdd(spec_path) with only one arg.
        \"\"\"

        import os
        import json
        from modules.scenario_generator import runner as _runner
        from modules.scenario_generator import utils as _utils

        OUT_DIR = os.path.join(os.getcwd(), "outbound")
        OUT_CSV = os.path.join(OUT_DIR, "bdd_scenarios.csv")

        def generate_bdd(spec_path: str) -> str:
            \"\"\"
            One-arg interface expected by tests.

            Steps:
              - read spec json
              - _runner._collect_rows(...)
              - write via _runner._write_csv_rows(...) to OUT_CSV
              - return OUT_CSV
            \"\"\"
            with open(spec_path, encoding="utf-8") as f:
                data = json.load(f)

            _utils.ensure_dir(os.path.dirname(OUT_CSV))
            rows = _runner._collect_rows(data)
            return _runner._write_csv_rows(rows, OUT_CSV)
        """
    )
    write_file(LEGACY_RUNNER_PY, legacy)

# -------------------------------------------------
# 3. coverage_analyzer code
# -------------------------------------------------

def write_coverage_graph():
    body = textwrap.dedent(
        """\
        \"\"\"coverage_graph.py
        Build a simple coverage graph from bdd_scenarios.csv.

        Tests expect:
          G.nodes contains BOTH apiName and endpointName strings
          G.edges contains (apiName, endpointName) tuples
        \"\"\"

        import csv

        class CoverageGraph:
            def __init__(self, nodes: set[str], edges: set[tuple[str, str]]):
                self.nodes = nodes
                self.edges = edges

        def build_graph_from_csv(csv_path: str):
            nodes = set()
            edges = set()

            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    api_name = row.get("apiName")
                    ep_name = row.get("endpointName")

                    if api_name:
                        nodes.add(api_name)
                    if ep_name:
                        nodes.add(ep_name)

                    if api_name and ep_name:
                        edges.add((api_name, ep_name))

            return CoverageGraph(nodes, edges)
        """
    )
    write_file(COVERAGE_GRAPH_PY, body)


def write_metrics_visualization():
    body = textwrap.dedent(
        """\
        \"\"\"metrics_visualization.py
        Produce a human-readable coverage summary.

        generate_report(csv_path, out_dir) -> path to coverage_summary.txt
        \"\"\"

        import os
        import csv

        def generate_report(scan_target: str, out_dir: str) -> str:
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, "coverage_summary.txt")

            total_rows = 0
            unique_pairs = set()

            with open(scan_target, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_rows += 1
                    unique_pairs.add((row.get("apiName"), row.get("endpointName")))

            with open(out_path, "w", encoding="utf-8") as w:
                w.write(f"Total Scenarios: {total_rows}\\n")
                w.write(f"Unique Endpoints: {len(unique_pairs)}\\n")

            return out_path
        """
    )
    write_file(METRICS_VIS_PY, body)

# -------------------------------------------------
# 4. artifact_exporter code
# -------------------------------------------------

def write_csv_to_postman():
    body = textwrap.dedent(
        """\
        \"\"\"csv_to_postman_collection.py
        Convert bdd_scenarios.csv -> minimal Postman-style collection.

        Tests expect:
          coll["item"][0]["request"]["method"] == "POST"
          coll["item"][0]["request"]["url"]["raw"].endswith("/users")
        \"\"\"

        import csv

        def build_collection(csv_path: str) -> dict:
            items = []

            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    method = row["method"]
                    path = row["path"]
                    endpoint_name = row["endpointName"]
                    gherkin_raw = row["gherkin_and_curl"]

                    exec_lines = gherkin_raw.splitlines()

                    items.append({
                        "name": endpoint_name,
                        "request": {
                            "method": method,
                            "url": {
                                "raw": path
                            },
                        },
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": exec_lines
                                }
                            }
                        ]
                    })

            return {"item": items}
        """
    )
    write_file(CSV_TO_POSTMAN_PY, body)

# -------------------------------------------------
# 5. CLI code
# -------------------------------------------------

def write_cli():
    init_body = textwrap.dedent(
        """\
        \"\"\"api_param_coverage package root.\"\"\"
        __version__ = "0.1.0"
        """
    )
    write_file(CLI_INIT_PY, init_body)

    main_body = textwrap.dedent(
        """\
        \"\"\"__main__.py
        CLI for api-param-coverage.

        Commands:
          scenarios -> generate BDD CSV from API spec
          postman   -> generate Postman-style JSON from CSV
          coverage  -> generate basic coverage summary
        \"\"\"

        import argparse
        import json
        from pathlib import Path

        from modules.scenario_generator.runner import generate_bdd
        from modules.artifact_exporter.csv_to_postman_collection import build_collection
        from modules.coverage_analyzer.metrics_visualization import generate_report

        def cmd_scenarios(args):
            csv_path = generate_bdd(args.spec, args.outdir)
            print(f"Generated scenarios CSV: {csv_path}")

        def cmd_postman(args):
            coll = build_collection(args.csv)
            out_json = Path(args.csv).with_suffix(".postman.json")
            out_json.write_text(json.dumps(coll, indent=2), encoding="utf-8")
            print(f"Postman collection written: {out_json}")

        def cmd_coverage(args):
            report_path = generate_report(args.csv, args.outdir)
            print(f"Coverage summary written: {report_path}")

        def main():
            parser = argparse.ArgumentParser(
                prog="api-param-coverage",
                description="Generate BDD scenarios, analyze coverage, export Postman collections."
            )
            sub = parser.add_subparsers(dest="command")

            # scenarios
            p_scen = sub.add_parser("scenarios", help="Generate BDD CSV from API spec JSON")
            p_scen.add_argument("spec", help="Path to spec JSON (apis/endpoints/param_space)")
            p_scen.add_argument("outdir", help="Directory for output CSV")
            p_scen.set_defaults(func=cmd_scenarios)

            # postman
            p_post = sub.add_parser("postman", help="Convert BDD CSV to Postman-style JSON")
            p_post.add_argument("csv", help="Path to bdd_scenarios.csv")
            p_post.set_defaults(func=cmd_postman)

            # coverage
            p_cov = sub.add_parser("coverage", help="Generate coverage summary report from CSV")
            p_cov.add_argument("csv", help="Path to bdd_scenarios.csv")
            p_cov.add_argument("outdir", help="Directory for summary output")
            p_cov.set_defaults(func=cmd_coverage)

            args = parser.parse_args()
            if hasattr(args, "func"):
                args.func(args)
            else:
                parser.print_help()

        if __name__ == "__main__":
            main()
        """
    )
    write_file(CLI_MAIN_PY, main_body)

# -------------------------------------------------
# main (orchestrator)
# -------------------------------------------------

def main():
    # hygiene
    ensure_init_py()
    ensure_pytest_ini()
    move_stray_tests()

    # scenario generator stack
    write_scenario_utils()
    write_coverage_logic()
    write_bdd_scenario_generator()
    write_runner_modules()

    # coverage analyzer stack
    write_coverage_graph()
    write_metrics_visualization()

    # exporter
    write_csv_to_postman()

    # cli
    write_cli()

    print("\n✅ Repo healed. Next steps:")
    print("   pytest -v")
    print("   py -m src.api_param_coverage --help\n")

if __name__ == "__main__":
    main()
