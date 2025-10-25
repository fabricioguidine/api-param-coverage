import os
import csv
import networkx as nx
import matplotlib.pyplot as plt

CSV_INPUT = "src/coverage_engine/outbound/bdd_scenarios.csv"
PNG_OUTPUT = "src/analytics/outbound/graph.png"

def build_graph_from_csv(csv_path: str):
    """
    Create a bipartite-ish graph:
    - One node for each API (apiName)
    - One node for each endpoint (endpointName)
    - Edge apiName -> endpointName
    """
    G = nx.DiGraph()

    if not os.path.exists(csv_path):
        print("[WARN] No CSV found:", csv_path)
        return G

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            api_node = row["apiName"]
            ep_node = row["endpointName"]

            G.add_node(api_node, kind="api")
            G.add_node(ep_node, kind="endpoint")
            G.add_edge(api_node, ep_node)

    return G


def draw_graph(G, out_png: str):
    """
    Lay out and save the graph.
    API nodes get one color, endpoint nodes get another.
    """
    if G.number_of_nodes() == 0:
        print("[WARN] empty graph, nothing to draw")
        return

    os.makedirs(os.path.dirname(out_png), exist_ok=True)

    pos = nx.spring_layout(G, seed=42)

    node_colors = [
        "lightblue" if G.nodes[n].get("kind") == "api" else "lightgray"
        for n in G.nodes()
    ]

    plt.figure(figsize=(8,6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        edge_color="gray",
        node_size=2000,
        font_size=8,
    )
    plt.title("API -> Endpoint Coverage Graph", fontsize=10)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

    print("[OK] wrote", out_png)


def main():
    G = build_graph_from_csv(CSV_INPUT)
    draw_graph(G, PNG_OUTPUT)


if __name__ == "__main__":
    main()
