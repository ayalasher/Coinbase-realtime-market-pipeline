-- Queries you can run to explore your 
-- data in The flink SQL workspace available in the confluent cloud web UI

-- View the 10 latest messages
SELECT * 
FROM `default`.`cluster_0`.`coinbase_market_streaming`
LIMIT 10;

-- Products count via the product_id
SELECT DISTINCT product_id AS message_count
FROM `default`.`cluster_0`.`coinbase_market_streaming`
GROUP BY product_id

-- Latest prices per product
SELECT 
    product_id,
    price,
    best_bid,
    best_ask,
    `time`
FROM `default`.`cluster_0`.`coinbase_market_streaming`
ORDER BY `time` DESC
LIMIT 20;

-- Average price 1 minute tumbling window
SELECT 
    product_id,
    TUMBLE_START(TO_TIMESTAMP(`time`), INTERVAL '1' MINUTE) as window_start,
    TUMBLE_END(TO_TIMESTAMP(`time`), INTERVAL '1' MINUTE) as window_end,
    AVG(CAST(price AS DECIMAL(20, 8))) as avg_price,
    MIN(CAST(price AS DECIMAL(20, 8))) as min_price,
    MAX(CAST(price AS DECIMAL(20, 8))) as max_price,
    COUNT(*) as tick_count
FROM `default`.`cluster_0`.`coinbase_market_streaming`
WHERE product_id IN ('BTC-USD', 'ETH-USD')
GROUP BY 
    product_id,
    TUMBLE(TO_TIMESTAMP(`time`), INTERVAL '1' MINUTE);


-- Ethereum vs bitcoin price ration
SELECT 
    `time`,
    MAX(CASE WHEN product_id = 'ETH-USD' THEN CAST(price AS DECIMAL(20, 8)) END) as eth_price,
    MAX(CASE WHEN product_id = 'BTC-USD' THEN CAST(price AS DECIMAL(20, 8)) END) as btc_price,
    MAX(CASE WHEN product_id = 'ETH-USD' THEN CAST(price AS DECIMAL(20, 8)) END) / 
    MAX(CASE WHEN product_id = 'BTC-USD' THEN CAST(price AS DECIMAL(20, 8)) END) as eth_btc_ratio
FROM `default`.`cluster_0`.`coinbase_market_streaming`
WHERE product_id IN ('ETH-USD', 'BTC-USD')
GROUP BY `time`
ORDER BY `time` DESC
LIMIT 10;

-- Bitcoin value -- USD vs EURO
SELECT 
    `time`,
    MAX(CASE WHEN product_id = 'BTC-USD' THEN CAST(price AS DECIMAL(20, 8)) END) as btc_usd,
    MAX(CASE WHEN product_id = 'BTC-EUR' THEN CAST(price AS DECIMAL(20, 8)) END) as btc_eur,
    MAX(CASE WHEN product_id = 'BTC-USD' THEN CAST(price AS DECIMAL(20, 8)) END) / 
    MAX(CASE WHEN product_id = 'BTC-EUR' THEN CAST(price AS DECIMAL(20, 8)) END) as usd_eur_rate
FROM `default`.`cluster_0`.`coinbase_market_streaming`
WHERE product_id IN ('BTC-USD', 'BTC-EUR')
GROUP BY `time`
ORDER BY `time` DESC
LIMIT 10;



-- Timescaledb queries
-- Enabling the timescaledb extension on our neon hosted postgres database
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS coinbase_prices (
            time TIMESTAMPTZ NOT NULL,
            product_id TEXT NOT NULL,
            type TEXT,
            sequence BIGINT,
            price NUMERIC(20, 8),
            open_24h NUMERIC(20, 8),
            volume_24h NUMERIC(20, 8),
            low_24h NUMERIC(20, 8),
            high_24h NUMERIC(20, 8),
            volume_30d NUMERIC(20, 8),
            best_bid NUMERIC(20, 8),
            best_ask NUMERIC(20, 8),
            side TEXT,
            trade_id BIGINT,
            last_size NUMERIC(20, 8)
        );

