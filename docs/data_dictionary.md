# Data Dictionary

## Audit scope

Technical audit completed on 2026-09-03 against all nine CSV files in `data/raw/`. The files contain 1,550,922 rows in total. All findings are reproducible through `notebooks/01_data_audit.ipynb` and `src/ecommerce_product_analytics/data_audit.py`.

The repository does not yet contain a dataset title, source URL, extraction method, timezone, currency definition, or upstream schema documentation. Entity and column descriptions below are therefore technical inferences from names, values, and observed relationships, not externally verified business definitions.

Conventions:

- Source files are immutable and protected by `data/raw_checksums.sha256`.
- Timestamps parse without errors but are timezone-naive.
- ZIP-code prefixes are categorical identifiers and must be loaded as five-character strings; integer inference removes leading zeroes.
- Source spellings `product_name_lenght` and `product_description_lenght` are retained for compatibility.
- Missing values are not automatically errors. Their meaning depends on order state and source-system behavior.

## Table overview

| Table | File | Rows | Columns | Candidate key | Exact duplicate rows | Missing cells |
|---|---|---:|---:|---|---:|---:|
| `customers` | `olist_customers_dataset.csv` | 99,441 | 5 | `customer_id` | 0 | 0 |
| `geolocation` | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | None in the raw table | 261,831 | 0 |
| `order_items` | `olist_order_items_dataset.csv` | 112,650 | 7 | (`order_id`, `order_item_id`) | 0 | 0 |
| `order_payments` | `olist_order_payments_dataset.csv` | 103,886 | 5 | (`order_id`, `payment_sequential`) | 0 | 0 |
| `order_reviews` | `olist_order_reviews_dataset.csv` | 99,224 | 7 | (`review_id`, `order_id`) | 0 | 145,903 |
| `orders` | `olist_orders_dataset.csv` | 99,441 | 8 | `order_id` | 0 | 4,908 |
| `products` | `olist_products_dataset.csv` | 32,951 | 9 | `product_id` | 0 | 2,448 |
| `sellers` | `olist_sellers_dataset.csv` | 3,095 | 4 | `seller_id` | 0 | 0 |
| `category_translation` | `product_category_name_translation.csv` | 71 | 2 | `product_category_name` | 0 | 0 |

## Entities and grain

### `customers`

Grain: one order-specific customer record. `customer_id` is unique and joins one-to-one to `orders.customer_id`. It must not be treated as a stable person identifier. `customer_unique_id` is the available repeat-customer identifier: 96,096 distinct values exist, and 2,997 appear in more than one customer/order row (maximum 17 rows).

| Column | Audit type | Missing | Distinct | Technical meaning |
|---|---|---:|---:|---|
| `customer_id` | text | 0 | 99,441 | Order-level customer key; unique in this table. |
| `customer_unique_id` | text | 0 | 96,096 | Cross-order customer identifier; not unique. |
| `customer_zip_code_prefix` | five-character string | 0 | 14,994 | Customer postal-code prefix. |
| `customer_city` | text | 0 | 4,119 | Customer city label. |
| `customer_state` | text | 0 | 27 | Customer state code. |

### `orders`

Grain: one order. It contains the observable order lifecycle from purchase through approval, carrier handoff, delivery, and estimated delivery.

| Column | Audit type | Missing | Distinct | Technical meaning |
|---|---|---:|---:|---|
| `order_id` | text | 0 | 99,441 | Unique order key. |
| `customer_id` | text | 0 | 99,441 | Order-specific customer key; complete match to `customers`. |
| `order_status` | text | 0 | 8 | Current/final recorded order state. |
| `order_purchase_timestamp` | datetime | 0 | 98,875 | Purchase timestamp. |
| `order_approved_at` | datetime | 160 (0.16%) | 90,733 | Approval timestamp. |
| `order_delivered_carrier_date` | datetime | 1,783 (1.79%) | 81,018 | Recorded carrier-handoff timestamp. |
| `order_delivered_customer_date` | datetime | 2,965 (2.98%) | 95,664 | Recorded customer-delivery timestamp. |
| `order_estimated_delivery_date` | datetime | 0 | 459 | Estimated delivery date. |

