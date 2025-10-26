import json
import os
import csv
from .models import ParamSpace, Endpoint


def load_collection(path_json: str):
    """
    Load our internal file:
    {
      "apis": [
        {
          "apiName": "API_1_Service",
          "endpoints": [
            {
              "name": "GET_resource_1_1",
              "method": "GET",
              "path": "/api_1/resource_1",
              "param_space": {
                "headers": {
                  "Authorization": {
                    "values": [...],
                    "required": true,
                    "blocks_logic_if_invalid": true
                  },
                  ...
                },
                "query": {...},
                "body": {...}
              }
            },
            ...
          ]
        }
      ]
    }
    """
    with open(path_json, "r", encoding="utf-8") as f:
        raw = json.load(f)

    endpoints = []

    for api_block in raw.get("apis", []):
        api_name = api_block.get("apiName", "UNKNOWN_API")

        for ep in api_block.get("endpoints", []):
            ps_raw = ep.get("param_space", {})

            # we store param_space exactly as-is (dicts of dicts with metadata)
            param_space = ParamSpace(
                headers=ps_raw.get("headers", {}),
                query=ps_raw.get("query", {}),
                body=ps_raw.get("body", {}),
            )

            endpoints.append(
                Endpoint(
                    apiName=api_name,
                    endpointName=ep.get("name", "UNKNOWN_ENDPOINT"),
                    method=ep.get("method", "GET"),
                    path=ep.get("path", "/unknown"),
                    param_space=param_space,
                )
            )

    return endpoints


def _merge_param_spaces(endpoint: Endpoint):
    """
    Take endpoint.param_space and flatten into a dict of:
    {
      "header.Authorization": {
         "values": [...],
         "required": True/False,
         "blocks_logic_if_invalid": True/False
      },
      "query.limit": {...},
      "body.currency": {...}
    }

    NOTE: this is richer than before, because now each param is not just values,
    it also carries constraint metadata.
    """
    merged = {}

    groups = [
        ("header", endpoint.param_space.headers),
        ("query", endpoint.param_space.query),
        ("body", endpoint.param_space.body),
    ]

    for prefix, params in groups:
        for param_name, meta in params.items():
            # meta is expected to be like:
            # {
            #    "values": [...],
            #    "required": bool,
            #    "blocks_logic_if_invalid": bool
            # }
            merged[f"{prefix}.{param_name}"] = {
                "values": meta.get("values", []),
                "required": bool(meta.get("required", False)),
                "blocks_logic_if_invalid": bool(meta.get("blocks_logic_if_invalid", False)),
            }

    return merged


def build_coverage_rows(endpoints, coverage_calculator_mod, llm_bdd_generator_mod):
    """
    For each endpoint:
      1. Flatten param definitions (with metadata)
      2. Ask coverage_calculator_mod.smart_minimal_scenarios() for scenarios
      3. Ask llm_bdd_generator_mod.generate_bdd_for_endpoint() for Gherkin/cURL text
      4. Aggregate rows for CSV
    """
    rows = []

    for ep in endpoints:
        rich_space = _merge_param_spaces(ep)

        scenarios = coverage_calculator_mod.smart_minimal_scenarios(rich_space)

        endpoint_meta = {
            "apiName": ep.apiName,
            "endpointName": ep.endpointName,
            "method": ep.method,
            "path": ep.path,
        }

        bdd_list = llm_bdd_generator_mod.generate_bdd_for_endpoint(
            endpoint_meta,
            scenarios,
            api_key=None  # wire your OPENAI_API_KEY here when you're ready to call LLM for real
        )

        for item in bdd_list:
            rows.append(
                {
                    "apiName": ep.apiName,
                    "endpointName": ep.endpointName,
                    "method": ep.method,
                    "path": ep.path,
                    "scenario_id": item["scenario_id"],
                    # escape newlines for CSV storage
                    "gherkin_and_curl": item["gherkin_and_curl"].replace("\n", "\\n"),
                }
            )

    return rows


def write_rows_to_csv(rows, out_dir="src/coverage_engine/outbound", filename="bdd_scenarios.csv"):
    """
    Write scenario coverage + BDD text into a CSV.
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    header = [
        "apiName",
        "endpointName",
        "method",
        "path",
        "scenario_id",
        "gherkin_and_curl",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return out_path
