from modules.scenario_generator.llm_bdd_generator import generate_bdd_for_endpoint

def test_generate_bdd_for_endpoint_stub():
    endpoint_meta = {
        "apiName": "API_1_Service",
        "endpointName": "CreateUser",
        "method": "POST",
        "path": "/users"
    }

    scenarios = [
        {
            "header.Authorization": "Bearer VALID",
            "body.currency": "USD"
        }
    ]

    result = generate_bdd_for_endpoint(endpoint_meta, scenarios, api_key=None)

    assert len(result) == 1
    first = result[0]

    assert "scenario_id" in first
    assert "gherkin_and_curl" in first
    assert "curl -X POST /users" in first["gherkin_and_curl"]
