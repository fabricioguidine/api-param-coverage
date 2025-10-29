"""utils.py
Shared helpers for scenario generation & runner.
"""

import os
import itertools

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path

def expand_param_space(param_space: dict) -> list[dict]:
    """
    Expand param_space (headers/query/body) to a list of flat combos.

    Example param_space:
    {
        "headers": { "Authorization": ["Bearer A", "Bearer B"] },
        "query":   { "limit": [10, 20] },
        "body":    { "currency": ["USD","BRL"] }
    }

    Output sample:
    [
      {
        "headers.Authorization": "Bearer A",
        "query.limit": 10,
        "body.currency": "USD"
      },
      ...
    ]
    """
    buckets = []

    for section_key in ("headers", "query", "body"):
        section_vals = param_space.get(section_key, {}) or {}
        expanded = []
        for field, values in section_vals.items():
            expanded.append([
                (f"{section_key}.{field}", v) for v in values
            ])
        if not expanded:
            continue

        # Cartesian product for this section
        section_products = [
            dict(pairs) for pairs in itertools.product(*expanded)
        ]
        buckets.append(section_products)

    if not buckets:
        return []

    combos = buckets[0]
    for other in buckets[1:]:
        new_list = []
        for a in combos:
            for b in other:
                merged = {}
                merged.update(a)
                merged.update(b)
                new_list.append(merged)
        combos = new_list

    return combos
