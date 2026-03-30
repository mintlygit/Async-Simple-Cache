# AsyncSimpleCache
Умный кэш для асинхронных функций с поддержкой TTL.

## Особенности
- 🚀 Простой и интуитивный API
- ⚡ Полная поддержка asyncio
- ⏰ TTL (Time-To-Live) для записей
- 💾 Несколько бэкендов (In-memory, Redis)
- 🔧 Декораторы для кэширования функций
- 🧹 Автоматическая очистка устаревших записей
- 📊 Статистика использования

## Установка
```bash
pip install async-simple-cache
```

## Установка с поддержкой Redis:
```
pip install async-simple-cache[redis]
```

# Быстрый старт
## Декоратор
```
import asyncio
from async_simple_cache import acache

@acache(ttl=60)  # Кэшируем на 60 секунд
async def get_user(user_id: int):
    # Тяжелые вычисления или запрос к БД
    return await db.fetch_user(user_id)

async def main():
    user = await get_user(1)  # Первый вызов
    user = await get_user(1)  # Берется из кэша
```

## Ручное управление
```
from async_simple_cache import AsyncCache

cache = AsyncCache(default_ttl=30)
await cache.start()

# Сохранить
await cache.set("key", "value", ttl=10)

# Получить
value = await cache.get("key")

# Удалить
await cache.delete("key")

await cache.stop()
```

## С REDIS
```
from async_simple_cache import AsyncCache, RedisBackend

backend = RedisBackend("redis://localhost:6379")
cache = AsyncCache(backend=backend)

await cache.start()
await cache.set("key", "value")
await cache.stop()
```

# API
## AsyncCache
- get(key) - получить значение
- set(key, value, ttl=None) - сохранить значение
- delete(key) - удалить ключ
- exists(key) - проверить существование
- get_or_set(key, factory, ttl=None) - получить или создать
- clear() - очистить весь кэш
- stats() - получить статистику

## Декораторы
- @acache(ttl=None, cache=None, key_prefix="") - базовый декоратор
- @acache_with_args(ttl=None, cache=None) - с динамическим TTL