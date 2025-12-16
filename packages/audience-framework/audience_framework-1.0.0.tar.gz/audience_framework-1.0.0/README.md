# Audience

Фреймворк для написания на Python асинхронных микросервисов поверх AMQP.

# Особенности:

*   **Декларативный стиль**: Регистрация обработчиков через декораторы.
*   **Два типа обработчиков**: Фоновые задачи (`@app.queue`) и RPC-вызовы (`@app.rpc`).
*   **Полностью асинхронный**: Построен на `asyncio` и `aio-pika`.
*   **Простой API**: Всего несколько методов для начала работы.

## Установка:

```bash
pip install audience-framework
```

## Пример использования:

1. Импорт модуля asyncio и класса Audience из библиотеки audience:
```python
import asyncio

from audience import Audience
```
2. Создание экземпляра приложения:
```python
app = Audience(broker_url="amqp://admin:12345@localhost")
```
3. Регистрация обработчиков очередей сообщений:
```python
@app.queue("queue_name")
async def foo():
    ...

@app.rpc("rpc_queue_name")
async def foo():
    ...
    return { ... }
```
4. Запуск приложения:
```python
if __name__ == "__main__":
    asyncio.run(app.startup())
```

### Дополнительные функции:
1. Отправка сообщения в очередь:
```python
await app.publish("queue_name", "message")
```
2. Отправка RPC-запроса:
```python
await app.rpc_call("rpc_queue_name", "message")