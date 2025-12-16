import asyncio
import os

import pytest
from aio_pika import ExchangeType

from rmq_client import RMQClient, RMQConfig, SyncRMQClient


pytestmark = pytest.mark.e2e

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))


@pytest.fixture
def config():
    return RMQConfig(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        max_retries=3,
        retry_base_delay=0.5,
    )


@pytest.fixture
async def async_client(config):
    client = RMQClient(config)
    yield client
    await client.close()


@pytest.fixture
def sync_client(config):
    client = SyncRMQClient(config)
    yield client
    client.close()


class TestAsyncIntegration:
    async def test_connect_disconnect(self, async_client) -> None:
        await async_client.connect()
        assert await async_client.is_connected()
        await async_client.close()
        assert not await async_client.is_connected()

    async def test_declare_queue(self, async_client) -> None:
        async with async_client:
            queue = await async_client.declare_queue(name='test_queue_declare')
            assert queue is not None

    async def test_declare_exchange(self, async_client) -> None:
        async with async_client:
            exchange = await async_client.declare_exchange(
                name='test_exchange',
                type=ExchangeType.TOPIC,
            )
            assert exchange is not None

    async def test_publish_consume(self, async_client) -> None:
        messages = []

        async def handler(msg) -> None:
            messages.append(msg.body.decode())

        async with async_client:
            queue_name = 'test_pub_consume'
            await async_client.declare_queue(name=queue_name)
            await async_client.consume(queue_name, handler)
            await async_client.publish(b'Hello RabbitMQ!', routing_key=queue_name)

            # Wait for message
            for _ in range(50):
                if messages:
                    break
                await asyncio.sleep(0.1)

            assert 'Hello RabbitMQ!' in messages

    async def test_exchange_routing(self, async_client) -> None:
        messages = []

        async def handler(msg) -> None:
            messages.append(msg.body.decode())

        async with async_client:
            await async_client.declare_exchange(name='test_topic', type=ExchangeType.TOPIC)
            await async_client.declare_queue(name='test_topic_queue')
            await async_client.bind_queue('test_topic_queue', 'test_topic', 'test.#')
            await async_client.consume('test_topic_queue', handler)
            await async_client.publish(
                b'Topic message',
                routing_key='test.routing',
                exchange_name='test_topic',
            )

            for _ in range(50):
                if messages:
                    break
                await asyncio.sleep(0.1)

            assert 'Topic message' in messages

    async def test_message_acknowledgement(self, async_client) -> None:
        processed = []

        async def handler(msg) -> None:
            processed.append(msg.body.decode())
            # Message auto-acked by wrapper when handler succeeds

        async with async_client:
            queue_name = 'test_ack_queue'
            await async_client.declare_queue(name=queue_name)
            await async_client.consume(queue_name, handler)
            await async_client.publish(b'Ack test', routing_key=queue_name)

            for _ in range(50):
                if processed:
                    break
                await asyncio.sleep(0.1)

            assert 'Ack test' in processed


class TestSyncIntegration:
    def test_connect_disconnect(self, sync_client) -> None:
        sync_client.connect()
        assert sync_client.is_connected()
        sync_client.close()

    def test_publish_consume(self, sync_client) -> None:
        messages = []

        def handler(msg) -> None:
            messages.append(msg.body.decode())

        with sync_client:
            queue_name = 'test_sync_pub_consume'
            sync_client.declare_queue(name=queue_name)
            sync_client.consume(queue_name, handler)
            sync_client.publish(b'Sync Hello!', routing_key=queue_name)

            import time

            for _ in range(50):
                if messages:
                    break
                time.sleep(0.1)

            assert 'Sync Hello!' in messages


class TestRetryMechanisms:
    async def test_connection_recovery(self, config) -> None:
        client = RMQClient(config)
        await client.connect()

        # Simulate disconnect
        if client._connection:
            await client._connection.close()

        # Should auto-reconnect on next operation
        await client.publish(b'After recovery', routing_key='recovery_test')
        assert await client.is_connected()
        await client.close()
