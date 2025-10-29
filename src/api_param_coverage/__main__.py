"""__main__.py
CLI for api-param-coverage.

Commands:
  scenarios -> generate BDD CSV from API spec
  postman   -> generate Postman-style JSON from CSV
  coverage  -> generate basic coverage summary
"""

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
