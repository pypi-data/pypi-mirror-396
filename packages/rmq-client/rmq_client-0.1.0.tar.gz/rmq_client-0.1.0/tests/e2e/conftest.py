import asyncio

import pytest


def pytest_configure(config) -> None:
    config.addinivalue_line('markers', 'e2e: end-to-end tests requiring RabbitMQ')


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
