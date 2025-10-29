"""csv_to_postman_collection.py
Convert bdd_scenarios.csv -> minimal Postman-style collection.

Tests expect:
  coll["item"][0]["request"]["method"] == "POST"
  coll["item"][0]["request"]["url"]["raw"].endswith("/users")
"""

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
