CREATE TABLE default.customers
(
    `customer_id` String,
    `customer_name` String,
    `city` String,
    `country` String,
    `membership_tier` String
)
ENGINE = MergeTree()
ORDER BY customer_id
SETTINGS index_granularity = 8192;

INSERT INTO default.customers
FROM INFILE '/docker-entrypoint-initdb.d/customers.csv'
FORMAT CSV;