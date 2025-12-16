import logging
import random
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from aio_pika.exceptions import AMQPConnectionError, AMQPError
from tenacity import (
    RetryCallState,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


logger = logging.getLogger(__name__)
T = TypeVar('T')


def add_jitter(retry_state: RetryCallState) -> float:
    """Add jitter to wait time."""
    exp_wait = wait_exponential(multiplier=1, min=1, max=60)
    base = exp_wait(retry_state)
    return base + random.uniform(0, base * 0.1)


def create_retry_decorator(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    use_jitter: bool = True,
):
    """Create configured retry decorator."""
    wait_strategy = (
        wait_exponential(multiplier=base_delay, min=base_delay, max=max_delay) if not use_jitter else add_jitter
    )
    return retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_strategy,
        retry=retry_if_exception_type((AMQPError, AMQPConnectionError, ConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def with_connection_check(method: Callable[..., T]) -> Callable[..., T]:
    """Decorator ensuring connection is alive before operation."""

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not await self.is_connected():
            logger.info('Connection lost, reconnecting...')
            await self.connect()
        return await method(self, *args, **kwargs)

    return wrapper
