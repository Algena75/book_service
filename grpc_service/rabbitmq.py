import asyncio
import logging
import os.path
import sys
from logging.handlers import RotatingFileHandler
import time
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

from config import settings as st

dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
log_file = os.path.join(dirname, 'reports/log_file.log')

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()
handler = RotatingFileHandler(log_file, maxBytes=1000, backupCount=5)

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
    url = (f"amqp://{st.RABBITMQ_USER}:{st.RABBITMQ_PASSWORD}@"
           f"{st.RABBITMQ_HOST}:{st.RABBITMQ_PORT}/")
    for i in range(1, 11):
        try:
            connection = await connect(url=url)
        except:
            logger.info(f'{i} попытка подключения к брокеру.')
            time.sleep(5)
            continue
        else:
            break
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
    except:
        logging.error('Брокер недоступен.')


def main():
    asyncio.run(message_receiver())


if __name__ == '__main__':
    main()
