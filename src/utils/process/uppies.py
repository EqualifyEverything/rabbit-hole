import json
from data.insert import create_crawl, record_urls
from utils.watch import logger


def process_uppies(channel, method, properties, body):
    logger.info('PROCESSING UPPIES PLACEHOLDER')


def process_crawler(channel, method, properties, body):
    messages = json.loads(body)

    # Count the number of url items in the message
    urls_found = len(messages)

    # Create a single scan_id for all messages
    first_message = messages[0]
    first_url_id = first_message['source_url_id']
    scan_id = create_crawl(first_url_id, urls_found)

    # Log the message
    logger.info("New Crawl Created: scan_id = %d", scan_id)

    # Collect all the URLs
    url_list = []
    for message in messages:
        # url_id = message['source_url_id']
        url = message['url']
        url_list.append(url)

    # Call insert/update URLs
    record_urls(scan_id, first_url_id, url_list)
    channel.basic_ack(delivery_tag=method.delivery_tag)
