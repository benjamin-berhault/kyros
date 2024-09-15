-- models/my_new_model.sql
SELECT *
FROM {{ ref('my_existing_model') }}
WHERE date > '2024-01-01';
