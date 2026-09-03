# Project Infrastructure Design

## Purpose

Create a minimal, reproducible foundation for an end-to-end product analytics portfolio project without starting the business analysis or choosing metrics, hypotheses, or recommendations.

## Repository boundary

The project is an independent Git repository rooted at `/Users/egor/Documents/ecommerce-product-analytics`. This prevents unrelated files from the parent `Documents` directory from entering project history.

## Python environment

The project uses a standard `pyproject.toml` and a local `.venv`. Installation must work through the Python standard-library workflow:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

The runtime dependencies are limited to packages needed for the initial data audit and notebook workflow. Development dependencies cover tests, linting, and notebook execution. Statistical, dashboard, database, and orchestration packages are deferred until an approved analytical requirement needs them.

## Project layout

- `data/raw/` stores immutable source CSV files and is never modified.
- `data/interim/` stores reproducible intermediate datasets.
- `data/processed/` stores reproducible analysis-ready datasets.
- `notebooks/` starts with a data-audit notebook and an exploratory-analysis notebook. Both contain structure and instructions only; they do not perform business analysis.
- `src/ecommerce_product_analytics/` is the importable Python package for reusable analytical logic when such logic is introduced.
- `tests/` contains environment, package-import, and raw-data integrity checks.
- `sql/` will contain meaningful saved SQL queries once analytical questions have been approved.
- `docs/` contains the required data dictionary, analysis plan, decision log, and assumptions register.
- `reports/` will contain finalized outputs and interview notes when the project reaches those stages.

Empty output directories are retained with `.gitkeep` files. They contain no invented results or decisions.

## Raw-data safeguards

The nine existing CSV files remain byte-for-byte unchanged. Their current SHA-256 checksums are recorded in a manifest outside `data/raw/`. A test verifies the filename set and checksums so accidental edits, deletion, or additions are visible.

The audit notebook will later read raw data and write derived artifacts only to `data/interim/` or `data/processed/`.

## Documentation

The required documentation files begin with titles and scope notes only. No dataset description, business problem, metric definition, finding, assumption, or decision is invented during setup.

## Initial notebooks

`00_data_audit.ipynb` identifies the technical audit stage and points reusable logic toward `src/`. `01_exploratory_analysis.ipynb` explicitly states that work begins only after the audit and relevant user decisions. Both notebooks use the project virtual environment kernel metadata.

## Testing and verification

Verification covers:

1. editable installation of the local package;
2. import of the package and declared runtime dependencies;
3. raw-file filename and SHA-256 integrity;
4. test execution with `pytest`;
5. static checks with Ruff;
6. notebook JSON validity and a no-output execution smoke test where applicable.

## Explicitly deferred scope

The setup does not select a business problem, define metrics, profile or transform the dataset, interpret patterns, write analytical SQL, perform statistical tests, build a dashboard, or create recommendations.
