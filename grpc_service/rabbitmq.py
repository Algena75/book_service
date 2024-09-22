import asyncio
import logging
import os.path
import sys
from logging.handlers import RotatingFileHandler

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

from grpc_service.config import settings as st

dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
log_file = os.path.join(dirname, f'logs/log_file.log')

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()
handler = logging.handlers.RotatingFileHandler(
              log_file, maxBytes=1000, backupCount=5)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)


async def on_message(message: AbstractIncomingMessage) -> None:
    """
    Функция обработки сообщений брокера.
    """
    logger.info(message.body.decode(encoding='utf-8'))


async def message_receiver() -> None:
    """
    Запускает прослушивание сообщений от брокера.
    """
    connection = await connect(host=st.RABBITMQ_HOST, port=st.RABBITMQ_PORT,
                               login=st.RABBITMQ_USER,
                               password=st.RABBITMQ_PASSWORD)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(st.RABBITMQ_QUEUE)

        await queue.consume(on_message, no_ack=True)

        logger.info(" [*] Waiting for messages. To exit press CTRL+C (twice)")
        await asyncio.Future()


def main():
    asyncio.run(message_receiver())


if __name__ == '__main__':
    main()
