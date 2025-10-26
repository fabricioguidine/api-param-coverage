import os
import json
import uuid
from datetime import datetime
from glob import glob


ENGINE_OUT_DIR = "src/coverage_engine/outbound"
OUT_DIR = "src/postman_export/outbound"


def newest_sample():
    """Automatically get the latest sample_*.json from ENGINE_OUT_DIR"""
    pattern = os.path.join(ENGINE_OUT_DIR, "sample_*.json")
    files = sorted(glob(pattern))
    if not files:
        raise FileNotFoundError("No sample_*.json found. Run the runner first.")
    return files[-1]


def convert_to_postman(internal_json):
    """Convert internal model → valid Postman v2.1 collection"""
    apis = internal_json.get("apis", [])
    folders = []
    for api in apis:
        endpoints = []
        for ep in api["endpoints"]:
            request = {
                "method": ep["method"],
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "url": {
                    "raw": f"https://api.example.com{ep['path']}",
                    "host": ["api", "example", "com"],
                    "path": ep["path"].strip("/").split("/")
                }
            }
            endpoints.append({"name": ep["name"], "request": request})
        folders.append({"name": api["apiName"], "item": endpoints})

    return {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": f"Generated Collection {datetime.utcnow().isoformat()}Z",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": folders
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sample_path = newest_sample()
    print(f"[INFO] Auto-detected sample: {sample_path}")

    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    postman_json = convert_to_postman(data)

    ts = int(datetime.utcnow().timestamp())
    out_path = os.path.join(OUT_DIR, f"postman_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(postman_json, f, indent=2)

    abs_path = os.path.abspath(out_path)
    print(f"[OK] Postman collection created at: {abs_path}")


if __name__ == "__main__":
    main()
