{{ config(materialized='table') }}

WITH review_metrics AS (
    SELECT
        restaurant_id,
        COUNT(*) AS review_count,
        COUNT(rating) AS rated_review_count,
        AVG(rating) AS average_review_rating,
        COUNT_IF(rating >= 4) AS positive_review_count,
        COUNT_IF(rating <= 2) AS low_rating_review_count,
        COUNT_IF(rating = 3) AS neutral_rating_review_count,
        MIN(review_date) AS first_review_date,
        MAX(review_date) AS latest_review_date
    FROM {{ ref('stg_reviews') }}
    WHERE restaurant_id IS NOT NULL
    GROUP BY restaurant_id
)

SELECT
    r.restaurant_id,
    r.restaurant_name,
    r.city,
    r.rating AS restaurant_listed_rating,
    COALESCE(v.review_count, 0) AS review_count,
    COALESCE(v.rated_review_count, 0) AS rated_review_count,
    v.average_review_rating,
    COALESCE(v.positive_review_count, 0) AS positive_review_count,
    COALESCE(v.low_rating_review_count, 0) AS low_rating_review_count,
    COALESCE(v.neutral_rating_review_count, 0)
        AS neutral_rating_review_count,
    v.first_review_date,
    v.latest_review_date
FROM {{ ref('stg_restaurant') }} AS r
LEFT JOIN review_metrics AS v
    ON r.restaurant_id = v.restaurant_id