import json
import websocket
import time
import logging

# Logger configuration...
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="real_time_crypto_pipeline.log",
    # 'a' simply means append -- Changes are going to be writen at the end of the file...
    filemode="a"
    )

logger = logging.getLogger()

sanbox_websocket_url = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
production_websocket_url = "wss://ws-feed.exchange.coinbase.com"

''' 
    This is common when working with crypto Websocket 
    API's and is used with the 
    on_message event handler... 
'''


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

# Defining the websocket event handlers...
def on_open(ws):
    try:
        logger.info("Websocket connection opened")
        # send a message when a websocket connection has been made..
        ws.send(json.dumps(subscribe_message))
        logger.info(f"subcription massage sent : {subscribe_message}")
    except Exception as e:
        logger.error(f"An error {e} trying to send the subscription message")
        raise

def on_message(ws,message):
    # receiving a stirng formatted json object and loading it into a pyrhon dictionary...
    try:
        data = json.loads(message)
        logger.info(f"Received message : {data.get('type','unknown')}")
        print(f"Message : {json.dumps(data , indent=2)} ")
    except Exception as e:
        logger.error(f"An error : {e} Occured when getting a sent message")
        raise
def on_error(ws, error):
    logger.error(f"An error : {error} occured in our websocket")
    print(f"Error:{error}")

def on_close(ws , close_status_code , close_msg):
    logger.info(f"Websocket connection closed : {close_status_code} - {close_msg}")
    print("Websocket connection closed...")

# Creating a websocket clint connection...
ws = websocket.WebSocketApp(
    production_websocket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

logger.info("Starting the websocket server")
ws.run_forever()