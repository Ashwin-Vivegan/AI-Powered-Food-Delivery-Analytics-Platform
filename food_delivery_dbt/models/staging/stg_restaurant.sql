{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(SOURCE_INDEX), '') AS source_index,
    NULLIF(TRIM(ID), '') AS restaurant_id,
    NULLIF(TRIM(NAME), '') AS restaurant_name,
    NULLIF(TRIM(CITY), '') AS city,
    TRY_TO_DECIMAL(NULLIF(TRIM(RATING), ''), 3, 2) AS rating,
    TRY_TO_NUMBER(NULLIF(TRIM(RATING_COUNT), '')) AS rating_count,
    TRY_TO_DECIMAL(NULLIF(TRIM(COST), ''), 10, 2) AS cost,
    NULLIF(TRIM(CUISINE), '') AS cuisine,
    NULLIF(TRIM(LIC_NO), '') AS license_number,
    NULLIF(TRIM(LINK), '') AS restaurant_link,
    NULLIF(TRIM(ADDRESS), '') AS address,
    NULLIF(TRIM(MENU), '') AS menu
FROM {{ source('raw', 'raw_restaurant') }}