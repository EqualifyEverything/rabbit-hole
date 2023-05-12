import json
from data.insert import create_crawl, record_urls, execute_insert
from utils.watch import logger


def process_crawler(channel, method, properties, body):
    logger.debug('Processing Crawler message...')
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
        logger.debug(f'URL added to list: {url}')

    # Call insert/update URLs
    logger.debug(f'Recording URLs for scan_id: {scan_id}')
    record_urls(scan_id, first_url_id, url_list)
    logger.debug('URLs recorded')

    channel.basic_ack(delivery_tag=method.delivery_tag)
    logger.debug('Crawler message acknowledged')


# Handle Gooseegg Results
def process_crawler_geese(channel, method, properties, body):
    logger.debug('Processing Crawler Goose egg')
    data = json.loads(body)
    url_id = data['source_url_id']
    logger.debug(f'Beginning to mark {url_id} as errored...')
    # Update targets.urls with active_crawler false
    column = 'active_crawler'
    status = 'false'
    update_url(url_id, column, status)
    logger.debug(f'{url_id} marked as active_crawler FALSE')


# Update the url active_ column in targets.urls
def update_url(url_id, column, status):
    try:
        logger.debug('Beginning to update url with error')
        # Update the active_.... column with status
        query = f"""
            UPDATE targets.urls
            SET {column} = %s
            WHERE id = %s
            RETURNING is_objective;
        """
        params = (
            status, url_id
        )
        things = execute_insert(query, params)
        logger.debug(f'URL {url_id} updated with error. {things}')
    except Exception as e:
        logger.error(f"Error updating URL {url_id} with error: {e}")
