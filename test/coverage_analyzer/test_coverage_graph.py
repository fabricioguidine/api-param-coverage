from modules.coverage_analyzer.coverage_graph import build_graph_from_csv

def test_build_graph_from_csv(tmp_path):
    csvf = tmp_path / "bdd_scenarios.csv"

    csvf.write_text(
        "apiName,endpointName,method,path,scenario_id,gherkin_and_curl\n"
        "BillingAPI,CreateInvoice,POST,/invoice,CreateInvoice_scn_1,stub\n",
        encoding="utf-8",
    )

    G = build_graph_from_csv(str(csvf))

    assert "BillingAPI" in G.nodes
    assert "CreateInvoice" in G.nodes
    assert ("BillingAPI", "CreateInvoice") in G.edges
