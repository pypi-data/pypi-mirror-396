from aio_pika import DeliveryMode, ExchangeType

from rmq_client.config import ExchangeConfig, QueueConfig, RMQConfig


class TestRMQConfig:
    def test_defaults(self) -> None:
        cfg = RMQConfig()
        assert cfg.host == 'localhost'
        assert cfg.port == 5672
        assert cfg.durable if hasattr(cfg, 'durable') else True
        assert cfg.delivery_mode == DeliveryMode.PERSISTENT

    def test_url_generation(self) -> None:
        cfg = RMQConfig(host='rabbit.local', port=5673, login='user', password='pass')
        assert cfg.url == 'amqp://user:pass@rabbit.local:5673/'

    def test_ssl_url(self) -> None:
        cfg = RMQConfig(ssl=True)
        assert cfg.url.startswith('amqps://')


class TestExchangeConfig:
    def test_defaults(self) -> None:
        cfg = ExchangeConfig()
        assert cfg.durable is True
        assert cfg.type == ExchangeType.DIRECT
        assert cfg.auto_delete is False


class TestQueueConfig:
    def test_defaults(self) -> None:
        cfg = QueueConfig()
        assert cfg.durable is True
        assert cfg.exclusive is False
        assert cfg.auto_delete is False
