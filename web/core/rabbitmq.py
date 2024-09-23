import asyncio
import logging

from aio_pika import Message, connect

from web.core.config import settings as st


async def send_message_to_broker(text: str) -> None:
    try:
        connection = await connect(host=st.RABBITMQ_HOST, port=st.RABBITMQ_PORT,
                                   login=st.RABBITMQ_USER,
                                   password=st.RABBITMQ_PASSWORD)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(st.RABBITMQ_QUEUE)
            message = Message(text.encode(encoding='utf-8'))
            await channel.default_exchange.publish(
                message,
                routing_key=queue.name,
            )
            logging.info(f" [x] Sent '{text}'")
    except:
        logging.error('Брокер недоступен.')


if __name__ == '__main__':
    asyncio.run(send_message_to_broker('test message'))
