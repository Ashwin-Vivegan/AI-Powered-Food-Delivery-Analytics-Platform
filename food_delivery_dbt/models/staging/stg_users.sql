{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(USER_ID), '') AS user_id,
    TRY_TO_NUMBER(NULLIF(TRIM(AGE), '')) AS age,
    NULLIF(TRIM(GENDER), '') AS gender,
    NULLIF(TRIM(MARITAL_STATUS), '') AS marital_status,
    NULLIF(TRIM(OCCUPATION), '') AS occupation,
    NULLIF(TRIM(MONTHLY_INCOME), '') AS monthly_income,
    NULLIF(TRIM(EDUCATIONAL_QUALIFICATIONS), '') AS educational_qualifications,
    TRY_TO_NUMBER(NULLIF(TRIM(FAMILY_SIZE), '')) AS family_size
FROM {{ source('raw', 'raw_users') }}