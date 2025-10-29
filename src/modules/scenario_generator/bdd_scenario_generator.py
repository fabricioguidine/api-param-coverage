"""bdd_scenario_generator.py
Simulated "LLM step":
Turn endpoint metadata + concrete param combos into BDD scenario dicts.

Tests expect:
  - generate_bdd_for_endpoint(endpoint_meta, variations, api_key=None)
    returns a list of dicts
  - each dict has:
      "scenario_id"
      "gherkin_and_curl"
  - "gherkin_and_curl" must include
    'curl -X <METHOD> <PATH>'
"""

def _endpoint_display_name(endpoint_def: dict) -> str:
    # tests pass endpointName; runner passes name
    return (
        endpoint_def.get("endpointName")
        or endpoint_def.get("name")
        or "UnnamedEndpoint"
    )

def _build_curl(method: str, path: str) -> str:
    """
    Minimal curl command string.
    Tests only assert substring 'curl -X POST /users', etc.
    """
    return f"curl -X {method} {path}"

def generate_bdd_for_endpoint(endpoint_def: dict, variations=None, api_key=None):
    """
    endpoint_def example:
    {
      "apiName": "API_1_Service",
      "endpointName": "CreateUser",
      "method": "POST",
      "path": "/users"
    }

    variations example:
    [
      {
        "header.Authorization": "Bearer VALID",
        "body.currency": "USD"
      }
    ]

    Returns:
    [
      {
        "scenario_id": "CreateUser_scn_1",
        "gherkin": "Scenario: CreateUser variation 1\n  When I call POST /users\n...",
        "gherkin_and_curl": "Scenario: ...\n\ncurl -X POST /users\n"
      },
      ...
    ]

    api_key is accepted but unused (placeholder for real LLM auth).
    """
    method = endpoint_def.get("method", "GET")
    path = endpoint_def.get("path", "/unknown")
    ep_name = _endpoint_display_name(endpoint_def)

    if variations is None:
        variations = [ {} ]

    results = []
    for i, combo in enumerate(variations, start=1):
        # build param lines
        param_lines = []
        for k, v in combo.items():
            param_lines.append(f"    And {k} = {v}")

        gherkin_block = (
            f"Scenario: {ep_name} variation {i}\n"
            f"  When I call {method} {path}\n"
            f"  Then I should receive 200\n"
        )
        if param_lines:
            gherkin_block += "\n".join(param_lines) + "\n"

        scenario_id = f"{ep_name}_scn_{i}"

        curl_block = _build_curl(method, path)
        gherkin_and_curl = f"{gherkin_block}\n{curl_block}\n"

        results.append({
            "scenario_id": scenario_id,
            "gherkin": gherkin_block,
            "gherkin_and_curl": gherkin_and_curl,
        })

    return results
