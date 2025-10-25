import os
import csv
import argparse

from . import utils
from . import coverage_calculator
from . import llm_bdd_generator

OUT_DIR = "src/coverage_engine/outbound"
OUT_CSV = os.path.join(OUT_DIR, "bdd_scenarios.csv")

DEFAULT_COLLECTION = "src/coverage_engine/outbound/sample.json"

def generate_bdd(collection_path: str):
    """
    1. Load endpoints from a collection JSON
    2. Build minimal coverage scenarios
    3. Ask the (stub) BDD generator to produce Gherkin text
    4. Save to CSV so other steps can consume
    """

    os.makedirs(OUT_DIR, exist_ok=True)

    endpoints = utils.load_collection(collection_path)
    rows = []

    for ep in endpoints:
        flat_space = utils.flatten_param_space(ep)
        scenarios = coverage_calculator.greedy_min_cover(flat_space)

        endpoint_meta = {
            "apiName": ep.apiName,
            "endpointName": ep.endpointName,
            "method": ep.method,
            "path": ep.path,
        }

        bdd_list = llm_bdd_generator.generate_bdd_for_endpoint(
            endpoint_meta,
            scenarios,
            api_key=None,  # stub right now
        )

        for item in bdd_list:
            rows.append(
                {
                    "apiName": ep.apiName,
                    "endpointName": ep.endpointName,
                    "method": ep.method,
                    "path": ep.path,
                    "scenario_id": item["scenario_id"],
                    "gherkin_and_curl": item["gherkin_and_curl"].replace("\n", "\\n"),
                }
            )

    if not rows:
        # still create the file with headers so downstream code doesn't explode
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "apiName",
                    "endpointName",
                    "method",
                    "path",
                    "scenario_id",
                    "gherkin_and_curl",
                ]
            )
        print("[WARN] No scenarios generated, wrote empty-ish CSV")
        return OUT_CSV

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "apiName",
                "endpointName",
                "method",
                "path",
                "scenario_id",
                "gherkin_and_curl",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("[OK] wrote", OUT_CSV)
    return OUT_CSV


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="Path to the input collection JSON",
    )
    args = parser.parse_args()

    generate_bdd(args.collection)


if __name__ == "__main__":
    main()
