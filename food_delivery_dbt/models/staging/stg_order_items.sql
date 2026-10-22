{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(ORDER_ITEM_ID), '') AS order_item_id,
    NULLIF(TRIM(ORDER_ID), '') AS order_id,
    NULLIF(TRIM(R_ID), '') AS restaurant_id,
    NULLIF(TRIM(F_ID), '') AS food_id,
    TRY_TO_DECIMAL(NULLIF(TRIM(PRICE), ''), 10, 2) AS price,
    TRY_TO_NUMBER(NULLIF(TRIM(QUANTITY), '')) AS quantity,
    TRY_TO_DECIMAL(NULLIF(TRIM(LINE_AMOUNT), ''), 12, 2) AS line_amount
FROM {{ source('raw', 'raw_order_items') }}