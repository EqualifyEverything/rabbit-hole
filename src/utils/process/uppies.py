import json
from data.insert import record_uppies
from utils.watch import logger


def process_uppies(channel, method, properties, body):
    message = json.loads(body)
    url_id = message['url_id']
    data = message['data']

    # Log the message
    logger.debug(f"New Uppies Inserted: {url_id} - {data['status_code']}")

    # Call insert/update URLs
    record_uppies(url_id, data)
    channel.basic_ack(delivery_tag=method.delivery_tag)
