-- The current prices of all products
SELECT 
    time as "time",
    product_id as metric,
    price as value
FROM coinbase_prices
WHERE time > NOW() - INTERVAL '1 hour'
ORDER BY time;

-- Current value of Bitcoin in USD
SELECT 
    price as value,
    time
FROM coinbase_prices
WHERE product_id = 'BTC-USD'
ORDER BY time DESC
LIMIT 1;

-- Current value of Bitcoin in Euros
SELECT 
    price as value,
    time
FROM coinbase_prices
WHERE product_id = 'BTC-EUR'
ORDER BY time DESC
LIMIT 1;

-- Current value of Ethereum in USD
SELECT 
    price as value,
    time
FROM coinbase_prices
WHERE product_id = 'ETH-USD'
ORDER BY time DESC
LIMIT 1;



-- current value of Ethereum in euros
SELECT 
    price as value,
    time
FROM coinbase_prices
WHERE product_id = 'ETH-EUR'
ORDER BY time DESC
LIMIT 1;

