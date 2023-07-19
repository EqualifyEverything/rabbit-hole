from utils.watch import logger
from data.insert import record_error, execute_insert
import json


# Handle Crawl Errors
def process_crawl_errors(channel, method, properties, body):
    logger.debug('Processing Crawler Error Queue')
    try:
        # Deserialize the message
        data = json.loads(body)

        # Get the data from the queue
        queue = 'error_crawler'
        url_id = data['url_id']
        error_message = data['error_message']

        record_error(queue, url_id, error_message)
        logger.info(f'Error Logged:\nURL ID: {url_id}\nQueue: {queue}')

    except Exception as e:
        logger.error(f"Error processing {queue} error: {e}")

    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug('Crawl Error Acknowledged')


# Handle Uppies Errors
def process_uppies_errors(channel, method, properties, body):
    logger.debug('Processing Uppies Error Queue')
    try:
        # Deserialize the message
        data = json.loads(body)

        # Get the data from the queue
        queue = 'error_uppies'
        url_id = data['url_id']
        error_message = data['error_message']

        record_error(queue, url_id, error_message)
        logger.info(f'Error Logged:\nURL ID: {url_id}\nQueue: {queue}')

    except Exception as e:
        logger.error(f"Error processing {queue} error: {e}")

    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug('Uppies Error Acknowledged')


# Handle Axe Errors
def process_axe_errors(channel, method, properties, body):
    logger.debug('Processing Axe Error Queue')
    try:
        # Deserialize the message
        data = json.loads(body)

        # Get the data from the queue
        queue = 'error_axe'
        url_id = data['url_id']
        error_message = data['error_message']

        record_error(queue, url_id, error_message)
        logger.info(f'Error Logged:\nURL ID: {url_id}\nQueue: {queue}')

    except Exception as e:
        logger.error(f"Error processing {queue} error: {e}")

    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug('Axe Error Acknowledged')





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
