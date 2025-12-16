from unittest.mock import AsyncMock, patch

import pytest

from rmq_client import RMQClient, RMQConfig


@pytest.fixture
def client():
    return RMQClient(RMQConfig())


class TestRMQClient:
    async def test_is_connected_false_initially(self, client) -> None:
        assert await client.is_connected() is False

    async def test_is_connected_true_after_connect(self, client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False

        with patch('aio_pika.connect_robust', return_value=mock_conn):
            mock_conn.channel = AsyncMock(return_value=mock_channel)
            await client.connect()
            assert await client.is_connected() is True

    async def test_connect_retry_on_failure(self, client) -> None:
        client._config = RMQConfig(max_retries=2, retry_base_delay=0.01)
        call_count = 0

        async def failing_connect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                msg = 'Test failure'
                raise ConnectionError(msg)
            mock = AsyncMock()
            mock.is_closed = False
            mock.channel = AsyncMock(return_value=AsyncMock(is_closed=False))
            return mock

        with patch('aio_pika.connect_robust', side_effect=failing_connect):
            await client.connect()
            assert call_count == 2

    async def test_close_cleans_up(self, client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn):
            await client.connect()
            await client.close()
            mock_channel.close.assert_called_once()
            mock_conn.close.assert_called_once()

    async def test_context_manager(self, client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn):
            async with client:
                assert await client.is_connected()
            mock_conn.close.assert_called()

    async def test_publish_ensures_connection(self, client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_channel.default_exchange = AsyncMock()
        mock_queue = AsyncMock()
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn):
            await client.publish(b'test', routing_key='test_queue')
            mock_channel.default_exchange.publish.assert_called_once()
