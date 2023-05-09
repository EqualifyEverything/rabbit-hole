from utils.watch import logger
from data.insert import record_error, execute_insert
import json


def process_errors(channel, method, properties, body, queue, column, status):
    try:
        logger.debug(f'Processing {queue} error')
        message = json.loads(body)

        # Get Error Details from message
        url_id = message['url_id']
        error_message = message['error_message']

        logger.debug(f'Logging error for {url_id}...')
        # Record the Error
        record_error(queue, url_id, error_message)
        # Mark url as errored
        update_url(url_id, column, status)
        logger.debug(f'✅ Recorded error for {url_id}...')
    except Exception as e:
        logger.error(f"Error processing {queue} error: {e}")


# Specific Queue Error Handlers
    """
    The first variable is the queue name,
    the second is the column in targets.urls to update,
    and the third is the status to set for that column in targets.urls.
    """


# Handle Crawl Errors
def process_crawl_errors(channel, method, properties, body):
    process_errors(
        channel, method, properties, body,
        'error_crawler', 'active_crawler', 'false')


# Handle Uppies Errors
def process_uppies_errors(channel, method, properties, body):
    process_errors(
        channel, method, properties, body,
        'error_uppies', 'active_scan_uppies', 'false')


# Handle Axe Errors
def process_axe_errors(channel, method, properties, body):
    process_errors(
        channel, method, properties, body,
        'error_axe', 'active_scan_axe', 'false')


# Update the url active_ column in targets.urls
def update_url(url_id, column, status):
    try:
        logger.debug('Beginning to update url with error')
        # Update the active_.... column with status
        query = """
            UPDATE targets.urls
            SET %s = %s
            WHERE id = %s;
        """
        params = (
            column, status, url_id
        )
        execute_insert(query, params)
        logger.debug(f'URL {url_id} updated with error')
    except Exception as e:
        logger.error(f"Error updating URL {url_id} with error: {e}")
