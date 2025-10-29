import os
import csv
from modules.artifact_exporter.csv_to_postman_collection import build_collection

def test_build_collection(tmp_path):
    csv_path = tmp_path / "bdd_scenarios.csv"

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["apiName","endpointName","method","path","scenario_id","gherkin_and_curl"])
        w.writerow(["API_1_Service","CreateUser","POST","/users","CreateUser_scn_1","Scenario text\\nThen 200"])

    coll = build_collection(str(csv_path))

    assert "item" in coll
    assert len(coll["item"]) == 1

    item = coll["item"][0]
    assert item["request"]["method"] == "POST"
    assert item["request"]["url"]["raw"].endswith("/users")
