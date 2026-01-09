import logging
import json
import psycopg2
from psycopg2.extras import execute_batch
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext , MessageField
from confluent_kafka import Consumer , KafkaError
from dotenv import load_dotenv
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="real_time_crypto_consumer.log",
    filemode="a"
)

load_dotenv()

logger = logging.getLogger()

bootstrap_servers = os.getenv("bootstrap_servers")
security_protocol = os.getenv("security_protocol")
sasl_mechanisims = os.getenv("sasl_mechanisms")
sasl_username = os.getenv("sasl_username")
sasl_password = os.getenv("sasl_password")

confluent_consumer_configuration = {
        'bootstrap.servers': bootstrap_servers,
        'security.protocol': security_protocol,
        'sasl.mechanism': sasl_mechanisims,
        'sasl.username': sasl_username,
        'sasl.password': sasl_password,
        'group.id': 'foo',
        'auto.offset.reset': 'smallest'
}

schema_registry_configuration = {
    'url': os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('SCHEMA_REGISTRY_KEY')}:{os.getenv('SCHEMA_REGISTRY_SECRET')}"
}

schema_registry_client = SchemaRegistryClient(schema_registry_configuration)
avro_deserializer = AvroDeserializer(
    schema_registry_client,
    schema_str=None  
)

timescale_database_configuration = {
    'host': os.getenv('PGHOST'),
    'database': os.getenv('PGDATABASE'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'port': 5432,
    'sslmode': 'require'
}


def create_timescale_table():
    try:
        conn = psycopg2.connect(**timescale_database_configuration)
        cursor = conn.cursor()

        create_table_query = """
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
"""
        cursor.execute(create_table_query)

        try:
            hypertable_query = """
 SELECT create_hypertable('coinbase_prices', 'time', if_not_exists => TRUE);
"""
            cursor.execute(hypertable_query)
            logger.info("Hypertabe created succesfully")
        except Exception as e:
            logger.error(f"Hyperytable may already exist.")

        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_product_time ON coinbase_prices (product_id, time DESC);",
            "CREATE INDEX IF NOT EXISTS idx_product_id ON coinbase_prices (product_id);",
            "CREATE INDEX IF NOT EXISTS idx_time ON coinbase_prices (time DESC);"
        ]

        for query in index_queries:
            cursor.execute(query)
        conn.commit()
        conn.close()
        logger.info("TImescaledb tables and indices created.")

    except Exception as e:
        logger.info(f"An error {e} occurred when creating timescale tables")
        raise


def Insert_to_timescale_db(data_batch):
    try:
        conn = psycopg2.connect(**timescale_database_configuration)
        cursor = conn.cursor()

        insert_query = """
INSERT INTO coinbase_prices (
            time, product_id, type, sequence, price, open_24h, 
            volume_24h, low_24h, high_24h, volume_30d, 
            best_bid, best_ask, side, trade_id, last_size
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT DO NOTHING;
"""

        values = []
        for data in data_batch:
            try:
                timestamp = datetime.fromisoformat(data.get('time','').replace('Z','+00:00'))
            except:
                timestamp = datetime.utcnow()

            values.append((
                timestamp,
                data.get('product_id'),
                data.get('type'),
                data.get('sequence'),
                float(data.get('price', 0)) if data.get('price') else None,
                float(data.get('open_24h', 0)) if data.get('open_24h') else None,
                float(data.get('volume_24h', 0)) if data.get('volume_24h') else None,
                float(data.get('low_24h', 0)) if data.get('low_24h') else None,
                float(data.get('high_24h', 0)) if data.get('high_24h') else None,
                float(data.get('volume_30d', 0)) if data.get('volume_30d') else None,
                float(data.get('best_bid', 0)) if data.get('best_bid') else None,
                float(data.get('best_ask', 0)) if data.get('best_ask') else None,
                data.get('side'),
                data.get('trade_id'),
                float(data.get('last_size', 0)) if data.get('last_size') else None
            ))

        execute_batch(cursor,insert_query,values)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Inserted values into the timescale database.")
    except Exception as e:
        logger.error(f"An erorr {e} occured inserting data into the table")
        raise



def consume_and_store():
    consumer =Consumer(confluent_consumer_configuration)
    consumer.subscribe(["coinbase_market_streaming"])

    logger.info("ocnsumer started , Listening for messages")
    batch = []
    batch_size = 100

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message , flush batch if exists...
                if batch:
                    Insert_to_timescale_db(batch)
                    consumer.commit()
                    logger.info(f"Commited a batch of {len(batch)} messages ")
                    batch = []
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"Reached end of parttion {msg.partition()}")
                else:
                    logger.error(f"Consumer error {msg.error()}")
                continue

            try:
                data = avro_deserializer(
                    msg.value(),
                    SerializationContext(msg.topic(), MessageField.VALUE)
                )
                batch.append(data)
                logger.info(f"Received: {data.get('product_id')} - ${data.get('price')}")

                if len(batch) >= batch_size:
                    Insert_to_timescale_db(batch)
                    consumer.commit()
                    print(f"Committed batch of {len(batch)} messages")
                    batch = []


            except Exception as e:
                logger.error(f"An error {e} occured tryign to desirialize messages")
                continue

    except KeyboardInterrupt:
        logger.error("Consumer Interrupted by the user")

    finally:
        if batch:
            Insert_to_timescale_db(batch)
            consumer.commit()
        
        consumer.close()
        logger.info("Consumer closed")

if __name__ == "__main__":
    create_timescale_table()
    consume_and_store()