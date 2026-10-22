{{ config(materialized='table') }}

SELECT
    food_id,
    food_name,
    food_category,
    COUNT(*) AS order_item_count,
    COUNT(DISTINCT order_id) AS distinct_order_count,
    SUM(quantity) AS total_quantity_sold,
    SUM(line_amount) AS total_recorded_revenue,
    AVG(price) AS average_unit_price
FROM {{ ref('int_order_item_enriched') }}
GROUP BY
    food_id,
    food_name,
    food_category