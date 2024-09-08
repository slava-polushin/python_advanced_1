import asyncio

from functools import partial

import aio_pika
from aio_pika  import ExchangeType

import json

from app.config import RABBITMQ_URL
from app.rabbitmq_client import APP_QUEUE_MAP, EXCHANGE_NAME


async def process_pay_message(
        message: aio_pika.IncomingMessage,
        channel: aio_pika.RobustChannel
        ):
    async with message.process():
        body = message.body.decode("utf-8")
        data = json.loads(body)
        order_status = data['order_status']
        pay_sum = data['pay_sum']
        # Process the data here
        print(f"Received message: {order_status}")
        print(f"Received pay_sum: {pay_sum}")
        
        #TODO: Реализовать вервис оплаты, в текущей (тестовой) реализации считается что оплата проведена
        producer_queue_name = APP_QUEUE_MAP["pay_approve_queue"]
        producer_queue = await channel.declare_queue(producer_queue_name, durable=True)

        if pay_sum:
            # отправляем ответ в exchange с ключом "pay_approve_queue"
            exch = await channel.declare_exchange(
                name=EXCHANGE_NAME,
                type=ExchangeType.DIRECT,
                durable=True 
            )

            out_message = {"order_status": order_status, "accepted_sum": pay_sum}

            message_body = json.dumps(out_message, sort_keys=True, indent=4, default=str).encode("utf-8")

            await exch.publish(
                message=aio_pika.Message(body=message_body),
                routing_key=producer_queue_name
            )

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