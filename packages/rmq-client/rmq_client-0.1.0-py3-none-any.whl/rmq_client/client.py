import asyncio
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

from .config import ExchangeConfig, QueueConfig, RMQConfig
from .exceptions import RMQConnectionError, RMQConsumeError, RMQPublishError
from .retry import create_retry_decorator, with_connection_check


logger = logging.getLogger(__name__)

MessageHandler = Callable[[AbstractIncomingMessage], Any]


class RMQClient:
    """Async RabbitMQ client with auto-recovery and retry mechanisms."""

    def __init__(self, config: RMQConfig | None = None) -> None:
        self.config = config or RMQConfig()
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._exchanges: dict[str, AbstractExchange] = {}
        self._queues: dict[str, AbstractQueue] = {}
        self._consumer_tags: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._retry = create_retry_decorator(
            max_retries=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            max_delay=self.config.retry_max_delay,
            use_jitter=self.config.retry_jitter,
        )

    async def is_connected(self) -> bool:
        """Check if connection and channel are alive."""
        return (
            self._connection is not None
            and not self._connection.is_closed
            and self._channel is not None
            and not self._channel.is_closed
        )

    async def connect(self) -> None:
        """Establish connection with retry logic."""
        async with self._lock:
            if await self.is_connected():
                return
            await self._connect_with_retry()

    async def _connect_with_retry(self) -> None:
        @self._retry
        async def _do_connect() -> None:
            logger.info(f'Connecting to RabbitMQ at {self.config.host}:{self.config.port}')
            self._connection = await aio_pika.connect_robust(
                self.config.url,
                timeout=self.config.connection_timeout,
                heartbeat=self.config.heartbeat,
            )
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=self.config.prefetch_count)
            self._exchanges.clear()
            self._queues.clear()
            logger.info('Connected to RabbitMQ successfully')

        try:
            await _do_connect()
        except Exception as e:
            msg = f'Failed to connect: {e}'
            raise RMQConnectionError(msg) from e

    async def close(self) -> None:
        """Close connection gracefully."""
        async with self._lock:
            for tag in list(self._consumer_tags.values()):
                try:
                    if self._channel and not self._channel.is_closed:
                        await self._channel.cancel(tag)
                except Exception as e:
                    logger.warning(f'Error canceling consumer {tag}: {e}')
            self._consumer_tags.clear()

            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            self._channel = None
            self._connection = None
            self._exchanges.clear()
            self._queues.clear()
            logger.info('Disconnected from RabbitMQ')

    async def __aenter__(self) -> 'RMQClient':
        await self.connect()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    @with_connection_check
    async def declare_exchange(
        self,
        config: ExchangeConfig | None = None,
        **kwargs,
    ) -> AbstractExchange:
        """Declare an exchange."""
        cfg = config or ExchangeConfig(**kwargs)
        if cfg.name in self._exchanges:
            return self._exchanges[cfg.name]

        exchange = await self._channel.declare_exchange(
            name=cfg.name,
            type=cfg.type,
            durable=cfg.durable,
            auto_delete=cfg.auto_delete,
        )
        self._exchanges[cfg.name] = exchange
        logger.debug(f'Declared exchange: {cfg.name}')
        return exchange

    @with_connection_check
    async def declare_queue(
        self,
        config: QueueConfig | None = None,
        **kwargs,
    ) -> AbstractQueue:
        """Declare a queue."""
        cfg = config or QueueConfig(**kwargs)
        if cfg.name in self._queues:
            return self._queues[cfg.name]

        queue = await self._channel.declare_queue(
            name=cfg.name or '',
            durable=cfg.durable,
            exclusive=cfg.exclusive,
            auto_delete=cfg.auto_delete,
            arguments=cfg.arguments,
        )
        self._queues[cfg.name or queue.name] = queue
        logger.debug(f'Declared queue: {cfg.name or queue.name}')
        return queue

    @with_connection_check
    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = '',
    ) -> None:
        """Bind queue to exchange."""
        queue = self._queues.get(queue_name)
        if not queue:
            msg = f'Queue {queue_name} not declared'
            raise RMQPublishError(msg)
        await queue.bind(exchange_name, routing_key)
        logger.debug(f'Bound {queue_name} to {exchange_name} with key {routing_key}')

    async def publish(
        self,
        body: bytes | str,
        routing_key: str = '',
        exchange_name: str = '',
        *,
        headers: dict | None = None,
        content_type: str | None = None,
        correlation_id: str | None = None,
        reply_to: str | None = None,
        expiration: int | None = None,
        message_id: str | None = None,
        priority: int | None = None,
        delivery_mode: DeliveryMode | None = None,
    ) -> None:
        """Publish message with automatic retry and connection recovery."""

        @self._retry
        async def _do_publish() -> None:
            await self._ensure_publish_ready(exchange_name, routing_key)

            msg_body = body.encode() if isinstance(body, str) else body
            message = Message(
                body=msg_body,
                headers=headers,
                content_type=content_type,
                correlation_id=correlation_id,
                reply_to=reply_to,
                expiration=expiration,
                message_id=message_id,
                priority=priority,
                delivery_mode=delivery_mode or self.config.delivery_mode,
            )

            exchange = self._exchanges.get(exchange_name) or self._channel.default_exchange
            await exchange.publish(message, routing_key=routing_key)
            logger.debug(f'Published to {exchange_name or "default"}:{routing_key}')

        try:
            await _do_publish()
        except Exception as e:
            msg = f'Failed to publish: {e}'
            raise RMQPublishError(msg) from e

    async def _ensure_publish_ready(self, exchange_name: str, routing_key: str) -> None:
        """Ensure connection, channel, exchange, and queue exist."""
        if not await self.is_connected():
            await self.connect()

        if exchange_name and exchange_name not in self._exchanges:
            await self.declare_exchange(name=exchange_name)

        # For default exchange, ensure queue exists
        if not exchange_name and routing_key and routing_key not in self._queues:
            await self.declare_queue(name=routing_key)

    async def consume(
        self,
        queue_name: str,
        handler: MessageHandler,
        *,
        no_ack: bool = False,
        exclusive: bool = False,
        auto_declare: bool = True,
    ) -> str:
        """Start consuming from queue. Returns consumer tag."""

        @self._retry
        async def _do_consume() -> str:
            if not await self.is_connected():
                await self.connect()

            if auto_declare and queue_name not in self._queues:
                await self.declare_queue(name=queue_name)

            queue = self._queues.get(queue_name)
            if not queue:
                msg = f'Queue {queue_name} not found'
                raise RMQConsumeError(msg)

            async def _wrapped_handler(message: AbstractIncomingMessage) -> None:
                try:
                    result = handler(message)
                    if asyncio.iscoroutine(result):
                        await result
                    if not no_ack:
                        await message.ack()
                except Exception as e:
                    logger.exception(f'Handler error: {e}')
                    if not no_ack:
                        await message.nack(requeue=True)

            tag = await queue.consume(_wrapped_handler, no_ack=no_ack, exclusive=exclusive)
            self._consumer_tags[queue_name] = tag
            logger.info(f'Started consuming from {queue_name}')
            return tag

        try:
            return await _do_consume()
        except Exception as e:
            msg = f'Failed to consume: {e}'
            raise RMQConsumeError(msg) from e

    async def cancel_consumer(self, queue_name: str) -> None:
        """Cancel consumer for queue."""
        tag = self._consumer_tags.pop(queue_name, None)
        if tag and self._channel and not self._channel.is_closed:
            await self._channel.cancel(tag)
            logger.info(f'Cancelled consumer for {queue_name}')

    @asynccontextmanager
    async def consume_context(
        self,
        queue_name: str,
        handler: MessageHandler,
        **kwargs,
    ):
        """Context manager for consuming."""
        tag = await self.consume(queue_name, handler, **kwargs)
        try:
            yield tag
        finally:
            await self.cancel_consumer(queue_name)
