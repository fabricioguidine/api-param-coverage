import json
from .models import ParamSpace, Endpoint

def load_collection(path_json: str):
    """
    Expected shape of collection JSON:
    {
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
    """
    with open(path_json, "r", encoding="utf-8") as f:
        raw = json.load(f)

    endpoints = []

    for api_block in raw.get("apis", []):
        api_name = api_block.get("apiName", "UNKNOWN_API")

        for ep in api_block.get("endpoints", []):
            ps_raw = ep.get("param_space", {})

            param_space = ParamSpace(
                headers=ps_raw.get("headers", {}),
                query=ps_raw.get("query", {}),
                body=ps_raw.get("body", {}),
            )

            endpoints.append(
                Endpoint(
                    apiName=api_name,
                    endpointName=ep["name"],
                    method=ep["method"],
                    path=ep["path"],
                    param_space=param_space,
                )
            )

    return endpoints


def flatten_param_space(endpoint: Endpoint):
    """
    Converts ParamSpace into a flat dict that coverage_calculator can consume.

    Example:
        {
            "header.Authorization": ["Bearer VALID", "Bearer EXPIRED"],
            "query.locale": ["en-US", "pt-BR"],
            "body.currency": ["USD", "BRL"]
        }
    """
    result = {}

    combos = [
        ("header", endpoint.param_space.headers),
        ("query",  endpoint.param_space.query),
        ("body",   endpoint.param_space.body),
    ]

    for prefix, group in combos:
        for param_name, values in group.items():
            key = f"{prefix}.{param_name}"
            vals = values if values else ["<default>"]
            result[key] = vals

    return result
