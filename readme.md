# Coinbase Real-time Market Data Streaming Pipeline

![Project Banner](https://img.shields.io/badge/Real--time-Crypto%20Data-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![Kafka](https://img.shields.io/badge/Kafka-Confluent%20Cloud-orange)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Neon-purple)
![Grafana](https://img.shields.io/badge/Grafana-Visualization-red)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Grafana Dashboard](#grafana-dashboard)
- [SQL Queries](#sql-queries)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

A real-time data streaming pipeline that ingests cryptocurrency market data from **Coinbase WebSocket API**, processes it through **Apache Kafka** (Confluent Cloud), stores it in **TimescaleDB** (Neon), and visualizes live metrics using **Grafana**.

### Key Capabilities:

- Real-time ingestion of BTC/ETH prices (USD & EUR)
- Avro schema validation via Confluent Schema Registry
- Time-series data storage with TimescaleDB hypertables
- Live Grafana dashboards with 5-second refresh
- Flink SQL support for stream processing

---

## Architecture

```
┌─────────────────┐
│  Coinbase API   │
│   (WebSocket)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Python Producer│─────▶│  Confluent Cloud │
│  (Avro Serializer)│    │   Apache Kafka   │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌────────────────┐
                         │ Schema Registry│
                         │  (Avro Schema) │
                         └────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                  ▼
┌─────────────────┐                              ┌──────────────────┐
│ Flink SQL       │                              │ Python Consumer  │
│ (Stream Proc.)  │                              │ (Avro Deserializer)│
└─────────────────┘                              └─────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  TimescaleDB    │
                                                  │  (Neon Postgres)│
                                                  └────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │     Grafana     │
                                                  │   (Real-time    │
                                                  │   Dashboards)   │
                                                  └─────────────────┘
```

---

## Features

### Data Ingestion

- WebSocket connection to Coinbase ticker channel
- Automatic reconnection on failures
- Supports 4 trading pairs: BTC-USD, BTC-EUR, ETH-USD, ETH-EUR

### Stream Processing

- Avro serialization with schema evolution support
- Kafka message batching for efficiency
- Confluent Cloud managed Kafka cluster
- Flink SQL for real-time analytics

### Data Storage

- TimescaleDB hypertables for time-series optimization
- Automatic data retention policies
- Indexed queries for fast retrieval
- Batch inserts (100 records per commit)

### Visualization

- Real-time Grafana dashboards
- Gauge panels for current prices
- Time-series charts (1-hour window)
- Auto-refresh every 5 seconds

---

## Tech Stack

| Component             | Technology                     | Purpose                     |
| --------------------- | ------------------------------ | --------------------------- |
| **Message Broker**    | Apache Kafka (Confluent Cloud) | Event streaming platform    |
| **Schema Registry**   | Confluent Schema Registry      | Avro schema management      |
| **Stream Processing** | Apache Flink SQL               | Real-time data processing   |
| **Database**          | TimescaleDB on Neon            | Time-series data storage    |
| **Visualization**     | Grafana                        | Real-time dashboards        |
| **Language**          | Python 3.12                    | Producer & Consumer scripts |
| **Data Format**       | Avro                           | Schema validation           |

---

## Prerequisites

### Software Requirements

- Python 3.12+
- pip (Python package manager)
- Git
- Grafana (local or cloud)

### Cloud Services

1. **Confluent Cloud Account** (free tier available)
   - Kafka cluster
   - Schema Registry
2. **Neon Account** (free tier available)

   - PostgreSQL database with TimescaleDB extension

3. **Coinbase Account** (API access is free)

---

## Project Structure

```
Coin_base_real_time_pipeline/
│
├── producer/
│   └── producer_script.py          # Kafka producer (WebSocket → Kafka)
│
├── consumer/
│   └── consumer.py                 # Kafka consumer (Kafka → TimescaleDB)
│
├── schema/
│   ├── main.py                     # Avro schema definition & registration
│   └── __pycache__/
│
├── infra/
│   └── create_topics.py            # Kafka topic creation script
│
├── notebooks/
│   └── test.ipynb                  # Testing and exploration notebook
│
├── sql/
│   ├── flink/
│   │   └── queries.sql             # Flink SQL queries for stream processing
│   ├── grafana/
│   │   └── queries.sql             # Grafana SQL queries
│   └── timescaledb/
│       └── queries.sql             # TimescaleDB specific queries
│
├── visualization/                  # Dashboard exports and configs
│
├── .env                            # Environment variables (DO NOT COMMIT)
├── .gitignore
├── test_websocket_script.py        # WebSocket connection testing
├── real_time_crypto_producer.log   # Producer logs
├── real_time_crypto_consumer.log   # Consumer logs
├── real_time_crypto_pipeline.log   # Pipeline logs
├── schema.log                      # Schema registration logs
├── requirements.txt                # Python dependencies
└── readme.md
```

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/ayalasher/Coinbase-realtime-market-pipeline.git
cd Coinbase-realtime-market-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```txt
confluent-kafka[avro]==2.3.0
orjson==3.9.10
fastavro==1.9.4
websocket-client==1.7.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

### 3. Configure Environment Variables

Create `.env` file in project root:

> **Note:** The values below are dummy examples. Replace them with your actual credentials from Confluent Cloud and Neon.

```bash
# Confluent Kafka Configuration
bootstrap_servers=pkc-xxxxx.region.cloud-provider.confluent.cloud:9092
security_protocol=SASL_SSL
sasl_mechanisms=PLAIN
sasl_username=YOUR_CONFLUENT_API_KEY
sasl_password=YOUR_CONFLUENT_API_SECRET
client_id=coinbase_producer

# Schema Registry Configuration
SCHEMA_REGISTRY_URL=https://psrc-xxxxx.region.cloud-provider.confluent.cloud
SCHEMA_REGISTRY_KEY=YOUR_SCHEMA_REGISTRY_API_KEY
SCHEMA_REGISTRY_SECRET=YOUR_SCHEMA_REGISTRY_API_SECRET

# Neon TimescaleDB Configuration
NEON_HOST=ep-xxxxx-xxxxx.region.cloud-provider.neon.tech
NEON_DATABASE=CoinbaseMarketData
NEON_USER=your_neon_username
NEON_PASSWORD=your_neon_password
NEON_PORT=5432
```

### 4. Setup Neon Database

Connect to Neon and run:

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tables will be auto-created by consumer script
```

### 5. Register Avro Schema

```bash
python schema/main.py
```

Expected output:

```
Schema registered with ID: 100001
```

---

## Running the Pipeline

### Step 1: Start Producer (WebSocket to Kafka)

```bash
python producer/producer_script.py
```

**Expected Output:**

```
Websocket connection happened
Message sent: BTC-USD - $95234.56
Message sent: ETH-USD - $3456.78
...
```

### Step 2: Start Consumer (Kafka to TimescaleDB)

```bash
python consumer/consumer.py
```

**Expected Output:**

```
Setting up TimescaleDB tables...
TimescaleDB tables created
Consumer started...
BTC-USD: $95234.56
Committed batch of 100 messages
...
```

### Step 3: Verify Data in Neon

```sql
SELECT COUNT(*) FROM coinbase_prices;
-- Should show increasing count

SELECT product_id, price, time
FROM coinbase_prices
ORDER BY time DESC
LIMIT 10;
```

---

## Grafana Dashboard

### Setup Grafana Data Source

1. **Open Grafana** → Configuration → Data Sources
2. **Add PostgreSQL data source:**

   - Host: `ep-xxxxx.eastus2.azure.neon.tech:5432`
   - Database: `CoinbaseMarketData`
   - User: `your_username`
   - Password: `your_password`
   - SSL Mode: `require`
   - Version: `14+`

3. **Test & Save**

### Create Dashboard

1. **New Dashboard** → Add panel
2. **Configure 5 panels:**

#### Panel 1: Time Series (All Products)

```sql
SELECT
    time as "time",
    product_id as metric,
    price as value
FROM coinbase_prices
WHERE time > NOW() - INTERVAL '1 hour'
ORDER BY time;
```

- Visualization: Time series
- Refresh: 5s

#### Panel 2-5: Gauge Panels

```sql
-- BTC-USD
SELECT price as value, time
FROM coinbase_prices
WHERE product_id = 'BTC-USD'
ORDER BY time DESC
LIMIT 1;
```

- Visualization: Gauge
- Unit: currency (USD)
- Min: 0
- Thresholds: 90000 (orange), 95000 (yellow), 100000 (green)

**Repeat for BTC-EUR, ETH-USD, ETH-EUR**

---

## SQL Queries

### Flink SQL (Confluent Cloud)

```sql
-- View real-time data
SELECT * FROM `default`.`cluster_0`.`coinbase_market_streaming` LIMIT 10;

-- 1-minute window aggregation
SELECT
    product_id,
    TUMBLE_START(TO_TIMESTAMP(`time`), INTERVAL '1' MINUTE) as window_start,
    AVG(CAST(price AS DECIMAL(20, 8))) as avg_price
FROM `default`.`cluster_0`.`coinbase_market_streaming`
GROUP BY product_id, TUMBLE(TO_TIMESTAMP(`time`), INTERVAL '1' MINUTE);
```

### TimescaleDB Analytics

```sql
-- Average price per product (last hour)
SELECT
    product_id,
    AVG(price) as avg_price,
    COUNT(*) as tick_count
FROM coinbase_prices
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY product_id;

-- OHLC data (5-minute candles)
SELECT
    time_bucket('5 minutes', time) as "time",
    product_id,
    FIRST(price, time) as open,
    MAX(price) as high,
    MIN(price) as low,
    LAST(price, time) as close
FROM coinbase_prices
WHERE product_id = 'BTC-USD'
  AND time > NOW() - INTERVAL '24 hours'
GROUP BY time_bucket('5 minutes', time), product_id
ORDER BY time;
```

---

## Monitoring & Logs

### Log Files

- **Producer logs**: `producer/real_time_crypto_producer.log`
- **Consumer logs**: `consumer/real_time_crypto_consumer.log`
- **Schema logs**: `schema/schema.log`

### Monitor Kafka

1. **Confluent Cloud UI** → Topics → `coinbase_market_streaming`
2. Check message throughput
3. Monitor consumer lag

### Monitor Database

```sql
-- Check data freshness
SELECT
    product_id,
    MAX(time) as last_update,
    NOW() - MAX(time) as lag
FROM coinbase_prices
GROUP BY product_id;

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('coinbase_prices'));
```

---

## Troubleshooting

### Common Issues

#### 1. Producer Not Sending Messages

```bash
# Check logs
tail -f producer/real_time_crypto_producer.log

# Verify Kafka credentials in .env
# Test websocket connection manually
```

#### 2. Consumer Not Inserting Data

```bash
# Check consumer logs
tail -f consumer/real_time_crypto_consumer.log

# Verify Neon connection
psql "postgresql://user:password@host/database?sslmode=require"
```

#### 3. Grafana Shows No Data

```sql
-- Test query in Neon SQL editor first
SELECT COUNT(*) FROM coinbase_prices;

-- Verify time range in Grafana (use Last 1 hour)
-- Check data source connection
```

#### 4. Schema Registry Errors

```bash
# Re-register schema
python schema/main.py

# Check Schema Registry in Confluent Cloud UI
```

---

## Future Enhancements

- [ ] Implement alerting (price thresholds)
- [ ] Add data quality checks
- [ ] Create predictive ML models
- [ ] Add API for historical data queries
- [ ] Implement continuous aggregations in TimescaleDB
- [ ] Add tests
- [ ] Create mobile-responsive Grafana dashboards
- [ ] Add data backup and disaster recovery

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author

**Your Name**

- GitHub: [@ayalasher](https://github.com/ayalasher)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## Acknowledgments

- [Coinbase API Documentation](https://docs.cloud.coinbase.com/exchange/docs)
- [Confluent Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## Project Stats

![GitHub stars](https://img.shields.io/github/stars/ayalasher/Coinbase-realtime-market-pipeline)
![GitHub forks](https://img.shields.io/github/forks/ayalasher/Coinbase-realtime-market-pipeline)
![GitHub issues](https://img.shields.io/github/issues/ayalasher/Coinbase-realtime-market-pipeline)

---

**Data engineering rocks 🚀**
