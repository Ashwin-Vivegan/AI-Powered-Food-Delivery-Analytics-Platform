{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(SOURCE_INDEX), '') AS source_index,
    NULLIF(TRIM(F_ID), '') AS food_id,
    NULLIF(TRIM(ITEM), '') AS food_name,
    NULLIF(TRIM(VEG_OR_NON_VEG), '') AS food_category
FROM {{ source('raw', 'raw_food') }}