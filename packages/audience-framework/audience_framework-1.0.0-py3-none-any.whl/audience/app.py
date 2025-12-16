import sys
import asyncio
import inspect
import logging
import json
import uuid
from typing import (
    Any,
    Callable,
    Optional,
    Union
)
from dataclasses import (
    dataclass, 
    field
)

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel

from .connections import (
    RabbitMQConnection, 
    ConnectionConfig
)
from .exceptions import (
    ConfigurationError, 
    HandlerError
)
from .decorators import (
    queue as d_queue,
    rpc as d_rpc
)


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class RegisteredHandler:
    """Контейнер для хранения информации о зарегистрированном обработчике"""
    func: Callable
    queue_name: str
    is_rpc: bool = False
    model: Optional[type[BaseModel]] = None


@dataclass
class Audience:
    """Основной класс приложения"""
    broker_url: str
    prefetch_count: int = 10
    _connection_pool: Optional[RabbitMQConnection] = None
    _handlers: dict[str, RegisteredHandler] = field(default_factory=dict)
    _consumers: dict[str, asyncio.Task] = field(default_factory=dict)

    def queue(self, queue_name: str):
        """
        Декоратор для регистрации асинхронного обработчика очереди.
        Использование: @app.queue("orders.created")
        """
        
        return d_queue(queue_name)
    
    def rpc(self, queue_name: str):
        """
        Декоратор для регистрации RPC-обработчика.
        Использование: @app.rpc("calculate.price")
        """
        
        return d_rpc(queue_name)
    
    def _register_handler(
        self, 
        func: Callable, 
        queue_name: str, 
        is_rpc: bool
    ):
        """Анализирует сигнатуру функции и регистрирует обработчик."""
        if not asyncio.iscoroutinefunction(func):
            raise ConfigurationError(
                f"Handler '{func.__name__}' has to be an async function."
            )

        sig = inspect.signature(func)
        model = None
        for param in sig.parameters.values():
            if inspect.isclass(param.annotation) and issubclass(
                param.annotation, 
                BaseModel
            ):
                model = param.annotation
                break

        handler = RegisteredHandler(
            func=func,
            queue_name=queue_name,
            is_rpc=is_rpc,
            model=model
        )

        self._handlers[queue_name] = handler
        logging.info(
            f"Registered handler for queue '{queue_name}': {func.__name__}"
        )
    
    def _register_handlers_from_decorators(self):
        """
        Автоматически регистрирует обработчики, помеченные декораторами.
        Вызывается при startup().
        """

        modules_items = list(sys.modules.items())
        for _, module in modules_items:
            for attr_name in dir(module):
                func = getattr(module, attr_name, None)
            
                if callable(func) and hasattr(func, '_is_amqp_handler'):
                    if hasattr(func, '_amqp_bindings'):
                        for binding in func._amqp_bindings:
                            self._register_handler(
                                func=func,
                                queue_name=binding.queue_name,
                                is_rpc=False
                            )
                
                    if hasattr(func, '_rpc_handler'):
                        rpc_info = func._rpc_handler
                        self._register_handler(
                            func=func,
                            queue_name=rpc_info.queue_name,
                            is_rpc=True
                        )
    
    async def startup(self):
        """Инициализирует соединение с брокером и запускает потребителей."""
        self._register_handlers_from_decorators()

        config = ConnectionConfig(url=self.broker_url)
    
        if self._connection_pool is None:
            self._connection_pool = RabbitMQConnection(config)
            await self._connection_pool.connect()

        for queue_name, handler in self._handlers.items():
            try:
                consumer_task = asyncio.create_task(
                    self._consume_queue(queue_name, handler)
                )
                await asyncio.wait_for(consumer_task, timeout=10.0)
            
            except asyncio.TimeoutError:
                logging.error(f"Timeout initializing consumer for '{queue_name}'")
                raise
            except Exception as e:
                logging.error(f"Failed to initialize consumer for '{queue_name}': {e}")
                raise
    
        logging.info(f"All {len(self._handlers)} consumers running")

        await asyncio.Future()
    
    async def shutdown(self):
        """Корректно останавливает потребителей и закрывает соединения."""
        logging.info("Begining graceful shutdown...")
        for task in self._consumers.values():
            task.cancel()
        if self._consumers:
            await asyncio.gather(
                *self._consumers.values(), 
                return_exceptions=True
            )

        if self._connection_pool:
            await self._connection_pool.disconnect()
        logging.info("Application shutted down.")
    
    async def _consume_queue(
        self, 
        queue_name: str, 
        handler: RegisteredHandler
    ):
        """Создает канал, объявляет очередь и начинает потребление сообщений."""
        try:
            channel = await self._connection_pool.create_channel()
            await channel.set_qos(prefetch_count=self.prefetch_count)

            queue = await channel.declare_queue(queue_name, durable=True)


            async def callback(message: AbstractIncomingMessage):
                """Обработка одного входящего сообщения."""
                async with message.process():
                    try:
                        result = await self._process_message(message, handler)

                        if handler.is_rpc and message.reply_to:
                            await self._send_rpc_reply(
                                message.reply_to, 
                                result, 
                                message.correlation_id
                            )
                    except Exception as e:
                        logging.error(f"Error while executing message: {e}")
            

            await queue.consume(callback)

        except asyncio.CancelledError:
            logging.info(f"Consumer for '{queue_name}' cancelled.")
        
        except Exception as e:
            logging.error(f"Critical error in consumer '{queue_name}': {e}")
    
    async def _process_message(
        self, 
        message: AbstractIncomingMessage, 
        handler: RegisteredHandler
    ) -> Any:
        """Декодирует, валидирует и выполняет бизнес-логику."""
        try:
            body = message.body.decode()
        except UnicodeDecodeError:
            raise HandlerError("Incorrect encoding message body.")

        data = body
        if handler.model:
            try:
                data = handler.model(**json.loads(body))
            except json.JSONDecodeError:
                raise HandlerError("Message body is not a valid JSON-type.")
            except Exception as e:
                raise HandlerError(f"Validation error: {e}")

        if inspect.signature(handler.func).parameters:
            result = await handler.func(data)
        else:
            result = await handler.func()

        return result
    
    async def _send_rpc_reply(
        self, 
        reply_to: str, 
        result: Any, 
        correlation_id: str
    ):
        """Отправляет ответ на RPC-запрос."""
        channel = await self._connection_pool.create_channel()
        try:
            if isinstance(
                result, (dict, list, str, int, float, bool, type(None))
            ):
                body = json.dumps(result).encode()
            elif isinstance(result, BaseModel):
                body = result.model_dump_json().encode()
            else:
                body = str(result).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=body,
                    correlation_id=correlation_id,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=reply_to
            )
        finally:
            await channel.close()
    
    async def publish(
        self,
        queue_name: str, 
        data: Union[dict, BaseModel, str]
    ):
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
        if not self._connection_pool:
            raise RuntimeError(
                "Application is not started up. Call await app.startup()"
            )

        channel = await self._connection_pool.create_channel()
        try:
            if isinstance(data, BaseModel):
                body = data.model_dump_json().encode()
            elif isinstance(data, dict):
                body = json.dumps(data).encode()
            else:
                body = str(data).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=body, 
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=queue_name
            )
        finally:
            await channel.close()

    async def rpc_call(
        self, 
        queue_name: str, 
        message: Union[dict, BaseModel, str], 
        timeout: float = 30.0,
        **kwargs
    ) -> dict:
        """
        Выполняет RPC-вызов и возвращает ответ.
        
        Args:
            queue_name: Очередь для отправки запроса
            message: Данные запроса (dict, BaseModel или JSON-строка)
            timeout: Максимальное время ожидания ответа (секунды)
            **kwargs: Доп. параметры (correlation_id, headers и т.д.)
        
        Returns:
            Ответ от RPC-сервера
        
        Raises:
            TimeoutError: Если ответ не получен за timeout
            ConnectionError: Если нет подключения к брокеру
        """
        if not self._connection_pool:
            raise ConnectionError(
                "Application is not started up. Call await app.startup()"
            )
        
        correlation_id = kwargs.get('correlation_id', str(uuid.uuid4()))
        
        channel = await self._connection_pool.create_channel()
        try:
            reply_queue = await channel.declare_queue(
                exclusive=True,
                auto_delete=True
            )
            
            if isinstance(message, BaseModel):
                body = message.model_dump_json().encode()
            elif isinstance(message, dict):
                body = json.dumps(message).encode()
            else:
                body = str(message).encode()
            
            amqp_message = aio_pika.Message(
                body=body,
                correlation_id=correlation_id,
                reply_to=reply_queue.name,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers=kwargs.get('headers', {})
            )
            
            await channel.default_exchange.publish(
                amqp_message,
                routing_key=queue_name
            )
            
            try:
                async with asyncio.timeout(timeout):
                    async for response in reply_queue:
                        async with response.process():
                            if response.correlation_id == correlation_id:
                                return json.loads(response.body.decode())
            except asyncio.TimeoutError:
                from .exceptions import TimeoutError
                raise TimeoutError(
                    f"RPC to '{queue_name}' exceeded timeout {timeout}s"
                )
                
        finally:
            await channel.close()
