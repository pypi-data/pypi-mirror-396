import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from aio_pika.abc import AbstractExchange, AbstractIncomingMessage, AbstractQueue

from .client import RMQClient
from .config import ExchangeConfig, QueueConfig, RMQConfig


def _run_sync(coro):
    """Run coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside async context - use thread
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


class SyncRMQClient:
    """Synchronous wrapper around async RMQClient."""

    def __init__(self, config: RMQConfig | None = None) -> None:
        self._async_client = RMQClient(config)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._consumer_running = threading.Event()

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop for sync operations."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    def _run(self, coro):
        """Run coroutine in managed loop."""
        loop = self._ensure_loop()
        return loop.run_until_complete(coro)

    @property
    def config(self) -> RMQConfig:
        return self._async_client.config

    def is_connected(self) -> bool:
        return self._run(self._async_client.is_connected())

    def connect(self) -> None:
        self._run(self._async_client.connect())

    def close(self) -> None:
        self._consumer_running.clear()
        self._run(self._async_client.close())
        if self._loop and not self._loop.is_closed():
            self._loop.close()
        self._loop = None

    def __enter__(self) -> 'SyncRMQClient':
        self.connect()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def declare_exchange(
        self,
        config: ExchangeConfig | None = None,
        **kwargs,
    ) -> AbstractExchange:
        return self._run(self._async_client.declare_exchange(config, **kwargs))

    def declare_queue(
        self,
        config: QueueConfig | None = None,
        **kwargs,
    ) -> AbstractQueue:
        return self._run(self._async_client.declare_queue(config, **kwargs))

    def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = '',
    ) -> None:
        self._run(self._async_client.bind_queue(queue_name, exchange_name, routing_key))

    def publish(
        self,
        body: bytes | str,
        routing_key: str = '',
        exchange_name: str = '',
        **kwargs,
    ) -> None:
        self._run(self._async_client.publish(body, routing_key, exchange_name, **kwargs))

    def consume(
        self,
        queue_name: str,
        handler: Callable[[AbstractIncomingMessage], Any],
        *,
        no_ack: bool = False,
        exclusive: bool = False,
        auto_declare: bool = True,
    ) -> str:
        """Start consuming. Handler can be sync or async."""

        def sync_wrapper(msg: AbstractIncomingMessage):
            result = handler(msg)
            if asyncio.iscoroutine(result):
                return self._run(result)
            return result

        return self._run(
            self._async_client.consume(
                queue_name,
                sync_wrapper,
                no_ack=no_ack,
                exclusive=exclusive,
                auto_declare=auto_declare,
            )
        )

    def consume_forever(
        self,
        queue_name: str,
        handler: Callable[[AbstractIncomingMessage], Any],
        **kwargs,
    ) -> None:
        """Block and consume messages until interrupted or close() called."""
        self._consumer_running.set()
        self.consume(queue_name, handler, **kwargs)

        try:
            while self._consumer_running.is_set():
                self._run(asyncio.sleep(0.1))
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    def cancel_consumer(self, queue_name: str) -> None:
        self._run(self._async_client.cancel_consumer(queue_name))
