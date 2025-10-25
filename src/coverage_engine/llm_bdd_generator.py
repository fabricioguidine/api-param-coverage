def generate_bdd_for_endpoint(meta, scenarios, api_key=None):
    """
    meta example:
        {
            "apiName": "API_1_Service",
            "endpointName": "CreateUser",
            "method": "POST",
            "path": "/users"
        }

    scenarios example:
        [
            {
                "header.Authorization": "Bearer VALID",
                "body.currency": "USD"
            }
        ]

    returns:
        [
            {
                "scenario_id": "CreateUser_scn_1",
                "gherkin_and_curl": "Given ...\nWhen ...\nThen ..."
            },
            ...
        ]
    """

    out = []

    for i, scenario in enumerate(scenarios, start=1):
        gherkin_text = (
            "Scenario: happy path\n"
            f"  Given parameters {scenario}\n"
            f"  When I call {meta['method']} {meta['path']}\n"
            "  Then I should receive 200 OK\n"
            "  And I can run:\n"
            f"    curl -X {meta['method']} {meta['path']}\n"
        )

        out.append(
            {
                "scenario_id": f"{meta['endpointName']}_scn_{i}",
                "gherkin_and_curl": gherkin_text,
            }
        )

    return out
