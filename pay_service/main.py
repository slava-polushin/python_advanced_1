import asyncio

from functools import partial

import aio_pika
from aio_pika  import ExchangeType

import json

from app.config import RABBITMQ_URL, CELERY_BROKER_URL, MAIN_SERVICE_URL
from app.rabbitmq_client import APP_QUEUE_MAP, EXCHANGE_NAME

from celery.app import Celery

async def process_pay_message(
        message: aio_pika.IncomingMessage,
        channel: aio_pika.RobustChannel
        ):
    async with message.process():
        body = message.body.decode("utf-8")
        data = json.loads(body)
        order_status = data['order_status']
        pay_sum = data['pay_sum']

        print(f"Received message: {order_status}")
        print(f"Received pay_sum: {pay_sum}")        
        
        #TODO: Реализовать сервис оплаты, в текущей (тестовой) реализации считается что оплата проведена

        if pay_sum: 
            import requests
            
            new_paying = {
                "order_id": order_status['order_id'],
                "pay_sum": pay_sum,
            }
            response = requests.post(f"{MAIN_SERVICE_URL}/pay_accepted", json=new_paying)
            
            print(f"Pay acceptation request processed: {response.json()}")

async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Define the queues to consume from
    for queue_name in (
        APP_QUEUE_MAP["pay_request_queue"],
        ):
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.consume(partial(process_pay_message,channel=channel))

    print(" [*] Waiting for messages. To exit press CTRL+C")
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())