from functools import wraps
from asyncio import sleep

from typing import (
    Awaitable,
    Callable,
    TypeVar,
    Any,
)

from loguru import logger

R = TypeVar('R')


def retry(retries: int = 2, delay: int = 30, backoff: float = 1.5) -> Callable:
    def decorator_retry(func: Callable[..., Awaitable[R]]) -> Callable:
        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> R:
            for i in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as ex:
                    if i == retries:
                        if '502' in str(ex):
                            logger.error('Client failed with code 502')
                        logger.error(ex)
                        return
                    else:
                        await sleep(delay * (backoff ** i))

        return wrapped

    return decorator_retry
