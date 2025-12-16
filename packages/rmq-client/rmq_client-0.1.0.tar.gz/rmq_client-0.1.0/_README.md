# RMQ Client

Robust async/sync RabbitMQ client with automatic retry and connection recovery.

## Features

- **Async-first** with sync wrapper
- **Auto-recovery** with exponential backoff + jitter
- **Smart defaults** (durable queues, persistent messages, prefetch)
- **Unified API** for publish/consume
- **Comprehensive logging**

## Installation

```bash
pip install rmq-client
```

## Quick Start

### Async

```python
import asyncio
from rmq_client import RMQClient, RMQConfig

async def main():
    config = RMQConfig(host="localhost", prefetch_count=10)

    async with RMQClient(config) as client:
        # Declare queue
        await client.declare_queue(name="my_queue")

        # Publish
        await client.publish(b"Hello!", routing_key="my_queue")

        # Consume
        async def handler(msg):
            print(f"Received: {msg.body.decode()}")

        await client.consume("my_queue", handler)
        await asyncio.sleep(5)

asyncio.run(main())
```

### Sync

```python
from rmq_client import SyncRMQClient, RMQConfig

with SyncRMQClient(RMQConfig()) as client:
    client.declare_queue(name="my_queue")
    client.publish(b"Hello sync!", routing_key="my_queue")

    def handler(msg):
        print(f"Got: {msg.body.decode()}")

    client.consume("my_queue", handler)
```

## Configuration

```python
from rmq_client import RMQConfig, ExchangeConfig, QueueConfig
from aio_pika import ExchangeType

config = RMQConfig(
    host="rabbit.example.com",
    port=5672,
    login="user",
    password="secret",
    virtualhost="/prod",
    ssl=True,
    max_retries=5,
    retry_base_delay=1.0,
    retry_max_delay=60.0,
    prefetch_count=20,
)

exchange_cfg = ExchangeConfig(
    name="events",
    type=ExchangeType.TOPIC,
    durable=True,
)

queue_cfg = QueueConfig(
    name="notifications",
    durable=True,
    arguments={"x-message-ttl": 86400000},
)
```

## Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("rmq_client").setLevel(logging.DEBUG)
```

## License

MIT
