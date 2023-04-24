import os
import threading
from flask import Flask, jsonify, Response
from utils.auth import catch_rabbits
from utils.watch import logger
from prometheus_client import Counter, Histogram, generate_latest


app = Flask(__name__)

# Define a global variable to control the RabbitMQ consumer loop
stop_consumer = threading.Event()


def rabbitmq_consumer():
    def callback(ch, method, properties, body):
        # Process the message
        logger.debug(f"Received message: {body}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    while not stop_consumer.is_set():
        try:
            catch_rabbits("your_queue_name", callback)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error in the RabbitMQ consumer: {e}")


# Thread to run the RabbitMQ consumer
consumer_thread = threading.Thread(target=rabbitmq_consumer, daemon=True)


@app.route('/start')
def start():
    logger.debug('Waking up...')
    if not consumer_thread.is_alive():
        stop_consumer.clear()
        consumer_thread.start()
    return jsonify({'message': 'Started listening to the RabbitMQ queue'})


@app.route('/stop')
def stop():
    logger.info('Stop request received...')
    stop_consumer.set()
    return jsonify({'message': 'Stopped listening to the RabbitMQ queue'})


@app.route('/')
def standby():
    return jsonify({'message': 'Welcome to the Rabbit Hole!'})


@app.route('/health')
def health_check():
    return jsonify({'status': 'UP'}), 200


@app.route('/status')
def get_status():
    # This application gets the current application status
    pass


# Prometheus
# Define metrics
REQUESTS = Counter('requests_total', 'Total number of requests')
LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')


@app.route('/metrics')
def metrics():
    # Collect and return the metrics as a Prometheus-formatted response
    response = Response(generate_latest(), mimetype='text/plain')
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


if __name__ == '__main__':
    # Get the port number from the environment variable or use 8083 as default
    app_port = int(os.environ.get('APP_PORT', 8084))
    standby()
    app.run(debug=True, host='0.0.0.0', port=app_port)
