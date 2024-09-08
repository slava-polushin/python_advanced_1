import json
import time

import pika
from pika.exchange_type import ExchangeType

from app.config import RABBITMQ_URL, RABBITMQ_RECONNECT_PAUSE, RABBITMQ_RECONNECT_COUNT

# Define a mapping between service_id and queue names
APP_QUEUE_MAP = {
    "pay_request_queue": "pay_request_queue",
    "pay_approve_queue": "pay_approve_queue",
}

EXCHANGE_NAME = "taxi_exchange"


class RabbitMQConnectionError(Exception):
    pass


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.retry_count = 0

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(RABBITMQ_URL))
        self.channel = self.connection.channel()
        # Declare exchange & queues

        self.channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=ExchangeType.direct,
            durable=True
        )

        for queue_name in APP_QUEUE_MAP.values():
            self.channel.queue_declare(queue_name, durable=True)
            # binding for publishing
            self.channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=queue_name,
                routing_key=queue_name
            )

    def publish(self, routing_key: str, message: dict):
        if self.retry_count > RABBITMQ_RECONNECT_COUNT:
            raise RabbitMQConnectionError(
                f"No connection after {self.retry_count} attempts"
            )
        try:
            message_body = json.dumps(
                message, sort_keys=True, indent=4, default=str).encode("utf-8")
            self.channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            self.retry_count = 0
        except pika.exceptions.StreamLostError:
            time.sleep(RABBITMQ_RECONNECT_PAUSE)
            self.connect()
            self.retry_count += 1
            self.publish(routing_key, message)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


# Create a global RabbitMQClient instance
rabbitmq_client = RabbitMQClient()
