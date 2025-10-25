import os
import json
from src.coverage_engine.runner import generate_bdd

def test_runner_generates_csv(tmp_path, monkeypatch):
    # Build a dummy collection file like the generator expects
    fake_collection = {
        "apis": [
            {
                "apiName": "API_1_Service",
                "endpoints": [
                    {
                        "name": "CreateUser",
                        "method": "POST",
                        "path": "/users",
                        "param_space": {
                            "headers": { "Authorization": ["Bearer VALID", "Bearer EXPIRED"] },
                            "query": {},
                            "body": { "currency": ["USD", "BRL"] }
                        }
                    }
                ]
            }
        ]
    }

    # write to temp
    coll_path = tmp_path / "collection.json"
    with open(coll_path, "w", encoding="utf-8") as f:
        json.dump(fake_collection, f)

    # redirect OUT_DIR and OUT_CSV inside runner so we don't write into real repo
    fake_out_dir = tmp_path / "out"
    fake_out_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("src.coverage_engine.runner.OUT_DIR", str(fake_out_dir))
    monkeypatch.setattr("src.coverage_engine.runner.OUT_CSV", str(fake_out_dir / "bdd_scenarios.csv"))

    csv_path = generate_bdd(str(coll_path))

    assert os.path.exists(csv_path)
    csv_text = open(csv_path, encoding="utf-8").read()
    assert "CreateUser_scn_" in csv_text
    assert "gherkin_and_curl" in csv_text