Status distribution: `delivered` 96,478; `shipped` 1,107; `canceled` 625; `unavailable` 609; `invoiced` 314; `processing` 301; `created` 5; `approved` 2.

### `order_items`

Grain: one numbered item row within an order. There are 98,666 represented orders; 9,803 have multiple item rows and the maximum recorded `order_item_id` is 21.

| Column | Audit type | Missing | Distinct / range | Technical meaning |
|---|---|---:|---|---|
| `order_id` | text | 0 | 98,666 | Parent order key. |
| `order_item_id` | integer | 0 | 1–21 | Item sequence within an order. |
| `product_id` | text | 0 | 32,951 | Product key; complete match to `products`. |
| `seller_id` | text | 0 | 3,095 | Seller key; complete match to `sellers`. |
| `shipping_limit_date` | datetime | 0 | 2016-09-19 to 2020-04-09 | Recorded seller shipping deadline. |
| `price` | decimal | 0 | 0.85–6,735.00 | Item price in an undocumented currency. |
| `freight_value` | decimal | 0 | 0.00–409.68 | Item-level freight amount in an undocumented currency. |

### `order_payments`

Grain: one sequential payment row within an order. There are 99,440 represented orders; 2,961 have multiple payment rows and the maximum sequence is 29.

| Column | Audit type | Missing | Distinct / range | Technical meaning |
|---|---|---:|---|---|
| `order_id` | text | 0 | 99,440 | Parent order key. |
| `payment_sequential` | integer | 0 | 1–29 | Payment sequence within an order. |
| `payment_type` | text | 0 | 5 | Recorded payment method. |
| `payment_installments` | integer | 0 | 0–24 | Number of installments; two rows contain zero. |
| `payment_value` | decimal | 0 | 0.00–13,664.08 | Payment-row amount in an undocumented currency. |

Payment types: `credit_card` 76,795; `boleto` 19,784; `voucher` 5,775; `debit_card` 1,529; `not_defined` 3.

### `order_reviews`

Grain: one review/order association. Neither `review_id` nor `order_id` is independently unique; (`review_id`, `order_id`) is unique. There are 814 repeated `review_id` rows and 551 repeated `order_id` rows. Consequently, joins that assume one review per order can duplicate orders.

| Column | Audit type | Missing | Distinct | Technical meaning |
|---|---|---:|---:|---|
| `review_id` | text | 0 | 98,410 | Review identifier; not unique in this extract. |
| `order_id` | text | 0 | 98,673 | Parent order key; not unique in this table. |
| `review_score` | integer | 0 | 5 | Score bounded to 1–5. |
| `review_comment_title` | text | 87,656 (88.34%) | 4,527 | Optional review title. |
| `review_comment_message` | text | 58,247 (58.70%) | 36,159 | Optional review body. |
| `review_creation_date` | datetime | 0 | 636 | Review creation date. |
| `review_answer_timestamp` | datetime | 0 | 98,248 | Review answer timestamp. |

Score distribution: 5 → 57,328; 4 → 19,142; 3 → 8,179; 2 → 3,151; 1 → 11,424.

### `products`

Grain: one product. Product name and description text are not present; only their recorded lengths are available.

| Column | Audit type | Missing | Distinct / range | Technical meaning |
|---|---|---:|---|---|
| `product_id` | text | 0 | 32,951 | Unique product key. |
| `product_category_name` | text | 610 (1.85%) | 73 | Portuguese category key. |
| `product_name_lenght` | decimal/integer-like | 610 (1.85%) | 5–76 | Recorded product-name length. |
| `product_description_lenght` | decimal/integer-like | 610 (1.85%) | 4–3,992 | Recorded description length. |
| `product_photos_qty` | decimal/integer-like | 610 (1.85%) | 1–20 | Recorded photo count. |
| `product_weight_g` | decimal | 2 (0.01%) | 0–40,425 | Product weight in grams; four non-null rows are zero. |
| `product_length_cm` | decimal | 2 (0.01%) | 7–105 | Product length in centimetres. |
| `product_height_cm` | decimal | 2 (0.01%) | 2–105 | Product height in centimetres. |
| `product_width_cm` | decimal | 2 (0.01%) | 6–118 | Product width in centimetres. |

The 610 missing catalog rows lack category, name length, description length, and photo count together. Two other products lack all four physical measurements together.

