import logging
import json
from confluent_kafka import Consumer , KafkaError
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="real_time_crypto_consumer.log",
    filemode="a"
)

load_dotenv()

logger = logging.getLogger()