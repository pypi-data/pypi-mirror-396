CREATE TABLE default.orders
(
    `order_id` String,
    `customer_id` String,
    `product` String,
    `quantity` Int64,
    `unit_price` Int64,
    `order_date` String
)
ENGINE = MergeTree()
ORDER BY order_id
SETTINGS index_granularity = 8192;

INSERT INTO default.orders
FROM INFILE '/docker-entrypoint-initdb.d/orders.csv'
FORMAT CSV;