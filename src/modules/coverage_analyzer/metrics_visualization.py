"""metrics_visualization.py
Produce a human-readable coverage summary.

generate_report(csv_path, out_dir) -> path to coverage_summary.txt
"""

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
        w.write(f"Total Scenarios: {total_rows}\n")
        w.write(f"Unique Endpoints: {len(unique_pairs)}\n")

    return out_path
