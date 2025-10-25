from src.coverage_engine.coverage_calculator import greedy_min_cover

def test_greedy_min_cover_basic():
    param_space = {
        "header.Authorization": ["Bearer VALID", "Bearer EXPIRED"],
        "body.currency": ["USD", "BRL"],
    }

    scenarios = greedy_min_cover(param_space)

    # We should have at least one generated scenario
    assert scenarios
    assert all(isinstance(s, dict) for s in scenarios)

    # Validate that we covered every value at least once
    seen_pairs = {(k, v) for s in scenarios for (k, v) in s.items()}

    assert ("header.Authorization", "Bearer VALID") in seen_pairs
    assert ("header.Authorization", "Bearer EXPIRED") in seen_pairs
    assert ("body.currency", "USD") in seen_pairs
    assert ("body.currency", "BRL") in seen_pairs
