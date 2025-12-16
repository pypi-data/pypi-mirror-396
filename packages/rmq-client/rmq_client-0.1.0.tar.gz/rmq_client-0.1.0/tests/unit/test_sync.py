from unittest.mock import AsyncMock, patch

import pytest

from rmq_client import RMQConfig, SyncRMQClient


@pytest.fixture
def sync_client():
    return SyncRMQClient(RMQConfig())


class TestSyncRMQClient:
    def test_connect_and_close(self, sync_client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn):
            sync_client.connect()
            assert sync_client.is_connected()
            sync_client.close()

    def test_context_manager(self, sync_client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn), sync_client:
            assert sync_client.is_connected()

    def test_publish(self, sync_client) -> None:
        mock_conn = AsyncMock()
        mock_conn.is_closed = False
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_channel.default_exchange = AsyncMock()
        mock_queue = AsyncMock()
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        with patch('aio_pika.connect_robust', return_value=mock_conn), sync_client:
            sync_client.publish(b'test message', routing_key='test')
            mock_channel.default_exchange.publish.assert_called_once()
