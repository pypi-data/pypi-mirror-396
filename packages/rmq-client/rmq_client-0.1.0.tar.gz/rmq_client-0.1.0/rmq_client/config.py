from dataclasses import dataclass, field

from aio_pika import DeliveryMode, ExchangeType


@dataclass
class ExchangeConfig:
    """Exchange configuration with production-ready defaults."""

    name: str = ''
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = True
    auto_delete: bool = False


@dataclass
class QueueConfig:
    """Queue configuration with production-ready defaults."""

    name: str = ''
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: dict = field(default_factory=dict)


@dataclass
class RMQConfig:
    """Main RabbitMQ client configuration."""

    host: str = 'localhost'
    port: int = 5672
    login: str = 'guest'
    password: str = 'guest'
    virtualhost: str = '/'
    ssl: bool = False
    # Retry settings
    max_retries: int = 5
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_jitter: bool = True
    # Message defaults
    delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    prefetch_count: int = 10
    # Timeouts
    connection_timeout: float = 30.0
    heartbeat: int = 60

    @property
    def url(self) -> str:
        proto = 'amqps' if self.ssl else 'amqp'
        return f'{proto}://{self.login}:{self.password}@{self.host}:{self.port}/{self.virtualhost}'
