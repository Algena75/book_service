import asyncio

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from config import settings as st
from services import logger, retry


async def on_message(message: AbstractIncomingMessage) -> None:
    """
    Функция обработки сообщений брокера.
    """
    logger.info(message.body.decode(encoding='utf-8'))


@retry(exc_list=[ConnectionError,], times=10, delay=5)
async def message_receiver() -> None:
    """
    Запускает прослушивание сообщений от брокера.
    """
    url = (f"amqp://{st.RABBITMQ_USER}:{st.RABBITMQ_PASSWORD}@"
           f"{st.RABBITMQ_HOST}:{st.RABBITMQ_PORT}/")
    try:
        connection = await connect(url=url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(st.RABBITMQ_QUEUE)
            await queue.consume(on_message, no_ack=True)
            logger.info(
                " [*] Waiting for messages. To exit press CTRL+C (twice)"
            )
            await asyncio.Future()
    except ConnectionError as e:
        logger.error('Брокер недоступен.')
        raise ConnectionError(e)


def main():
    asyncio.run(message_receiver())


if __name__ == '__main__':
    main()
