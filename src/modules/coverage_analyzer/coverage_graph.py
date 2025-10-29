"""coverage_graph.py
Build a simple coverage graph from bdd_scenarios.csv.

Tests expect:
  G.nodes contains BOTH apiName and endpointName strings
  G.edges contains (apiName, endpointName) tuples
"""

import csv

class CoverageGraph:
    def __init__(self, nodes: set[str], edges: set[tuple[str, str]]):
        self.nodes = nodes
        self.edges = edges

def build_graph_from_csv(csv_path: str):
    nodes = set()
    edges = set()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            api_name = row.get("apiName")
            ep_name = row.get("endpointName")

            if api_name:
                nodes.add(api_name)
            if ep_name:
                nodes.add(ep_name)

            if api_name and ep_name:
                edges.add((api_name, ep_name))

    return CoverageGraph(nodes, edges)
