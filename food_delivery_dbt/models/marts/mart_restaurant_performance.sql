{{ config(materialized='table') }}

WITH order_metrics AS (
    SELECT
        restaurant_id,
        COUNT(*) AS order_item_count,
        COUNT(DISTINCT order_id) AS distinct_order_count,
        SUM(quantity) AS total_quantity_sold,
        SUM(line_amount) AS total_recorded_revenue
    FROM {{ ref('int_order_item_enriched') }}
    GROUP BY restaurant_id
),

review_metrics AS (
    SELECT
        restaurant_id,
        COUNT(*) AS review_count,
        AVG(rating) AS average_review_rating
    FROM {{ ref('stg_reviews') }}
    WHERE restaurant_id IS NOT NULL
    GROUP BY restaurant_id
)

SELECT
    r.restaurant_id,
    r.restaurant_name,
    r.city,
    r.cuisine,
    r.rating AS restaurant_listed_rating,
    COALESCE(o.order_item_count, 0) AS order_item_count,
    COALESCE(o.distinct_order_count, 0) AS distinct_order_count,
    COALESCE(o.total_quantity_sold, 0) AS total_quantity_sold,
    COALESCE(o.total_recorded_revenue, 0) AS total_recorded_revenue,
    COALESCE(v.review_count, 0) AS review_count,
    v.average_review_rating
FROM {{ ref('stg_restaurant') }} AS r
LEFT JOIN order_metrics AS o
    ON r.restaurant_id = o.restaurant_id
LEFT JOIN review_metrics AS v
    ON r.restaurant_id = v.restaurant_id