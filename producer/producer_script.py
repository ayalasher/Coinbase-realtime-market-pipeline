import logging
import json
import websocket
from confluent_kafka import Producer , KafkaError
from confluent_kafka.serialization import SerializationContext , MessageField, StringSerializer
from dotenv import load_dotenv
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema.main import avro_serializer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="real_time_crypto_producer.log",
    filemode="a"
)

load_dotenv()

logger = logging.getLogger()

production_websocket_url = "wss://ws-feed.exchange.coinbase.com"

subscribe_message = {

    "type": "subscribe",
    "product_ids": [
        "ETH-USD",
        "BTC-USD",
        "ETH-EUR",
        "BTC-EUR",

    ],
    "channels": ["ticker"]

}

bootstrap_servers = os.getenv("bootstrap_servers")
security_protocol = os.getenv("security_protocol")
sasl_mechanisms = os.getenv("sasl_mechanisms")
sasl_username = os.getenv("sasl_username")
sasl_password = os.getenv("sasl_password")
session_timeout_milliseconds = 45000
client_id = os.getenv("client_id")

confluent_config = {
   'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanisms,
    'sasl.username': sasl_username,
    'sasl.password': sasl_password ,
    'client.id':client_id
}


configured_kafka_producer =  Producer(confluent_config)
string_serializer = StringSerializer('utf_8')

kafka_topic = "coinbase_market_streaming"

def delivery_report(err:KafkaError, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def on_open(ws):
    try:
        logger.info("Websocket connection happened")
        ws.send(json.dumps(subscribe_message))
        logger.info(f"Subscription message sent : {subscribe_message} ")
    except Exception as e :
        logger.error(f"an error {e} while trying to send the subscription message")


def on_message(ws, message):
    try:
        data = json.loads(message)
        logger.info(f"Received message : {data.get('type','unknown')}")
        # Serilization with the avro schema
        serialized_value = avro_serializer(
            data,
            SerializationContext(kafka_topic,MessageField.VALUE)
        )

        serialized_key = string_serializer(
            data.get('product_id','unknown'),
            SerializationContext(kafka_topic,MessageField.KEY)
        )


        configured_kafka_producer.produce(
            kafka_topic,
            key=serialized_key,
            value=serialized_value,
            callback=delivery_report
        )
        configured_kafka_producer.poll(0)
        print(f"Message : {json.dumps(data , indent=2)}")
    except Exception as e:
        logger.error(f"An error {e} occured while trying to get the sent message and send it to kafka")

def on_error(ws , error):
    logger.error(f"an error {error} occured in the websocket")
    print(f"Error:{error}")


def on_close(ws, close_status_code,close_msg):
    logger.info(f"Websocket connection closed : {close_status_code} - {close_msg}")
    print("Websocket connection closed")


ws = websocket.WebSocketApp(
    production_websocket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.run_forever()
logger.info("Starting the websocker server")

