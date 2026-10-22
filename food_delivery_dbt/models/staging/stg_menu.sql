{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(SOURCE_INDEX), '') AS source_index,
    NULLIF(TRIM(MENU_ID), '') AS menu_id,
    NULLIF(TRIM(R_ID), '') AS restaurant_id,
    NULLIF(TRIM(F_ID), '') AS food_id,
    NULLIF(TRIM(CUISINE), '') AS cuisine,
    TRY_TO_DECIMAL(NULLIF(TRIM(PRICE), ''), 10, 2) AS price
FROM {{ source('raw', 'raw_menu') }}