class RMQError(Exception):
    """Base exception for RMQ client."""


class RMQConnectionError(RMQError):
    """Connection-related errors."""


class RMQPublishError(RMQError):
    """Message publishing errors."""


class RMQConsumeError(RMQError):
    """Message consumption errors."""
