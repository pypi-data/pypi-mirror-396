from typing import NoReturn

import pytest

from rmq_client.retry import create_retry_decorator, with_connection_check


class TestRetryDecorator:
    async def test_retry_on_connection_error(self) -> None:
        call_count = 0
        decorator = create_retry_decorator(max_retries=3, base_delay=0.01)

        @decorator
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                msg = 'Transient error'
                raise ConnectionError(msg)
            return 'success'

        result = await flaky_func()
        assert result == 'success'
        assert call_count == 2

    async def test_max_retries_exceeded(self) -> None:
        decorator = create_retry_decorator(max_retries=2, base_delay=0.01)
        call_count = 0

        @decorator
        async def always_fails() -> NoReturn:
            nonlocal call_count
            call_count += 1
            msg = 'Persistent error'
            raise ConnectionError(msg)

        with pytest.raises(ConnectionError):
            await always_fails()
        assert call_count == 2


class TestConnectionCheck:
    async def test_reconnects_if_disconnected(self) -> None:
        class MockClient:
            def __init__(self) -> None:
                self.connected = False
                self.connect_called = False

            async def is_connected(self):
                return self.connected

            async def connect(self) -> None:
                self.connect_called = True
                self.connected = True

            @with_connection_check
            async def do_something(self) -> str:
                return 'done'

        client = MockClient()
        result = await client.do_something()
        assert result == 'done'
        assert client.connect_called
