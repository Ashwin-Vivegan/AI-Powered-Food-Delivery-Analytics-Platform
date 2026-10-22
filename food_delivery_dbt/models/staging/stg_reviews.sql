{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(REVIEW_ID), '') AS review_id,
    NULLIF(TRIM(ORDER_ID), '') AS order_id,
    NULLIF(TRIM(USER_ID), '') AS user_id,
    NULLIF(TRIM(RESTAURANT_ID), '') AS restaurant_id,
    TRY_TO_DECIMAL(NULLIF(TRIM(RATING), ''), 3, 2) AS rating,
    NULLIF(TRIM(COMMENT), '') AS review_comment,
    TRY_TO_DATE(NULLIF(TRIM(REVIEW_DATE), '')) AS review_date
FROM {{ source('raw', 'raw_reviews') }}