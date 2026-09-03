"""Reusable technical-audit helpers for the immutable source CSV files."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": (
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ),
    "geolocation": (
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ),
    "order_items": (
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ),
    "order_payments": (
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ),
    "order_reviews": (
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ),
    "orders": (
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
    "products": (
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ),
    "sellers": (
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ),
    "category_translation": (
        "product_category_name",
        "product_category_name_english",
    ),
}

TABLE_FILES: dict[str, str] = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

DATE_COLUMNS: dict[str, tuple[str, ...]] = {
    "order_items": ("shipping_limit_date",),
    "order_reviews": ("review_creation_date", "review_answer_timestamp"),
    "orders": (
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
}

STRING_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": ("customer_zip_code_prefix",),
    "geolocation": ("geolocation_zip_code_prefix",),
    "sellers": ("seller_zip_code_prefix",),
}


@dataclass(frozen=True)
class KeyCandidate:
    """Columns whose non-null uniqueness is evaluated as a candidate key."""

    table: str
    columns: tuple[str, ...]
    label: str


@dataclass(frozen=True)
class Relationship:
    """A child-to-parent relationship evaluated for lookup coverage."""

    label: str
    child_table: str
    child_column: str
    parent_table: str
    parent_column: str
    strict: bool


KEY_CANDIDATES: tuple[KeyCandidate, ...] = (
    KeyCandidate("customers", ("customer_id",), "customers.customer_id"),
    KeyCandidate(
        "order_items",
        ("order_id", "order_item_id"),
        "order_items.(order_id, order_item_id)",
    ),
    KeyCandidate(
        "order_payments",
        ("order_id", "payment_sequential"),
        "order_payments.(order_id, payment_sequential)",
    ),
    KeyCandidate(
        "order_reviews",
        ("review_id", "order_id"),
        "order_reviews.(review_id, order_id)",
    ),
    KeyCandidate("orders", ("order_id",), "orders.order_id"),
    KeyCandidate("products", ("product_id",), "products.product_id"),
    KeyCandidate("sellers", ("seller_id",), "sellers.seller_id"),
    KeyCandidate(
        "category_translation",
        ("product_category_name",),
        "category_translation.product_category_name",
    ),
)

RELATIONSHIPS: tuple[Relationship, ...] = (
    Relationship(
        "orders.customer_id → customers.customer_id",
        "orders",
        "customer_id",
        "customers",
        "customer_id",
        True,
    ),
    Relationship(
        "order_items.order_id → orders.order_id",
        "order_items",
        "order_id",
        "orders",
        "order_id",
        True,
    ),
    Relationship(
        "order_payments.order_id → orders.order_id",
        "order_payments",
        "order_id",
        "orders",
        "order_id",
        True,
    ),
    Relationship(
        "order_reviews.order_id → orders.order_id",
        "order_reviews",
        "order_id",
        "orders",
        "order_id",
        True,
    ),
    Relationship(
        "order_items.product_id → products.product_id",
        "order_items",
        "product_id",
        "products",
        "product_id",
        True,
    ),
    Relationship(
        "order_items.seller_id → sellers.seller_id",
        "order_items",
        "seller_id",
        "sellers",
        "seller_id",
        True,
    ),
    Relationship(
        "products.category → category_translation.category",
        "products",
        "product_category_name",
        "category_translation",
        "product_category_name",
        False,
    ),
    Relationship(
        "customers.zip_prefix → geolocation.zip_prefix",
        "customers",
        "customer_zip_code_prefix",
        "geolocation",
        "geolocation_zip_code_prefix",
        False,
    ),
    Relationship(
        "sellers.zip_prefix → geolocation.zip_prefix",
        "sellers",
        "seller_zip_code_prefix",
        "geolocation",
        "geolocation_zip_code_prefix",
        False,
    ),
)


def load_tables(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all expected source tables without modifying the source files."""
    tables: dict[str, pd.DataFrame] = {}
    for table, filename in TABLE_FILES.items():
        dtype = {column: "string" for column in STRING_COLUMNS.get(table, ())}
        frame = pd.read_csv(raw_dir / filename, dtype=dtype, encoding="utf-8-sig")
        if tuple(frame.columns) != EXPECTED_COLUMNS[table]:
            raise ValueError(f"Unexpected columns in {filename}: {tuple(frame.columns)}")
        for column in DATE_COLUMNS.get(table, ()):
            frame[column] = pd.to_datetime(frame[column], errors="raise")
        tables[table] = frame
    return tables


