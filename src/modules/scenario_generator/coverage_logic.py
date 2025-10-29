"""coverage_logic.py
Functions to reason about param coverage.

Export:
    greedy_min_cover(param_matrix) -> list[dict]
"""

def greedy_min_cover(param_matrix: dict) -> list[dict]:
    """
    Given:
        {
          "header.Authorization": ["Bearer VALID", "Bearer EXPIRED"],
          "body.currency": ["USD", "BRL"],
        }

    Build a compact set of representative combos.

    Strategy: index-zip. For each index i, take the i-th element
    from each param list, falling back to the last if needed.
    """
    keys = list(param_matrix.keys())
    lists_ = [param_matrix[k] for k in keys]
    if not lists_:
        return []

    max_len = max(len(vs) for vs in lists_)
    combos = []
    for i in range(max_len):
        row = {}
        for k, vs in zip(keys, lists_):
            idx = i if i < len(vs) else len(vs) - 1
            row[k] = vs[idx]
        combos.append(row)
    return combos
