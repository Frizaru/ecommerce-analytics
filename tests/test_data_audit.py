import pandas as pd

from ecommerce_product_analytics.data_audit import (
    KeyCandidate,
    Relationship,
    profile_columns,
    profile_keys,
    profile_relationships,
    profile_tables,
    value_distribution,
)


def test_profile_tables_counts_rows_columns_duplicates_and_missing_cells() -> None:
    tables = {
        "sample": pd.DataFrame(
            {"id": [1, 1, 2], "value": ["same", "same", None]}
        )
    }

    result = profile_tables(tables).set_index("table").loc["sample"]

    assert result.to_dict() == {
        "rows": 3,
        "columns": 2,
        "exact_duplicate_rows": 1,
        "missing_cells": 1,
    }


def test_profile_columns_reports_completeness_cardinality_and_numeric_range() -> None:
    tables = {
        "sample": pd.DataFrame({"amount": [1.0, None, 3.0], "label": ["a", "a", "b"]})
    }

    result = profile_columns(tables).set_index("column")

    assert result.loc["amount", "missing_count"] == 1
    assert result.loc["amount", "unique_non_null"] == 2
    assert result.loc["amount", "minimum"] == 1.0
    assert result.loc["amount", "median"] == 2.0
    assert result.loc["amount", "maximum"] == 3.0
    assert pd.isna(result.loc["label", "minimum"])


def test_profile_keys_distinguishes_repeated_single_and_unique_composite_keys() -> None:
    tables = {
        "items": pd.DataFrame(
            {"order_id": ["a", "a", "b"], "line_number": [1, 2, 1]}
        )
    }
    candidates = (
        KeyCandidate("items", ("order_id",), "order only"),
        KeyCandidate("items", ("order_id", "line_number"), "order line"),
    )

    result = profile_keys(tables, candidates).set_index("key")

    assert result.loc["order only", "duplicate_key_rows"] == 1
    assert not bool(result.loc["order only", "is_candidate_key"])
    assert result.loc["order line", "duplicate_key_rows"] == 0
    assert bool(result.loc["order line", "is_candidate_key"])


def test_profile_relationships_counts_orphans_without_treating_nulls_as_keys() -> None:
    tables = {
        "children": pd.DataFrame({"parent_id": [1, 2, 2, 3, None]}),
        "parents": pd.DataFrame({"id": [1, 2]}),
    }
    relationships = (
        Relationship(
            "child to parent",
            "children",
            "parent_id",
            "parents",
            "id",
            strict=True,
        ),
    )

    result = profile_relationships(tables, relationships).iloc[0]

    assert result["child_rows"] == 5
    assert result["child_null_rows"] == 1
    assert result["orphan_rows"] == 1
    assert result["orphan_distinct_values"] == 1


def test_value_distribution_keeps_missing_values_visible() -> None:
    table = pd.DataFrame({"status": ["done", "done", "open", None]})

    result = value_distribution(table, "status")

    assert result["count"].sum() == 4
    assert result.loc[result["value"].isna(), "count"].item() == 1
