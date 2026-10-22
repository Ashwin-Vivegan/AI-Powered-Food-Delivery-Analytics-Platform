{{ config(materialized='view') }}

SELECT
    oi.order_item_id,
    oi.order_id,
    oi.restaurant_id,
    r.restaurant_name,
    r.city,
    oi.food_id,
    f.food_name,
    f.food_category,
    oi.price,
    oi.quantity,
    oi.line_amount
FROM {{ ref('stg_order_items') }} AS oi
LEFT JOIN {{ ref('stg_food') }} AS f
    ON oi.food_id = f.food_id
LEFT JOIN {{ ref('stg_restaurant') }} AS r
    ON oi.restaurant_id = r.restaurant_id