# Confluent kafka schema registry
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s ",
    filename="schema.log",
    filemode="a"
)

logger = logging.getLogger()
load_dotenv()

schema_registry_conf = {
    'url':os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('SCHEMA_REGISTRY_KEY')}:{os.getenv('SCHEMA_REGISTRY_SECRET')}"
}

schema_registry_client = SchemaRegistryClient(schema_registry_conf)

coinbase_ticker_schema = """
{
  "type": "record",
  "name": "CoinbaseTicker",
  "namespace": "com.coinbase.ticker",
  "fields": [
    {"name": "type", "type": "string"},
    {"name": "sequence", "type": ["null", "long"], "default": null},
    {"name": "product_id", "type": "string"},
    {"name": "price", "type": ["null", "string"], "default": null},
    {"name": "open_24h", "type": ["null", "string"], "default": null},
    {"name": "volume_24h", "type": ["null", "string"], "default": null},
    {"name": "low_24h", "type": ["null", "string"], "default": null},
    {"name": "high_24h", "type": ["null", "string"], "default": null},
    {"name": "volume_30d", "type": ["null", "string"], "default": null},
    {"name": "best_bid", "type": ["null", "string"], "default": null},
    {"name": "best_ask", "type": ["null", "string"], "default": null},
    {"name": "side", "type": ["null", "string"], "default": null},
    {"name": "time", "type": "string"},
    {"name": "trade_id", "type": ["null", "long"], "default": null},
    {"name": "last_size", "type": ["null", "string"], "default": null}
  ]
}
"""

avro_serializer = AvroSerializer(
    schema_registry_client,
    coinbase_ticker_schema
    )


def register_schema(subject_name="topic_kafka_coinbase_test-value"):
    try:
        schema_id = schema_registry_client.register_schema(
            subject_name=subject_name,
            schema=coinbase_ticker_schema
        )
        logger.info(f"Schema registered succesfully with ID {schema_id} ")
        return schema_id
    except Exception as e:
        logger.info(f"An error {e} occured registering the schema")
        return None


def test_schema_registry_connection():
    try:
        subjects = schema_registry_client.get_subjects()
        logger.info(f"Connected to the schema registry.Existing subjects{subjects}")
        return True
    except Exception as e:
        logger.info(f"An error {e} occurred when testing the schema registry connection")
        return False



if __name__ == "__main__":
    print("Testing Schema registry")
    if test_schema_registry_connection():
        print("\n Registering schema")
        register_schema()