### `sellers`

Grain: one seller.

| Column | Audit type | Missing | Distinct | Technical meaning |
|---|---|---:|---:|---|
| `seller_id` | text | 0 | 3,095 | Unique seller key. |
| `seller_zip_code_prefix` | five-character string | 0 | 2,246 | Seller postal-code prefix. |
| `seller_city` | text | 0 | 611 | Seller city label. |
| `seller_state` | text | 0 | 23 | Seller state code. |

### `geolocation`

Grain: a raw geolocation observation for a postal prefix, not a unique postal-code dimension. The table has 261,831 exact duplicate rows. One prefix may map to multiple coordinates and city spellings; 8,556 prefixes have multiple city labels and 8 prefixes have multiple state labels.

| Column | Audit type | Missing | Distinct / range | Technical meaning |
|---|---|---:|---|---|
| `geolocation_zip_code_prefix` | five-character string | 0 | 19,015 | Postal-code prefix; highly non-unique. |
| `geolocation_lat` | decimal | 0 | −36.605 to 45.066 | Latitude observation. |
| `geolocation_lng` | decimal | 0 | −101.467 to 121.105 | Longitude observation. |
| `geolocation_city` | text | 0 | 8,011 | City label associated with an observation. |
| `geolocation_state` | text | 0 | 27 | State code associated with an observation. |

Any one-row-per-prefix table must be derived using an explicit aggregation/deduplication rule. The audit's broad Brazil bounding-box heuristic flags 29,038 rows; this is a review flag, not proof that every coordinate is invalid.

### `category_translation`

Grain: one Portuguese-to-English category mapping. Both columns are complete and independently unique.

| Column | Audit type | Missing | Distinct | Technical meaning |
|---|---|---:|---:|---|
| `product_category_name` | text | 0 | 71 | Portuguese category key. |
| `product_category_name_english` | text | 0 | 71 | English category label. |

Thirteen product rows across two non-null categories lack a translation: `pc_gamer` (3 products) and `portateis_cozinha_e_preparadores_de_alimentos` (10 products).

## Relationship map

| Child → parent | Observed cardinality | Integrity result |
|---|---|---|
| `orders.customer_id` → `customers.customer_id` | one-to-one | 0 orphan rows |
| `customers.customer_unique_id` → conceptual customer | many order-specific IDs to one repeat-customer ID | 96,096 IDs; 2,997 repeat |
| `order_items.order_id` → `orders.order_id` | many-to-one | 0 orphans; 775 orders have no item row |
| `order_payments.order_id` → `orders.order_id` | many-to-one | 0 orphans; 1 order has no payment row |
| `order_reviews.order_id` → `orders.order_id` | many-to-one | 0 orphans; 768 orders have no review row |
| `order_items.product_id` → `products.product_id` | many-to-one | 0 orphan rows |
| `order_items.seller_id` → `sellers.seller_id` | many-to-one | 0 orphan rows |
| `products.product_category_name` → `category_translation.product_category_name` | optional many-to-one lookup | 610 null categories; 13 untranslated product rows across 2 values |
| customer ZIP → geolocation ZIP | non-strict lookup | 278 customer rows / 157 distinct prefixes uncovered |
| seller ZIP → geolocation ZIP | non-strict lookup | 7 seller rows / 7 distinct prefixes uncovered |

Joining geolocation directly to customers or sellers will multiply rows because postal prefixes are not unique. Joining reviews directly to orders may also multiply rows because 547 orders have multiple review rows.

## Date coverage and chronology

| Field | Minimum | Maximum | Missing |
|---|---|---|---:|
| Purchase timestamp | 2016-09-04 21:15:19 | 2018-10-17 17:30:18 | 0 |
| Approval timestamp | 2016-09-15 12:16:38 | 2018-09-03 17:40:06 | 160 |
| Carrier timestamp | 2016-10-08 10:34:01 | 2018-09-11 19:48:28 | 1,783 |
| Customer delivery timestamp | 2016-10-11 13:46:32 | 2018-10-17 13:22:46 | 2,965 |
| Estimated delivery date | 2016-09-30 | 2018-11-12 | 0 |
| Shipping limit | 2016-09-19 00:15:34 | 2020-04-09 22:35:08 | 0 |
| Review creation | 2016-10-02 | 2018-08-31 | 0 |
| Review answer | 2016-10-07 18:32:28 | 2018-10-29 12:27:35 | 0 |

