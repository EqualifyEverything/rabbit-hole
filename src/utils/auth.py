import pika
from utils.watch import logger

def rabbit(queue_name, message):
    try:
        logger.debug('Connecting to RabbitMQ server...')
        credentials = pika.PlainCredentials('rabbit_hole', 'lets_insert_things')
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', credentials=credentials, virtual_host='gova11y'))
        logger.debug('Connected to RabbitMQ server!')

        logger.debug(f'Declaring queue: {queue_name}...')
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True, arguments={'x-message-ttl': 7200000})
        logger.debug(f'Queue {queue_name} declared!')

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make the messages persistent
        )
        logger.info(f'Message sent to queue {queue_name}: {message}')
    except Exception as e:
        logger.error(f"Error sending message to RabbitMQ: {e}")
    finally:
        try:
            channel.close()
            connection.close()
            logger.debug('RabbitMQ connection closed')
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")

# Catching Rabbits
def catch_rabbits(queue_name, process_func):
    try:
        logger.debug('Connecting to RabbitMQ server...')
        credentials = pika.PlainCredentials('rabbit_hole', 'lets_insert_things')
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', credentials=credentials, virtual_host='gova11y'))
        logger.debug('Connected to RabbitMQ server!')

        logger.debug(f'Declaring queue: {queue_name}...')
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True, arguments={'x-message-ttl': 7200000})
        logger.debug(f'Queue {queue_name} declared!')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=process_func,
            auto_ack=False
        )
        logger.info(f'🐇 [*] Waiting for messages in {queue_name}. To exit press CTRL+C')

        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in catch_rabbits function: {e}")
    finally:
        try:
            channel.stop_consuming()
            connection.close()
            logger.debug('RabbitMQ connection closed')
        except Exception as e:
            logger.error(f"Error stopping consumer and closing RabbitMQ connection: {e}")
