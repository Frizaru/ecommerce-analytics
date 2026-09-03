# Technical Data Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, bounded technical audit of every CSV in `data/raw/`, document the data model, and automate critical structural checks without selecting a business problem.

**Architecture:** Reusable audit logic lives in `src/ecommerce_product_analytics/data_audit.py` and returns pandas DataFrames for table, column, key, relationship, journey-coverage, and anomaly summaries. The notebook calls that API and stores concise executed results. Pytest checks structural contracts against the immutable raw snapshot.

**Tech Stack:** Python 3.9, pandas 2.x, pytest 8, JupyterLab/nbconvert, Ruff

**Spec:** `AGENTS.md` and `PROJECT_BRIEF.md`, constrained by the approved technical-audit request dated 2026-09-03

## Global Constraints

- Never write to or modify `data/raw/`.
- Do not select a business problem, primary metric, hypothesis, statistical method, or recommendation.
- Inspect all nine CSV files but avoid open-ended exploratory analysis.
- Record observed facts separately from inferred semantics and limitations.
- Keep result-critical calculations in `src/`, not only in notebook cells.

---

### Task 1: Reusable audit API through TDD

**Files:**
- Create: `tests/test_data_audit.py`
- Create: `src/ecommerce_product_analytics/data_audit.py`

**Interfaces:**
- Produces: `load_tables(raw_dir: Path) -> dict[str, pd.DataFrame]`
- Produces: `profile_tables(tables) -> pd.DataFrame`
- Produces: `profile_columns(tables) -> pd.DataFrame`
- Produces: `profile_keys(tables) -> pd.DataFrame`
- Produces: `profile_relationships(tables) -> pd.DataFrame`
- Produces: `build_quality_findings(tables) -> pd.DataFrame`
- Produces: `build_journey_coverage(tables) -> pd.DataFrame`
- Produces: `value_distribution(table, column) -> pd.DataFrame`

- [x] **Step 1: Write failing unit tests with small in-memory tables**

Test that table profiling reports row/column counts and exact duplicates; key profiling distinguishes a unique composite key from a repeated single column; relationship profiling counts orphan rows and distinct orphan values; and value distribution includes missing values explicitly.

- [x] **Step 2: Run the focused tests and confirm import failure**

Run `.venv/bin/python -m pytest tests/test_data_audit.py -q`.

Expected: collection fails because `ecommerce_product_analytics.data_audit` does not exist.

- [x] **Step 3: Implement the minimal general profiling functions**

Define immutable table/schema/date/key/relationship metadata and the eight public functions listed above. CSV loading must preserve five-digit postal prefixes as strings and parse known date columns with `errors="raise"`.

- [x] **Step 4: Run focused and existing tests**

Run `.venv/bin/python -m pytest tests/test_data_audit.py tests/test_environment.py tests/test_raw_data_integrity.py -q`.

Expected: all tests pass.

### Task 2: Automated contracts for the observed raw snapshot

**Files:**
- Create: `tests/test_source_data_contracts.py`

**Interfaces:**
- Consumes: `load_tables`, `EXPECTED_COLUMNS`, `KEY_CANDIDATES`, and `RELATIONSHIPS`
- Protects: file schemas, stable candidate keys, strict foreign keys, bounded domains, and parseable dates

- [x] **Step 1: Add source-contract tests**

Assert the exact column sequence for all nine tables; uniqueness and non-nullness of the eight accepted candidate keys; zero orphan rows for six strict entity relationships; order statuses equal the eight observed values; review scores stay in 1–5; monetary values are non-negative; and all configured date columns load as datetimes.

- [x] **Step 2: Run the contract tests against all source files**

Run `.venv/bin/python -m pytest tests/test_source_data_contracts.py -q`.

Expected: all contracts pass. Known issues such as untranslated categories, uncovered postal prefixes, nonunique standalone `review_id`, zero-valued payments, and temporal anomalies are documented rather than asserted away.

### Task 3: Reproducible notebook and data dictionary

**Files:**
- Create: `notebooks/01_data_audit.ipynb`
- Modify: `docs/data_dictionary.md`

**Interfaces:**
- Consumes: every public audit function from Task 1 and the raw snapshot
- Produces: an executed audit notebook and a human-readable technical data model

- [x] **Step 1: Build the notebook with bounded sections**

Include scope, loading, table overview, column profile, key checks, relationship checks, three categorical distributions, journey coverage, anomaly counts, and technical limitations. The notebook must call reusable functions rather than duplicate their logic.

- [x] **Step 2: Execute the notebook in place**

Run `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_audit.ipynb --ExecutePreprocessor.timeout=180`.

Expected: execution exits 0 with no cell errors.

- [x] **Step 3: Expand the data dictionary from observed evidence**

Document each table and column, candidate keys, relationship cardinalities, missingness, date ranges, known quality issues, reconstructable journey, missing information, and answerable/non-answerable product-question classes. Mark postal codes as categorical strings and clarify that `customer_id` is order-level while `customer_unique_id` is the repeat-customer identifier.

- [x] **Step 4: Run final verification**

Run the full pytest suite, Ruff, notebook validation, a fresh notebook execution, raw SHA-256 verification, and `git diff --check`.

Expected: every command exits 0, raw hashes remain unchanged, and no business problem or metric is selected.
