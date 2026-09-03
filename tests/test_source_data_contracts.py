from pathlib import Path

import pandas as pd
import pytest

from ecommerce_product_analytics.data_audit import (
    DATE_COLUMNS,
    EXPECTED_COLUMNS,
    build_journey_coverage,
    build_quality_findings,
    load_tables,
    profile_keys,
    profile_relationships,
)

RAW_DATA_DIR = Path(__file__).parents[1] / "data" / "raw"


@pytest.fixture(scope="module")
def source_tables() -> dict[str, pd.DataFrame]:
    return load_tables(RAW_DATA_DIR)


def test_source_schemas_match_the_audited_contract(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    assert {
        table: tuple(frame.columns) for table, frame in source_tables.items()
    } == EXPECTED_COLUMNS


def test_accepted_candidate_keys_are_complete_and_unique(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    result = profile_keys(source_tables)

    assert len(result) == 8
    assert result["null_key_rows"].eq(0).all()
    assert result["duplicate_key_rows"].eq(0).all()
    assert result["is_candidate_key"].all()


def test_strict_entity_relationships_have_no_orphans(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    result = profile_relationships(source_tables)
    strict = result.loc[result["strict"]]

    assert len(strict) == 6
    assert strict["child_null_rows"].eq(0).all()
    assert strict["orphan_rows"].eq(0).all()


def test_bounded_source_domains_remain_valid(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    assert set(source_tables["orders"]["order_status"]) == {
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
    }
    assert source_tables["order_reviews"]["review_score"].between(1, 5).all()
    assert source_tables["order_items"]["price"].gt(0).all()
    assert source_tables["order_items"]["freight_value"].ge(0).all()
    assert source_tables["order_payments"]["payment_value"].ge(0).all()


def test_configured_dates_are_parsed_as_datetimes(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    for table, columns in DATE_COLUMNS.items():
        for column in columns:
            assert pd.api.types.is_datetime64_any_dtype(
                source_tables[table][column]
            )


def test_postal_prefixes_preserve_leading_zeroes(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    assert source_tables["customers"]["customer_zip_code_prefix"].str.len().eq(5).all()
    assert (
        source_tables["geolocation"]["geolocation_zip_code_prefix"]
        .str.len()
        .eq(5)
        .all()
    )
    assert source_tables["sellers"]["seller_zip_code_prefix"].str.len().eq(5).all()


def test_journey_coverage_matches_the_audited_snapshot(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    result = build_journey_coverage(source_tables).set_index("metric")["value"]

    assert result.to_dict() == {
        "orders": 99441,
        "orders_with_items": 98666,
        "orders_with_payments": 99440,
        "orders_with_reviews": 98673,
        "unique_customer_identifiers": 96096,
        "repeat_customer_identifiers": 2997,
        "orders_with_multiple_items": 9803,
        "orders_with_multiple_payment_rows": 2961,
        "orders_with_multiple_review_rows": 547,
    }


def test_known_quality_findings_remain_visible(
    source_tables: dict[str, pd.DataFrame],
) -> None:
    result = build_quality_findings(source_tables).set_index("check")["count"]

    assert result["geolocation_exact_duplicate_rows"] == 261831
    assert result["review_id_duplicate_rows"] == 814
    assert result["products_without_category_translation_rows"] == 13
    assert result["customer_rows_without_geolocation_zip"] == 278
    assert result["carrier_timestamp_before_purchase_rows"] == 166
    assert result["shipping_limit_after_2018_rows"] == 4
