import inspect
import warnings
from typing import (
    Callable, 
    Optional
)
from functools import wraps

from .exceptions import ConfigurationError


class QueueBinding:
    """Метаданные привязки обработчика к очереди."""
    __slots__ = ('queue_name', 'exchange', 'routing_key', 'options')
    
    def __init__(
        self, 
        queue_name: str, 
        exchange: Optional[str] = None,
        routing_key: Optional[str] = None,
        **options
    ):
        self.queue_name = queue_name
        self.exchange = exchange
        self.routing_key = routing_key or queue_name
        self.options = options or {}


class RPCHandler:
    """Метаданные RPC-обработчика."""
    __slots__ = ('queue_name', 'timeout', 'options')
    
    def __init__(
        self, 
        queue_name: str, 
        timeout: float = 30.0, 
        **options
    ):
        self.queue_name = queue_name
        self.timeout = timeout
        self.options = options


def queue(queue_name: str, 
          exchange: Optional[str] = None,
          routing_key: Optional[str] = None,
          **kwargs) -> Callable:
    """
    Декоратор для регистрации обработчика очереди.
    
    Args:
        queue_name: Имя очереди
        exchange: Обменник (если не указан, используется default)
        routing_key: Ключ маршрутизации (по умолчанию = queue_name)
        **kwargs: Доп. параметры для queue_declare (durable, exclusive и т.д.)
    
    Example:
        @queue("orders.created", exchange="events", durable=True)
        async def handle_order(msg):
            ...
    """
    def decorator(func: Callable) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise ConfigurationError(
                f"Handler '{func.__name__}' have to be an async function."
                f"Got: {func.__name__}"
            )
        
        binding = QueueBinding(
            queue_name=queue_name,
            exchange=exchange,
            routing_key=routing_key,
            **kwargs
        )
        
        if not hasattr(func, '_amqp_bindings'):
            func._amqp_bindings = []
        func._amqp_bindings.append(binding)
        
        func._is_amqp_handler = True
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def rpc(queue_name: str, 
        timeout: float = 30.0,
        **kwargs) -> Callable:
    """
    Декоратор для регистрации RPC-обработчика.
    
    Args:
        queue_name: Имя очереди для RPC-запросов
        timeout: Таймаут выполнения (секунды)
        **kwargs: Доп. параметры для queue_declare
    
    Example:
        @rpc("calculate.price", timeout=10.0)
        async def calculate(data):
            return {"price": 100}
    """
    def decorator(func: Callable) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise ConfigurationError(
                f"RPC-consumer '{queue_name}' has to be an async function."
                f"Got: {func.__name__}"
            )
        
        sig = inspect.signature(func)
        if sig.return_annotation is inspect.Signature.empty:
            warnings.warn(
                f"RPC-consumer {func.__name__} has no return annotation type."
            )
        
        rpc_info = RPCHandler(
            queue_name=queue_name,
            timeout=timeout,
            **kwargs
        )
        func._rpc_handler = rpc_info
        func._is_amqp_handler = True
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
