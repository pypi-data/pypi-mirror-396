import asyncio
import logging
import ssl
from typing import Optional
from contextlib import asynccontextmanager

import aio_pika
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractChannel
)
from pydantic import (
    BaseModel, 
    Field,
    ConfigDict
)

from .utils import mask_password


class ConnectionConfig(BaseModel):
    """Конфигурация подключения с валидацией."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: str
    reconnect_interval: int = Field(default=5, ge=1)
    max_retries: Optional[int] = Field(default=None, ge=1)
    ssl_context: Optional[ssl.SSLContext] = None


class RabbitMQConnection:
    """
    Управляет жизненным циклом подключения к RabbitMQ.
    Обрабатывает переподключения, создает каналы.
    """
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connection: Optional[AbstractRobustConnection] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._is_shutting_down = False

    async def connect(self) -> None:
        """Устанавливает соединение с механизмом повторных попыток."""
        if self._connection and not self._connection.is_closed:
            return

        logging.info(f"Connecting to {mask_password(self.config.url)}")
        retry_count = 0

        while not self._is_shutting_down:
            try:
                self._connection = await aio_pika.connect_robust(
                    self.config.url,
                    ssl_context=self.config.ssl_context,
                    timeout=10
                )
                self._connection.reconnect_callbacks.add(
                    self._on_connection_lost
                )
                logging.info("Connection created")
                return

            except (ConnectionError, OSError, asyncio.TimeoutError) as e:
                retry_count += 1
                if (
                    self.config.max_retries 
                    and retry_count > self.config.max_retries
                ):
                    logging.error(
                        f"Attempts limit achieved ({self.config.max_retries})"
                    )
                    raise

                wait_time = self.config.reconnect_interval * \
                            (2 ** (retry_count - 1))
                logging.warning(
                    "Connection error: {}. " \
                    "Repeat after {}s (attempt {})".format(
                        e,
                        wait_time,
                        retry_count
                    )
                )
                await asyncio.sleep(wait_time)

    async def disconnect(self) -> None:
        """Корректное отключение."""
        self._is_shutting_down = True
        if self._reconnect_task:
            self._reconnect_task.cancel()

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logging.info("Connection closed")

    async def create_channel(self) -> AbstractChannel:
        """Создает новый канал с обработкой ошибок."""
        if not self._connection or self._connection.is_closed:
            raise RuntimeError("Connection is not active")

        try:
            return await self._connection.channel()
        except Exception as e:
            logging.error(f"Creating channel error: {e}")
            raise

    async def _on_connection_lost(
        self, 
        connection: AbstractRobustConnection, 
        exc: Exception
    ) -> None:
        """Callback при потере соединения."""
        if self._is_shutting_down:
            return

        logging.error(
            f"Lost connection {connection}: {exc}. Trying to reconnect..."
        )
        self._reconnect_task = asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        """Фоновая задача переподключения."""
        await asyncio.sleep(self.config.reconnect_interval)
        try:
            await self.connect()
        except Exception as e:
            logging.error(f"Reconnection failed: {e}")

    @asynccontextmanager
    async def get_channel(self):
        """
        Context manager для автоматического закрытия канала.
        Использование:
        async with connection.get_channel() as channel:
            await channel.queue_declare(...)
        """
        channel = await self.create_channel()
        try:
            yield channel
        finally:
            if not channel.is_closed:
                await channel.close()
