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

