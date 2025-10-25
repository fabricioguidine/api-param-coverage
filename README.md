## 1. `README.md`

````markdown
# API Param Coverage

This repo does 3 core things:

1. Coverage calculation:
   - Parse a collection of API endpoints (method, path, params)
   - Compute a minimal-ish set of scenarios that covers all parameter/value pairs
   - Generate Gherkin-like BDD text per scenario

2. Postman export:
   - Take the BDD CSV and generate a Postman collection
   - Each Postman request has the BDD text embedded in the Tests tab

3. Analytics:
   - Build a coverage/dependency graph between APIs and endpoints

---

## Workflow

### 1) Generate the BDD CSV

```bash
python -m src.coverage_engine.runner --collection src/coverage_engine/outbound/sample.json
````

This writes:
`src/coverage_engine/outbound/bdd_scenarios.csv`

### 2) Export to Postman

```bash
python src/postman_export/csv_to_postman_collection.py
```

This writes something like:
`src/postman_export/outbound/postman_1699999999.json`

You can import that JSON file directly into Postman.

### 3) Generate the coverage graph

```bash
python src/analytics/coverage_graph.py
```

This writes:
`src/analytics/outbound/graph.png`

The graph links API -> endpoint nodes based on the CSV.

### 4) Run tests

```bash
pytest
```

---

## Environment

Create a `.env` file in the project root with:

```text
OPENAI_API_KEY=sk-proj-your-key-here
```

Your real key goes there. We currently stub LLM behavior and don't actually call the OpenAI API, but the key is reserved for future use.

---

## Repo Layout

```text
src/
  coverage_engine/      # scenario generation, coverage math, BDD generation
  postman_export/       # builds Postman collection from CSV
  analytics/            # builds graph from CSV

test/
  coverage_engine/      # pytest unit tests for coverage logic and runner
  postman_export/       # pytest for postman export shape
  analytics/            # pytest for analytics module

outbound/               # diagnostic/export artifacts (structure snapshots, etc.)
```

````

---

## 2. `requirements.txt`

```text
pytest
python-dotenv
networkx
matplotlib
pydantic
openai
````