import argparse
import os
import importlib
from glob import glob
from datetime import datetime
from . import utils
from . import coverage_calculator
from . import llm_bdd_generator


def _newest_sample_path():
    """Find latest sample_*.json in src/coverage_engine/outbound/"""
    pattern = os.path.join("src", "coverage_engine", "outbound", "sample_*.json")
    files = sorted(glob(pattern))
    if not files:
        raise FileNotFoundError(
            "No sample_*.json found in src/coverage_engine/outbound/. "
            "Run `python -m src.coverage_engine.runner --generate-sample` first."
        )
    return files[-1]


def run_full_pipeline(collection_path: str):
    """Run coverage → BDD generation → CSV export."""
    print(f"[INFO] Using collection: {collection_path}")
    endpoints = utils.load_collection(collection_path)

    rows = utils.build_coverage_rows(
        endpoints=endpoints,
        coverage_calculator_mod=coverage_calculator,
        llm_bdd_generator_mod=llm_bdd_generator,
    )

    csv_path = utils.write_rows_to_csv(rows)
    print(f"[OK] BDD CSV generated at: {csv_path}")
    return csv_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", type=str, help="Path to existing sample JSON")
    parser.add_argument("--generate-sample", action="store_true", help="Generate a new random sample collection")
    args = parser.parse_args()

    # Handle --generate-sample
    if args.generate_sample:
        try:
            dummy_gen = importlib.import_module("test.coverage_engine.dummy_data_generator")
        except ImportError as e:
            raise RuntimeError(f"Could not import dummy_data_generator: {e}")

        path = dummy_gen.create_sample_collection()
        print(f"[OK] New dummy collection generated: {path}")
        collection_path = path
    else:
        # Automatically get latest if none provided
        if args.collection:
            collection_path = args.collection
        else:
            collection_path = _newest_sample_path()
            print(f"[INFO] Auto-detected latest collection: {collection_path}")

    # Process the collection into coverage + BDD
    run_full_pipeline(collection_path)


if __name__ == "__main__":
    main()
