"""
coverage_calculator.py

This module is responsible for generating the minimal set of test scenarios
for an endpoint, respecting constraints like required auth headers and
avoiding useless cross-product explosion.

Input (rich_space) looks like:
{
  "header.Authorization": {
      "values": ["Bearer VALID_TOKEN", "Bearer EXPIRED_TOKEN", "Bearer MISSING_SCOPE"],
      "required": True,
      "blocks_logic_if_invalid": True
  },
  "header.X-Tenant-ID": {
      "values": ["tenant_a", "tenant_b"],
      "required": False,
      "blocks_logic_if_invalid": False
  },
  "query.limit": {
      "values": ["10", "50", "100"],
      "required": False,
      "blocks_logic_if_invalid": False
  },
  ...
}

We produce a list of scenario dicts, e.g.:

[
  {
    "header.Authorization": "Bearer VALID_TOKEN",
    "header.X-Tenant-ID": "tenant_a",
    "query.limit": "10"
  },
  {
    "header.Authorization": "Bearer VALID_TOKEN",
    "header.X-Tenant-ID": "tenant_b",
    "query.limit": "50"
  },
  {
    "header.Authorization": "Bearer EXPIRED_TOKEN"
    // negative path, no need to explore other params
  },
  ...
]

Rules implemented:
1. HAPPY-PATH SET:
   - Pick ONE "good" value for every param that is required & blocks_logic_if_invalid.
     We assume the *first* value is "good" (e.g. VALID_TOKEN).
   - Then combine all other params to get coverage of their possible values
     using a simple pairwise-ish greedy strategy (approximation).
     In other words, explore variations across non-blocking params while keeping
     the blocking param on its first value.

2. NEGATIVE/GUARDRAIL SET:
   - For any param where blocks_logic_if_invalid=True and it has multiple values,
     generate ONE scenario per "bad" value after index 0.
     That scenario ONLY flips that param. We DO NOT mix other params.
     Rationale: invalid auth 401 is enough; no need to see tenant variations there.

This keeps test count small but meaningful.
"""

from itertools import product


def _split_params(rich_space):
    """
    Separate parameters into:
    - blocking_required_params: those with required=True and blocks_logic_if_invalid=True
    - other_params: everything else

    Returns:
      (blocking_required_params, other_params)

    Each is dict[param_name] = { "values": [...], "required": bool, ... }
    """
    blocking_required = {}
    others = {}

    for pname, meta in rich_space.items():
        required = meta.get("required", False)
        blocking = meta.get("blocks_logic_if_invalid", False)

        if required and blocking:
            blocking_required[pname] = meta
        else:
            others[pname] = meta

    return blocking_required, others


def _build_happy_path_scenarios(blocking_required, others):
    """
    Build scenarios that explore "business logic" combinations.

    Steps:
    1. Lock each blocking+required param to its first value (assume index 0 is 'valid').
    2. For all other params, we try to cover their values in a compact way.

    We'll do a naive greedy coverage:
    - We'll iterate each non-blocking param and create a scenario for each of its values,
      reusing defaults for the rest.
    - Defaults for each non-blocking param = first value.
    """

    # 1. base/default scenario dict with "good" values
    base = {}

    # blocking required params -> pick first value as "good"
    for pname, meta in blocking_required.items():
        vals = meta.get("values", [])
        base[pname] = vals[0] if vals else None

    # others -> also pick first value as default for now
    for pname, meta in others.items():
        vals = meta.get("values", [])
        base[pname] = vals[0] if vals else None

    scenarios = []

    # always include the base scenario
    scenarios.append(dict(base))

    # now expand per param to exercise its other values
    for pname, meta in others.items():
        vals = meta.get("values", [])
        if len(vals) <= 1:
            continue  # nothing else to vary
        # for each alternative beyond index 0, clone base and flip just that param
        for alt in vals[1:]:
            scenario = dict(base)
            scenario[pname] = alt
            scenarios.append(scenario)

    # also expand blocking_required params ONLY IF they have >1 "good-ish" values
    # but for happy path we actually do NOT flip them here because flips might be invalid
    # so we keep them locked to the first value in happy paths.

    # deduplicate scenarios
    unique = []
    seen = set()
    for sc in scenarios:
        key = tuple(sorted(sc.items()))
        if key not in seen:
            seen.add(key)
            unique.append(sc)

    return unique


def _build_negative_guardrail_scenarios(blocking_required):
    """
    For each blocking+required param, produce ONE scenario for each "bad" value
    beyond index 0.

    Example:
    Authorization.values = ["Bearer VALID_TOKEN", "Bearer EXPIRED_TOKEN", "Bearer MISSING_SCOPE"]

    -> we generate:
    { "header.Authorization": "Bearer EXPIRED_TOKEN" }
    { "header.Authorization": "Bearer MISSING_SCOPE" }

    (No other params included, because once auth is bad, everything else is irrelevant.)
    """
    neg_scenarios = []
    for pname, meta in blocking_required.items():
        vals = meta.get("values", [])
        if len(vals) <= 1:
            continue
        # assume index 0 is "valid/happy", others are negative
        for bad_val in vals[1:]:
            neg_scenarios.append({
                pname: bad_val
            })
    return neg_scenarios


def smart_minimal_scenarios(rich_space):
    """
    Public function called by utils.build_coverage_rows().
    """

    blocking_required, others = _split_params(rich_space)

    happy = _build_happy_path_scenarios(blocking_required, others)
    neg = _build_negative_guardrail_scenarios(blocking_required)

    # merge and dedupe
    all_scenarios = happy + neg

    final_unique = []
    seen = set()
    for sc in all_scenarios:
        key = tuple(sorted(sc.items()))
        if key not in seen:
            seen.add(key)
            final_unique.append(sc)

    return final_unique
