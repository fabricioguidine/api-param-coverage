# 🧩 API Param Coverage

**Automated API Scenario Generation, Coverage Analysis, and Export Tools**

`api-param-coverage` is a modular Python toolkit that helps QA engineers and developers:

* Generate dummy API parameter variations
* Transform them into **BDD-style Gherkin scenarios** (optionally using an LLM)
* Export them into **Postman collections**
* Analyze **coverage graphs** and **report summaries** for quick visibility.

It’s designed for extensibility and smooth automation in continuous testing pipelines.

---

## 🚀 Features

| Category               | Description                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| **Scenario Generator** | Expands API parameter spaces into representative combinations using a greedy coverage algorithm.  |
| **LLM BDD Generator**  | Converts endpoint metadata and parameter variations into human-readable BDD-style test scenarios. |
| **Runner**             | Executes the full generation pipeline and writes `bdd_scenarios.csv`.                             |
| **Coverage Analyzer**  | Builds a graph showing endpoint-to-API relationships and produces summary reports.                |
| **Artifact Exporter**  | Converts the CSV output into a lightweight Postman collection JSON.                               |
| **CLI Tool**           | Allows you to run the entire flow or individual steps from the command line.                      |

---

## 🧠 Functional Flow

```
+---------------------+
|  Input Spec (JSON)  |
|  apis → endpoints   |
+---------+-----------+
          |
          v
+---------------------------+
|  Scenario Generator       |
|  - Greedy Param Expansion |
|  - Gherkin BDD Generator  |
+-------------+-------------+
              |
              v
+-----------------------------+
|  Coverage Engine (Runner)   |
|  - Writes bdd_scenarios.csv |
+-------------+---------------+
              |
              +-------------------------------+
              |                               |
              v                               v
+-------------------------+     +--------------------------+
| Coverage Analyzer       |     | Artifact Exporter        |
| - Graph & Report        |     | - Postman JSON Generator |
+-------------------------+     +--------------------------+
```

---

## 🧰 Directory Structure

```
src/
├── api_param_coverage/
│   ├── __init__.py
│   └── __main__.py             # CLI entrypoint
│
├── modules/
│   ├── artifact_exporter/
│   │   └── csv_to_postman_collection.py
│   ├── coverage_analyzer/
│   │   ├── coverage_graph.py
│   │   └── metrics_visualization.py
│   ├── scenario_generator/
│   │   ├── utils.py
│   │   ├── coverage_logic.py
│   │   ├── bdd_scenario_generator.py
│   │   └── runner.py
│   └── domain_models/         # Reserved for type/entity models
│
├── coverage_engine/
│   ├── __init__.py
│   └── runner.py              # Legacy shim for backward compat
│
└── common/                    # Shared logic (future)
```

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/api-param-coverage.git
cd api-param-coverage
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate on Linux/Mac
pip install -r requirements.txt
```

---

## 🧩 Usage

### 1️⃣ Generate BDD Scenarios from an API Spec

Example `spec.json`:

```json
{
  "apis": [
    {
      "apiName": "UserService",
      "endpoints": [
        {
          "name": "CreateUser",
          "method": "POST",
          "path": "/users",
          "param_space": {
            "headers": { "Authorization": ["Bearer VALID", "Bearer EXPIRED"] },
            "body": { "currency": ["USD", "BRL"] }
          }
        }
      ]
    }
  ]
}
```

Run:

```bash
py -m src.api_param_coverage scenarios spec.json out/
```

✅ Outputs:

* `out/bdd_scenarios.csv`

---

### 2️⃣ Export to Postman

```bash
py -m src.api_param_coverage postman out/bdd_scenarios.csv
```

✅ Outputs:

* `out/bdd_scenarios.postman.json`

---

### 3️⃣ Generate Coverage Report

```bash
py -m src.api_param_coverage coverage out/bdd_scenarios.csv out/
```

✅ Outputs:

* `out/coverage_summary.txt`

---

## 🧪 Running Tests

All modules are validated through `pytest`.

```bash
pytest -v
```

Expected output:

```
collected 5 items

test/artifact_exporter/test_csv_to_postman_collection.py .    [20%]
test/coverage_analyzer/test_coverage_graph.py .               [40%]
test/scenario_generator/test_coverage_calculator.py .         [60%]
test/scenario_generator/test_llm_bdd_generator.py .           [80%]
test/scenario_generator/test_runner_flow.py .                 [100%]

✅ 5 passed in 0.24s
```

---

## 🛠 Developer Utilities

To reset or heal the repository (auto-regenerate modules, structure, and tests), just run:

```bash
py reorganize.py
```

It will:

* Recreate missing `__init__.py` files
* Move stray tests into `/test`
* Rebuild all key modules
* Ensure CLI + legacy compatibility
* Restore passing test state

---

## 🧩 Key Modules Summary

| Module                         | Purpose                                      |
| ------------------------------ | -------------------------------------------- |
| `utils.py`                     | File operations, param expansion             |
| `coverage_logic.py`            | Greedy minimal parameter coverage generation |
| `bdd_scenario_generator.py`    | Gherkin + curl BDD text generation           |
| `runner.py`                    | Core pipeline orchestration                  |
| `coverage_graph.py`            | Coverage graph building                      |
| `csv_to_postman_collection.py` | Postman-compatible export                    |
| `metrics_visualization.py`     | Coverage report generator                    |
| `__main__.py`                  | CLI commands entrypoint                      |

---

## 🧭 CLI Overview

| Command     | Description                                 |
| ----------- | ------------------------------------------- |
| `scenarios` | Generate CSV of BDD scenarios from API spec |
| `postman`   | Create Postman JSON from generated CSV      |
| `coverage`  | Produce coverage summary report             |

Run `py -m src.api_param_coverage --help` for full options.

---

## 📄 License

MIT License © 2025 Fabrício Guidine