import csv
import json
import os
from datetime import datetime

CSV_IN = "src/coverage_engine/outbound/bdd_scenarios.csv"
OUT_DIR = "src/postman_export/outbound"

def to_js_test_block(gherkin_text: str, scenario_id: str):
    """
    We take the generated BDD text and embed it into the Postman
    Tests script as commented lines, then add a status 200 assertion.
    """
    lines = []

    lines.append(f"// Scenario {scenario_id}")
    lines.append("// BDD:")
    for raw_line in gherkin_text.split("\\n"):  # gherkin_and_curl is \n-escaped
        lines.append(f"// {raw_line}")
    lines.append("pm.test('should return 200', function () {")
    lines.append("    pm.response.to.have.status(200);")
    lines.append("});")

    return lines


def build_collection(csv_path: str):
    """
    Build a Postman collection object from bdd_scenarios.csv
    """
    if not os.path.exists(csv_path):
        print("[WARN] CSV not found:", csv_path)
        return {"info": {"name": "Empty"}, "item": []}

    # group rows per (apiName, endpointName, method, path)
    grouped = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = (
                row["apiName"],
                row["endpointName"],
                row["method"],
                row["path"],
            )
            grouped.setdefault(key, []).append(row)

    items = []

    for (api_name, ep_name, http_method, path), scenario_rows in grouped.items():
        # build combined test script for all scenarios of this request
        exec_lines = []
        for s in scenario_rows:
            exec_lines.extend(
                to_js_test_block(
                    s["gherkin_and_curl"],
                    s["scenario_id"],
                )
            )
            exec_lines.append("")  # spacer

        # build the Postman item
        item = {
            "name": f"{api_name} - {ep_name}",
            "request": {
                "method": http_method,
                "header": [],  # headers can be injected here if needed
                "url": {
                    "raw": f"http://localhost:8080{path}",
                    "host": ["http://localhost:8080"],
                    "path": [seg for seg in path.strip("/").split("/") if seg],
                },
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": exec_lines,
                    },
                }
            ],
        }

        items.append(item)

    collection = {
        "info": {
            "name": f"Coverage Collection {datetime.now().isoformat()}",
            "description": "Generated from bdd_scenarios.csv. BDD steps embedded in Tests tab.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
    }

    return collection


def save_collection(coll):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(
        OUT_DIR,
        f"postman_{int(datetime.now().timestamp())}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(coll, f, indent=2)
    print("[OK] wrote", out_path)
    return out_path


def main():
    coll = build_collection(CSV_IN)
    save_collection(coll)


if __name__ == "__main__":
    main()
