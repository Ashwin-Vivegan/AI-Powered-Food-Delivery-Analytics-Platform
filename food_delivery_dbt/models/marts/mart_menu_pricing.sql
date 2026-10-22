{{ config(materialized='table') }}

SELECT
    m.food_id,
    f.food_name,
    m.restaurant_id,
    r.restaurant_name,
    r.city,
    m.cuisine,
    m.price AS menu_price,
    AVG(m.price) OVER (
        PARTITION BY m.food_id
    ) AS average_food_price_across_menus,
    MIN(m.price) OVER (
        PARTITION BY m.food_id
    ) AS minimum_food_price,
    MAX(m.price) OVER (
        PARTITION BY m.food_id
    ) AS maximum_food_price
FROM {{ ref('stg_menu') }} AS m
LEFT JOIN {{ ref('stg_food') }} AS f
    ON m.food_id = f.food_id
LEFT JOIN {{ ref('stg_restaurant') }} AS r
    ON m.restaurant_id = r.restaurant_id
WHERE m.price IS NOT NULL