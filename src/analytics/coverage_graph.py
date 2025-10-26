import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = "src/coverage_engine/outbound/bdd_scenarios.csv"
OUT_DIR = "src/analytics/outbound"

# How many endpoints to show in the chart (keep it readable)
TOP_N_ENDPOINTS = 25

# Endpoints with scenario_count <= this will be flagged as "under-tested"
UNDER_TESTED_THRESHOLD = 1


def load_scenarios(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No BDD CSV found at {csv_path}. "
            "Run `python -m src.coverage_engine.runner --generate-sample` first."
        )
    df = pd.read_csv(csv_path)
    # sanity columns
    required = {"apiName", "endpointName", "method", "path", "scenario_id", "gherkin_and_curl"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    return df


def compute_coverage(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      per_endpoint: index (apiName, endpointName) -> scenario_count
      per_api:      index apiName -> endpoint_count, scenario_count
    """
    per_endpoint = (
        df.groupby(["apiName", "endpointName"])
          .size()
          .rename("scenario_count")
          .reset_index()
    )

    per_api = (
        per_endpoint.groupby("apiName")
        .agg(endpoint_count=("endpointName", "nunique"),
             scenario_count=("scenario_count", "sum"))
        .reset_index()
        .sort_values("scenario_count", ascending=False)
    )

    return per_endpoint, per_api


def write_text_report(df: pd.DataFrame, per_endpoint: pd.DataFrame, per_api: pd.DataFrame, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = int(datetime.now().timestamp())
    out_path = os.path.join(out_dir, f"coverage_report_{ts}.txt")

    total_scenarios = len(df)
    total_endpoints = per_endpoint["endpointName"].nunique()
    total_apis = per_api["apiName"].nunique()

    # Top / Bottom endpoints by scenario count
    top_endpoints = per_endpoint.sort_values("scenario_count", ascending=False).head(10)
    bottom_endpoints = per_endpoint.sort_values("scenario_count", ascending=True).head(10)

    # Under-tested endpoints
    under_tested = per_endpoint[per_endpoint["scenario_count"] <= UNDER_TESTED_THRESHOLD] \
        .sort_values(["scenario_count", "apiName", "endpointName"])

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=== API PARAM COVERAGE REPORT ===\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n\n")

        f.write(">> GLOBAL TOTALS\n")
        f.write(f"- APIs:        {total_apis}\n")
        f.write(f"- Endpoints:   {total_endpoints}\n")
        f.write(f"- Scenarios:   {total_scenarios}\n\n")

        f.write(">> PER-API SUMMARY (sorted by total scenarios)\n")
        f.write(per_api.to_string(index=False))
        f.write("\n\n")

        f.write(">> TOP 10 ENDPOINTS BY SCENARIOS\n")
        f.write(top_endpoints.to_string(index=False))
        f.write("\n\n")

        f.write(">> BOTTOM 10 ENDPOINTS BY SCENARIOS\n")
        f.write(bottom_endpoints.to_string(index=False))
        f.write("\n\n")

        f.write(f">> UNDER-TESTED (scenario_count <= {UNDER_TESTED_THRESHOLD})\n")
        if under_tested.empty:
            f.write("None 🎉\n")
        else:
            f.write(under_tested.to_string(index=False))
            f.write("\n")

    print(f"[OK] Text coverage report saved at: {out_path}")
    return out_path


def save_readable_chart(per_endpoint: pd.DataFrame, out_dir: str) -> str:
    """
    Create a single, readable image:
     - Horizontal bar chart
     - X axis = number of scenarios
     - Y axis = endpoint names (shortened)
     - Color by API
     - Annotated values on bars
    """
    os.makedirs(out_dir, exist_ok=True)
    ts = int(datetime.now().timestamp())
    out_path = os.path.join(out_dir, f"coverage_graph_{ts}.png")

    # Build a short label: "API :: METHOD_resource_..." trimmed
    data = per_endpoint.copy()
    # We try to extract method prefix from endpointName for readability
    short_names = []
    for _, row in data.iterrows():
        ep = row["endpointName"]
        # Keep method (prefix until first _) and first two tokens
        parts = ep.split("_")
        if len(parts) >= 2:
            short = f"{parts[0]}_{parts[1]}"
        else:
            short = ep
        short_names.append(f"{row['apiName']} :: {short}")
    data["label"] = short_names

    # Keep top N by scenario_count (most relevant)
    data = data.sort_values("scenario_count", ascending=True).tail(TOP_N_ENDPOINTS)

    fig_h = max(6, 0.35 * len(data))  # dynamic height so labels fit
    plt.figure(figsize=(14, fig_h))

    # Color by API (categorical)
    apis = data["apiName"].unique().tolist()
    api_color = {api: plt.cm.tab20(i % 20) for i, api in enumerate(apis)}
    colors = data["apiName"].map(api_color)

    plt.barh(data["label"], data["scenario_count"], color=colors, edgecolor="black", alpha=0.9)

    # Annotate counts at end of each bar
    for i, (cnt) in enumerate(data["scenario_count"]):
        plt.text(cnt + 0.1, i, str(cnt), va="center", fontsize=9)

    plt.xlabel("Number of Scenarios")
    plt.title(f"Endpoint Coverage (Top {min(TOP_N_ENDPOINTS, len(per_endpoint))} by scenarios)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"[OK] Readable coverage chart saved at: {out_path}")
    return out_path


def main():
    df = load_scenarios(CSV_PATH)
    per_endpoint, per_api = compute_coverage(df)

    # 1) TXT report
    write_text_report(df, per_endpoint, per_api, OUT_DIR)

    # 2) Readable image
    save_readable_chart(per_endpoint, OUT_DIR)


if __name__ == "__main__":
    main()
