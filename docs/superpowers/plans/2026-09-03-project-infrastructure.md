# Project Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and verify the minimal reproducible repository infrastructure needed to begin a technical audit of the existing e-commerce CSV files.

**Architecture:** A standard `src`-layout Python package is installed into a project-local virtual environment from `pyproject.toml`. Raw CSV files remain ignored and immutable, while a tracked checksum manifest and pytest safeguard detect changes. Notebooks and documentation contain stage boundaries only; analytical code and decisions are deferred.

**Tech Stack:** Python 3.9+, setuptools, pandas, JupyterLab, ipykernel, pytest, Ruff

**Spec:** `docs/superpowers/specs/2026-09-03-project-infrastructure-design.md`

## Global Constraints

- Do not perform business analysis or select a business problem.
- Do not define product metrics, hypotheses, statistical methods, or recommendations.
- Never modify or overwrite any file in `data/raw/`.
- Derived datasets may only be written to `data/interim/` or `data/processed/`.
- Use only dependencies justified for the initial audit, notebook workflow, tests, and linting.
- Preserve the current SHA-256 digest of every raw CSV.

---

### Task 1: Repository configuration and tracked directory boundaries

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `data/interim/.gitkeep`
- Create: `data/processed/.gitkeep`
- Create: `src/.gitkeep`
- Create: `sql/.gitkeep`
- Create: `reports/.gitkeep`

**Interfaces:**
- Consumes: the independent Git repository and Python 3.9.6 available on the host
- Produces: install metadata for package `ecommerce_product_analytics` and stable tracked output directories

- [x] **Step 1: Add repository ignore rules**

Create `.gitignore` with rules for `.venv`, Python caches, test and lint caches, notebook checkpoints, operating-system files, generated contents of `data/raw`, `data/interim`, `data/processed`, and `reports`, while retaining each directory's `.gitkeep` marker.

- [x] **Step 2: Add Python project metadata**

Create `pyproject.toml` with `requires-python = ">=3.9"`, pandas as the sole runtime dependency, and a `dev` optional dependency group containing JupyterLab, ipykernel, pytest, and Ruff. Configure setuptools for `src/`, pytest for `tests/`, and Ruff for Python 3.9.

- [x] **Step 3: Add output-directory markers**

Create zero-byte `.gitkeep` files in `data/interim`, `data/processed`, `src`, `sql`, and `reports`. The `src` marker allows the initial editable distribution install before the test-first package directory is added.

- [x] **Step 4: Create and install the environment**

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

Expected: every command exits with status 0 and the editable project is installed into `.venv`.

### Task 2: Test-first package skeleton and raw-data safeguard

**Files:**
- Create: `tests/test_environment.py`
- Create: `tests/test_raw_data_integrity.py`
- Create: `src/ecommerce_product_analytics/__init__.py`
- Create: `data/raw_checksums.sha256`

**Interfaces:**
- Consumes: editable package name `ecommerce_product_analytics`, repository root derived from `Path(__file__).parents[1]`, and the nine inspected raw CSV files
- Produces: importable package constant `__version__: str` and reproducible raw-file integrity verification

- [x] **Step 1: Write the failing package smoke test**

Create `tests/test_environment.py`:

```python
import pandas as pd

import ecommerce_product_analytics


def test_project_package_and_pandas_are_importable() -> None:
    assert ecommerce_product_analytics.__version__ == "0.1.0"
    assert int(pd.__version__.split(".")[0]) >= 2
```

- [x] **Step 2: Run the smoke test and confirm the expected failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_environment.py -q
```

Expected: collection fails because `ecommerce_product_analytics` does not yet exist.

- [x] **Step 3: Add the minimal importable package**

Create `src/ecommerce_product_analytics/__init__.py`:

```python
"""Reusable code for the e-commerce product analytics project."""

__version__ = "0.1.0"
```

- [x] **Step 4: Reinstall and verify the smoke test turns green**

Run:

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests/test_environment.py -q
```

Expected: one test passes.

- [x] **Step 5: Record the inspected raw-file checksums**

Create `data/raw_checksums.sha256` with the nine SHA-256 digests collected before implementation, one digest and repository-relative path per line.

- [x] **Step 6: Add a raw-data integrity test**

Create `tests/test_raw_data_integrity.py` that parses `data/raw_checksums.sha256`, asserts the exact current `*.csv` filename set in `data/raw/`, and compares each file's streamed SHA-256 digest with the manifest.

- [x] **Step 7: Run both safeguards**

Run:

```bash
.venv/bin/python -m pytest tests/test_environment.py tests/test_raw_data_integrity.py -q
```

Expected: two tests pass and no raw file is written.

### Task 3: Stage documentation and notebooks

**Files:**
- Create: `docs/data_dictionary.md`
- Create: `docs/analysis_plan.md`
- Create: `docs/decision_log.md`
- Create: `docs/assumptions.md`
- Create: `notebooks/00_data_audit.ipynb`
- Create: `notebooks/01_exploratory_analysis.ipynb`

**Interfaces:**
- Consumes: stage order and ownership rules in `AGENTS.md` and `PROJECT_BRIEF.md`
- Produces: empty, stage-scoped documentation and valid notebook containers without analytical results

- [x] **Step 1: Create required documentation shells**

Each Markdown file contains its title and one sentence stating when it will be populated. `decision_log.md` states that decisions must retain the user's reasoning; the other files contain no decisions, assumptions, dataset definitions, or metrics.

- [x] **Step 2: Create the data-audit notebook shell**

Create a valid notebook with one Markdown cell describing schema inspection, data-quality checks, and reproducible code boundaries. Include no executable cells and no findings.

- [x] **Step 3: Create the exploratory-analysis notebook shell**

Create a valid notebook with one Markdown cell stating that exploratory work starts only after the audit and relevant user decisions. Include no executable cells and no findings.

- [x] **Step 4: Validate notebook JSON and absence of outputs**

Run a Python standard-library script that loads both files with `json`, verifies `nbformat == 4`, and asserts every cell has no `outputs` field or an empty `outputs` list.

Expected: the script prints both notebook paths and exits with status 0.

### Task 4: Full verification and repository review

**Files:**
- Modify only if verification exposes a defect in a file created by Tasks 1–3

**Interfaces:**
- Consumes: all infrastructure created by Tasks 1–3
- Produces: fresh evidence that installation, tests, linting, notebook validity, raw integrity, and repository scope are correct

- [x] **Step 1: Run the full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: two tests pass.

- [x] **Step 2: Run static checks**

Run:

```bash
.venv/bin/python -m ruff check src tests
```

Expected: exit status 0 with no lint errors.

- [x] **Step 3: Verify raw files against the pre-implementation checksums**

Run:

```bash
shasum -a 256 -c data/raw_checksums.sha256
```

Expected: all nine CSV paths report `OK`.

- [x] **Step 4: Inspect the final tracked and ignored state**

Run `git status --short --ignored`, confirm `.venv`, `.DS_Store`, and raw CSV files are ignored, and confirm all intended project files are visible for tracking.

- [x] **Step 5: Print the resulting project tree**

Run a sorted `find` command that excludes `.git`, `.venv`, Python caches, and notebook checkpoints while retaining the raw CSV filenames.

Expected: output shows the complete project structure without environment noise.
