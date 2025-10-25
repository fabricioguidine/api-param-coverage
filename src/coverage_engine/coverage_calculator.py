import itertools

def greedy_min_cover(space):
    """
    space is a dict:
        {
            "header.Authorization": ["Bearer VALID", "Bearer EXPIRED"],
            "body.currency": ["USD", "BRL"],
            ...
        }

    We produce a minimal-ish list of combinations (scenarios)
    such that every (param, value) pair appears in at least one scenario.
    """
    if not space:
        return []

    keys = list(space.keys())

    # generate full cartesian
    combos = [
        dict(zip(keys, values))
        for values in itertools.product(*space.values())
    ]

    # all unique pairs that MUST be covered
    required_pairs = {(k, v) for k, vals in space.items() for v in vals}

    covered = set()
    chosen = []

    while covered != required_pairs:
        # choose the combo that covers the most not-yet-covered pairs
        best_combo = None
        best_gain = -1
        for combo in combos:
            gain = len(set(combo.items()) - covered)
            if gain > best_gain:
                best_gain = gain
                best_combo = combo

        if best_combo is None:
            break

        chosen.append(best_combo)
        covered |= set(best_combo.items())

    return chosen
