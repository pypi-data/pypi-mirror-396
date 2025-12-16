class AudienceError(Exception):
    """Базовое исключение для всех ошибок фреймворка."""
    pass

class ConfigurationError(AudienceError):
    """Ошибка конфигурации."""
    pass

class ConnectionError(AudienceError):
    """Ошибки подключения к брокеру или внешним сервисам."""
    pass

class HandlerError(AudienceError):
    """Ошибки в пользовательских обработчиках."""
    pass

class ValidationError(HandlerError):
    """Ошибка валидации входящего сообщения."""
    def __init__(self, field: str, value: str, msg: str):
        super().__init__(
            f"Validation error of field '{field}': {msg}. Got: {value}"
        )
        self.field = field
        self.value = value

class SerializationError(HandlerError):
    """Ошибка сериализации/десериализации сообщения."""
    pass

class TimeoutError(AudienceError):
    """Таймаут RPC-запроса."""
    pass

class QueueError(AudienceError):
    """Ошибки работы с очередями."""
    pass
