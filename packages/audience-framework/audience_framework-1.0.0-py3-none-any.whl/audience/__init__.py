"""
audience — фреймворк для написания на Python асинхронных микросервисов поверх AMQP.
"""

from .app import Audience
from .exceptions import (
    AudienceError,
    ConfigurationError,
    ConnectionError,
    HandlerError,
    ValidationError,
    SerializationError,
    TimeoutError,
    QueueError
)

__all__ = [
    'Audience',
    'AudienceError',
    'ConfigurationError',
    'ConnectionError',
    'HandlerError',
    'ValidationError',
    'SerializationError',
    'TimeoutError',
    'QueueError',
]

__version__ = "0.1.0"
