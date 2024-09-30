import asyncio
import logging
import os.path
import sys
import time
from contextlib import contextmanager
from functools import wraps
from logging.handlers import RotatingFileHandler
from time import sleep
from typing import Any

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


def retry(times: int = 3,
          delay: int = 1,
          exc_list: list = [Exception, ]) -> Any:
    exc_list = tuple(exc_list)

    def inner_decorator(func, *args, **kwargs):

        @contextmanager
        def wrapping_logic():
            start_ts = time.time()
            yield
            dur = time.time() - start_ts
            print('{} took {:.2} seconds'.format(func.__name__, dur))

        @wraps(func)
        async def wrapper(*args, **kwargs):
            er_msg: Exception = None
            for i in range(1, times + 1):
                logger.info(f'{func.__name__} - {i} попытка подключения.')
                try:
                    if not asyncio.iscoroutinefunction(func):
                        with wrapping_logic():
                            return func(*args, **kwargs)
                    else:
                        with wrapping_logic():
                            return (await func(*args, **kwargs))
                except exc_list as e:
                    er_msg = e
                    sleep(delay)
            return logger.error(er_msg)
        return wrapper
    return inner_decorator
