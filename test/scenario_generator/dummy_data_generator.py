import os
import json
import random
from datetime import datetime

OUT_DIR = "src/coverage_engine/outbound"

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# We now declare params with metadata instead of just list[str]
# - values: list of candidate values (strings)
# - required: this param must exist for the request to "reach business logic"
# - blocks_logic_if_invalid: if this param is invalid/missing, the request fails early
#   and we DO NOT need to waste combinations with other params
HEADER_PARAM_MODEL = {
    "Authorization": {
        "values": [
            "Bearer VALID_TOKEN",        # happy path
            "Bearer EXPIRED_TOKEN",      # should 401
            "Bearer MISSING_SCOPE"       # should 403
        ],
        "required": True,
        "blocks_logic_if_invalid": True
    },
    "X-Tenant-ID": {
        "values": ["tenant_a", "tenant_b"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "Content-Type": {
        "values": ["application/json", "application/xml"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "Accept": {
        "values": ["application/json"],
        "required": False,
        "blocks_logic_if_invalid": False
    }
}

QUERY_PARAM_MODEL = {
    "locale": {
        "values": ["en-US", "pt-BR", "es-CL"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "limit": {
        "values": ["10", "50", "100"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "sort": {
        "values": ["asc", "desc"],
        "required": False,
        "blocks_logic_if_invalid": False
    }
}

BODY_PARAM_MODEL = {
    "currency": {
        "values": ["USD", "BRL", "EUR"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "role": {
        "values": ["admin", "user", "readonly"],
        "required": False,
        "blocks_logic_if_invalid": False
    },
    "status": {
        "values": ["active", "blocked", "pending"],
        "required": False,
        "blocks_logic_if_invalid": False
    }
}


def _random_param_subset(model: dict) -> dict:
    """
    Take a dict like { "Authorization": {...}, "X-Tenant-ID": {...} }
    Pick a random non-empty subset of keys for this endpoint,
    and return ONLY those param definitions (same metadata format).
    """
    if not model:
        return {}

    keys = list(model.keys())
    how_many = random.randint(1, len(keys))
    chosen = random.sample(keys, how_many)

    subset = {}
    for k in chosen:
        subset[k] = model[k]
    return subset


def _generate_endpoint(api_index: int, ep_index: int) -> dict:
    method = random.choice(HTTP_METHODS)

    base = f"resource_{ep_index+1}"
    path = random.choice([
        f"/api_{api_index+1}/{base}",
        f"/api_{api_index+1}/{base}/{{id}}",
        f"/api_{api_index+1}/{base}/sync",
        f"/api_{api_index+1}/{base}/details",
    ])

    # pick random subset of headers/query/body definitions for THIS endpoint
    headers_def = _random_param_subset(HEADER_PARAM_MODEL)
    query_def = _random_param_subset(QUERY_PARAM_MODEL)
    body_def = {}
    if method in ("POST", "PUT", "PATCH"):
        body_def = _random_param_subset(BODY_PARAM_MODEL)

    return {
        "name": f"{method}_{base}_{ep_index+1}",
        "method": method,
        "path": path,
        "param_space": {
            "headers": headers_def,
            "query": query_def,
            "body": body_def
        }
    }


def _generate_api(api_index: int, ep_count: int) -> dict:
    endpoints = []
    for i in range(ep_count):
        endpoints.append(_generate_endpoint(api_index, i))
    return {
        "apiName": f"API_{api_index+1}_Service",
        "endpoints": endpoints
    }


def make_random_collection(
    min_apis=1,
    max_apis=10,
    min_endpoints=1,
    max_endpoints=5
):
    """
    Returns:
    {
      "apis": [
        {
          "apiName": "...",
          "endpoints": [
            {
              "name": "...",
              "method": "...",
              "path": "...",
              "param_space": {
                 "headers": { paramName: {values: [...], required: bool, blocks_logic_if_invalid: bool}, ... },
                 "query":   { ... },
                 "body":    { ... }
              }
            },
            ...
          ]
        },
        ...
      ]
    }
    """
    api_count = random.randint(min_apis, max_apis)
    apis = []

    for api_i in range(api_count):
        ep_count = random.randint(min_endpoints, max_endpoints)
        apis.append(_generate_api(api_i, ep_count))

    return {"apis": apis}


def create_sample_collection(
    min_apis=1,
    max_apis=10,
    min_endpoints=1,
    max_endpoints=5
):
    os.makedirs(OUT_DIR, exist_ok=True)

    data = make_random_collection(
        min_apis=min_apis,
        max_apis=max_apis,
        min_endpoints=min_endpoints,
        max_endpoints=max_endpoints,
    )

    ts = int(datetime.now().timestamp())
    out_path = os.path.join(OUT_DIR, f"sample_{ts}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    abs_path = os.path.abspath(out_path)
    print(f"[OK] Dummy collection created at: {abs_path}")
    return abs_path


if __name__ == "__main__":
    create_sample_collection()