The edges of the purchase period are sparse: 4 orders in September 2016, no orders in November 2016, 1 in December 2016, 16 in September 2018, and 4 in October 2018. Analyses using full boundary months would therefore have unequal observation coverage.

Chronology flags:

- 166 orders record carrier handoff before purchase; most differences are under roughly two hours, but one is about 171 days.
- 23 orders record customer delivery before carrier handoff.
- 4 item rows have shipping deadlines in 2020 although their orders were purchased in 2017.
- 7,827 rows record delivery after the estimated date; this can be a valid operational outcome rather than a data defect.
- No approval precedes purchase, no customer delivery precedes purchase, no estimate precedes purchase, no review answer precedes review creation, and no shipping deadline precedes purchase.

## Other quality observations

- Nine payment rows have value zero; three of these use `not_defined`, and the others include voucher rows.
- Two credit-card rows report zero installments.
- All item prices are positive; freight and payment values are non-negative.
- Four products have zero recorded weight, while all three dimensions are positive.
- For 378 orders with both item and payment data, summed payments differ from summed item price plus freight by more than 0.01. The extract has no adjustment/refund table that explains the difference.
- The order with no payment is recorded as delivered.
- The 775 orders without items are primarily `unavailable` (603) or `canceled` (164), with eight other incomplete-state rows.
- Reviews are absent for 768 orders, including 646 delivered orders.

## Potentially reconstructable journey

Within the observed purchase window, the following post-purchase sequence can potentially be reconstructed:

1. Repeat-customer identity through `customer_unique_id`.
2. Order placement through `order_purchase_timestamp`.
3. Approval through `order_approved_at`.
4. Purchased item, product category, seller, price, and freight composition.
5. Payment method, installment count, and one or more payment rows.
6. Seller shipping deadline and recorded carrier handoff.
7. Estimated and recorded customer delivery.
8. Review score, optional text, creation date, and answer timestamp.

Coverage is not complete at every step: 98,666 of 99,441 orders have items, 99,440 have payments, and 98,673 have reviews. Repeat behavior is observable only inside the dataset window and is subject to left and right censoring.

## Important information not present

- Website/app visits, sessions, impressions, searches, clicks, product-page views, favorites, carts, checkout starts, and abandonment.
- Acquisition source, campaign, marketing spend, attribution, referral, and traffic channel.
- Customer demographics, account creation, device, platform, consent, or reliable behavioral segmentation fields.
- Inventory levels, stock-out history, product availability, seller capacity, or promised-service rules.
- Product names, full descriptions, images, brand, list price, discounts, promotions, coupons, taxes, or currency metadata.
- Costs, margin, commissions, seller fees, recognized revenue, accounting status, or profitability.
- Shipment carrier identity, tracking events, route, service level, or reason for operational delay.
- Explicit return, refund, chargeback, replacement, support-contact, complaint, or cancellation-reason data.
- Experiment assignment, feature exposure, release markers, or other causal-intervention metadata.
- Verified dataset provenance, extraction logic, update cadence, timezone, and definitions supplied by the source owner.

## Product-question boundaries

The data can support descriptive or associational questions about:

- order lifecycle coverage and delivery timing;
- repeat ordering within the observation window;
- order/item composition, categories, sellers, geography, freight, and payments;
- review scores and their association with observed order, delivery, product, seller, or geographic attributes;
- cancellation/unavailability patterns present in the order table;
- data-informed hypotheses that are explicitly treated as non-causal.

The data cannot directly answer:

- visit-to-purchase conversion, funnel drop-off before order creation, or cart abandonment;
- why a customer did not buy, canceled, returned, complained, or churned;
- acquisition efficiency, campaign incrementality, or channel attribution;
- true revenue recognition, margin, profitability, customer lifetime value beyond the window, or refund-adjusted economics;
- inventory or recommendation-system performance;
- causal impact of a product change, seller action, delivery speed, payment method, or any other exposure without additional identification assumptions or experimental data.

No business problem or metric framework is selected by this audit.