def profile_tables(tables: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize table size, exact duplicate rows, and missing cells."""
    rows = []
    for table, frame in tables.items():
        rows.append(
            {
                "table": table,
                "rows": len(frame),
                "columns": len(frame.columns),
                "exact_duplicate_rows": int(frame.duplicated().sum()),
                "missing_cells": int(frame.isna().sum().sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("table").reset_index(drop=True)


def profile_columns(tables: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize types, completeness, cardinality, and bounded ranges."""
    rows = []
    for table, frame in tables.items():
        for column in frame.columns:
            series = frame[column]
            is_datetime = isinstance(series.dtype, pd.DatetimeTZDtype) or (
                pd.api.types.is_datetime64_any_dtype(series)
            )
            is_numeric = pd.api.types.is_numeric_dtype(series)
            non_null = series.dropna()
            rows.append(
                {
                    "table": table,
                    "column": column,
                    "dtype": str(series.dtype),
                    "missing_count": int(series.isna().sum()),
                    "missing_pct": float(series.isna().mean()),
                    "unique_non_null": int(series.nunique(dropna=True)),
                    "minimum": non_null.min()
                    if len(non_null) and (is_datetime or is_numeric)
                    else None,
                    "median": non_null.median()
                    if len(non_null) and (is_datetime or is_numeric)
                    else None,
                    "maximum": non_null.max()
                    if len(non_null) and (is_datetime or is_numeric)
                    else None,
                }
            )
    return pd.DataFrame(rows)


def profile_keys(
    tables: Mapping[str, pd.DataFrame],
    candidates: Sequence[KeyCandidate] = KEY_CANDIDATES,
) -> pd.DataFrame:
    """Evaluate configured columns as non-null candidate keys."""
    rows = []
    for candidate in candidates:
        frame = tables[candidate.table]
        columns = list(candidate.columns)
        null_rows = int(frame[columns].isna().any(axis=1).sum())
        duplicate_rows = int(frame.duplicated(columns).sum())
        rows.append(
            {
                "table": candidate.table,
                "key": candidate.label,
                "columns": ", ".join(candidate.columns),
                "null_key_rows": null_rows,
                "duplicate_key_rows": duplicate_rows,
                "is_candidate_key": null_rows == 0 and duplicate_rows == 0,
            }
        )
    return pd.DataFrame(rows)


def profile_relationships(
    tables: Mapping[str, pd.DataFrame],
    relationships: Sequence[Relationship] = RELATIONSHIPS,
) -> pd.DataFrame:
    """Measure referential or lookup coverage for configured relationships."""
    rows = []
    for relationship in relationships:
        child = tables[relationship.child_table][relationship.child_column]
        parent = tables[relationship.parent_table][relationship.parent_column]
        child_non_null = child.dropna()
        orphan_mask = ~child_non_null.isin(parent.dropna().unique())
        rows.append(
            {
                "relationship": relationship.label,
                "strict": relationship.strict,
                "child_rows": len(child),
                "child_null_rows": int(child.isna().sum()),
                "orphan_rows": int(orphan_mask.sum()),
                "orphan_distinct_values": int(
                    child_non_null.loc[orphan_mask].nunique()
                ),
            }
        )
    return pd.DataFrame(rows)


def value_distribution(table: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return a complete categorical distribution, including missing values."""
    result = (
        table[column]
        .value_counts(dropna=False)
        .rename_axis("value")
        .reset_index(name="count")
    )
    result["pct"] = result["count"] / len(table)
    return result


def build_journey_coverage(
    tables: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Summarize which order-journey components are observable."""
    orders = tables["orders"]
    customers = tables["customers"]
    customer_order_counts = customers["customer_unique_id"].value_counts()
    metrics = [
        ("orders", len(orders)),
        (
            "orders_with_items",
            int(orders["order_id"].isin(tables["order_items"]["order_id"]).sum()),
        ),
        (
            "orders_with_payments",
            int(
                orders["order_id"]
                .isin(tables["order_payments"]["order_id"])
                .sum()
            ),
        ),
        (
            "orders_with_reviews",
            int(
                orders["order_id"].isin(tables["order_reviews"]["order_id"]).sum()
            ),
        ),
        ("unique_customer_identifiers", customers["customer_unique_id"].nunique()),
        ("repeat_customer_identifiers", int((customer_order_counts > 1).sum())),
        (
            "orders_with_multiple_items",
            int((tables["order_items"]["order_id"].value_counts() > 1).sum()),
        ),
        (
            "orders_with_multiple_payment_rows",
            int((tables["order_payments"]["order_id"].value_counts() > 1).sum()),
        ),
        (
            "orders_with_multiple_review_rows",
            int((tables["order_reviews"]["order_id"].value_counts() > 1).sum()),
        ),
    ]
    return pd.DataFrame(metrics, columns=["metric", "value"])


def build_quality_findings(
    tables: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Count bounded, pre-defined data-quality observations."""
    customers = tables["customers"]
    geolocation = tables["geolocation"]
    items = tables["order_items"]
    payments = tables["order_payments"]
    reviews = tables["order_reviews"]
    orders = tables["orders"]
    products = tables["products"]
    sellers = tables["sellers"]
    translation = tables["category_translation"]

    item_orders = items.merge(
        orders[["order_id", "order_purchase_timestamp"]],
        on="order_id",
        how="left",
        validate="many_to_one",
    )
    item_totals = (
        items.assign(item_total=items["price"] + items["freight_value"])
        .groupby("order_id")["item_total"]
        .sum()
    )
    payment_totals = payments.groupby("order_id")["payment_value"].sum()
    amount_comparison = pd.concat(
        [item_totals.rename("item_total"), payment_totals.rename("payment_total")],
        axis=1,
    ).dropna()

    product_catalog_fields = [
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
    ]
    product_physical_fields = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    geo_bbox_outlier = ~geolocation["geolocation_lat"].between(-34, -5) | (
        ~geolocation["geolocation_lng"].between(-74, -34)
    )

    findings = [
        (
            "geolocation_exact_duplicate_rows",
            int(geolocation.duplicated().sum()),
            "Exact duplicates; geolocation is not a unique ZIP dimension.",
        ),
        (
            "review_id_duplicate_rows",
            int(reviews.duplicated(["review_id"]).sum()),
            "review_id alone is not unique.",
        ),
        (
            "review_order_id_duplicate_rows",
            int(reviews.duplicated(["order_id"]).sum()),
            "Some orders have more than one review row.",
        ),
        (
            "products_missing_catalog_metadata_rows",
            int(products[product_catalog_fields].isna().all(axis=1).sum()),
            "Category, name length, description length, and photo count all missing.",
        ),
        (
            "products_missing_physical_metadata_rows",
            int(products[product_physical_fields].isna().all(axis=1).sum()),
            "All weight and dimension fields missing.",
        ),
        (
            "products_zero_weight_rows",
            int(products["product_weight_g"].eq(0).sum()),
            "Zero weight is suspicious but not overwritten.",
        ),
        (
            "products_without_category_translation_rows",
            int(
                (
                    products["product_category_name"].notna()
                    & ~products["product_category_name"].isin(
                        translation["product_category_name"]
                    )
                ).sum()
            ),
            "Two Portuguese category values have no English lookup.",
        ),
        (
            "customer_rows_without_geolocation_zip",
            int(
                (~customers["customer_zip_code_prefix"].isin(
                    geolocation["geolocation_zip_code_prefix"]
                )).sum()
            ),
            "Postal lookup coverage gap; not a strict entity foreign key.",
        ),
        (
            "seller_rows_without_geolocation_zip",
            int(
                (~sellers["seller_zip_code_prefix"].isin(
                    geolocation["geolocation_zip_code_prefix"]
                )).sum()
            ),
            "Postal lookup coverage gap; not a strict entity foreign key.",
        ),
        (
            "zero_value_payment_rows",
            int(payments["payment_value"].eq(0).sum()),
            "Includes vouchers and undefined payment types.",
        ),
        (
            "zero_installment_payment_rows",
            int(payments["payment_installments"].eq(0).sum()),
            "Two credit-card rows report zero installments.",
        ),
        (
            "undefined_payment_type_rows",
            int(payments["payment_type"].eq("not_defined").sum()),
            "Payment method is not defined.",
        ),
        (
            "carrier_timestamp_before_purchase_rows",
            int(
                orders["order_delivered_carrier_date"]
                .lt(orders["order_purchase_timestamp"])
                .sum()
            ),
            "Chronology violation in the order lifecycle.",
        ),
        (
            "customer_delivery_before_carrier_rows",
            int(
                orders["order_delivered_customer_date"]
                .lt(orders["order_delivered_carrier_date"])
                .sum()
            ),
            "Chronology violation in the order lifecycle.",
        ),
        (
            "shipping_limit_after_2018_rows",
            int(items["shipping_limit_date"].gt("2018-12-31").sum()),
            "Four rows have 2020 deadlines while purchases occurred in 2017.",
        ),
        (
            "shipping_limit_before_purchase_rows",
            int(
                item_orders["shipping_limit_date"]
                .lt(item_orders["order_purchase_timestamp"])
                .sum()
            ),
            "Expected chronology check.",
        ),
        (
            "delivery_after_estimate_rows",
            int(
                orders["order_delivered_customer_date"]
                .gt(orders["order_estimated_delivery_date"])
                .sum()
            ),
            "Observed late delivery, not necessarily a data error.",
        ),
        (
            "geolocation_rows_outside_brazil_bbox",
            int(geo_bbox_outlier.sum()),
            "Heuristic bounding-box flag; requires geospatial validation.",
        ),
        (
            "matched_orders_with_amount_difference_gt_0_01",
            int(
                (
                    amount_comparison["payment_total"]
                    - amount_comparison["item_total"]
                )
                .abs()
                .gt(0.01)
                .sum()
            ),
            "May reflect adjustments absent from the item table.",
        ),
    ]
    return pd.DataFrame(findings, columns=["check", "count", "note"])


__all__ = [
    "DATE_COLUMNS",
    "EXPECTED_COLUMNS",
    "KEY_CANDIDATES",
    "RELATIONSHIPS",
    "STRING_COLUMNS",
    "TABLE_FILES",
    "KeyCandidate",
    "Relationship",
    "build_journey_coverage",
    "build_quality_findings",
    "load_tables",
    "profile_columns",
    "profile_keys",
    "profile_relationships",
    "profile_tables",
    "value_distribution",
]
