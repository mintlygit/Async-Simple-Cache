# 🚀 AsyncSimpleCache

[![PyPI version](https://badge.fury.io/py/async-simple-cache.svg)](https://badge.fury.io/py/async-simple-cache)
[![Python Version](https://img.shields.io/pypi/pyversions/async-simple-cache.svg)](https://pypi.org/project/async-simple-cache)
[![License](https://img.shields.io/github/license/mintlygit/Async-Simple-Cache.svg)](https://github.com/mintlygit/Async-Simple-Cache/blob/main/LICENSE)
[![Tests](https://github.com/mintlygit/Async-Simple-Cache/workflows/Tests/badge.svg)](https://github.com/mintlygit/Async-Simple-Cache/actions)
[![Code Coverage](https://codecov.io/gh/mintlygit/Async-Simple-Cache/branch/main/graph/badge.svg)](https://codecov.io/gh/mintlygit/Async-Simple-Cache)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Умный кэш для асинхронных функций с поддержкой TTL**

---

## ✨ Особенности

| Особенность | Описание |
|------------|----------|
| 🚀 **Простой API** | Интуитивно понятный интерфейс, который легко освоить |
| ⚡ **Полная асинхронность** | Нативная поддержка `asyncio` из коробки |
| ⏰ **TTL** | Гибкая настройка времени жизни кэша |
| 💾 **Множество бэкендов** | In-memory, Redis и легко расширяемые бэкенды |
| 🔧 **Декораторы** | Красивое кэширование функций в одну строку |
| 🧹 **Автоочистка** | Автоматическое удаление устаревших записей |
| 📊 **Статистика** | Мониторинг эффективности кэша |
| 🔒 **Потокобезопасность** | Безопасная работа в асинхронной среде |

---

## 📦 Установка
### Базовая установка
```bash
pip install async-simple-cache
```

### С поддержкой Redis
```bash
pip install async-simple-cache[redis]
```

### Для разработки
```bash
pip install async-simple-cache[dev]
```

# Быстрый старт
## [1️⃣] Декоратор
```python
import asyncio
from async_simple_cache import acache

@acache(ttl=60)  #Кэшируем на 60 секунд
async def get_user(user_id: int):
    """Тяжелые вычисления или запрос к БД"""
    print(f"Загружаем пользователя {user_id}...")
    await asyncio.sleep(1)  #Симуляция тяжелой операции
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
#Первый вызов - выполнится функция
    user1 = await get_user(1)
    
#Второй вызов - данные из кэша (мгновенно)
    user2 = await get_user(1)
    
    print(user1 == user2)  # True

asyncio.run(main())
```

## [2️⃣] Ручное управление
```python
from async_simple_cache import AsyncCache

async def manual_example():
    cache = AsyncCache(default_ttl=30)
    await cache.start()
    
#Сохраняем значение
    await cache.set("user:1", {"name": "Alice"}, ttl=10)
    
#Получаем значение
    user = await cache.get("user:1")
    print(user)  # {'name': 'Alice'}
    
#Проверяем существование
    if await cache.exists("user:1"):
        print("Ключ существует!")
    
#Получаем или создаем
    value = await cache.get_or_set(
        "counter",
        lambda: 100,
        ttl=60
    )
    
#Статистика
    stats = await cache.stats()
    print(f"Активных записей: {stats['active_entries']}")
    
    await cache.stop()
```

## [3️⃣] Redis
```python
from async_simple_cache import AsyncCache, RedisBackend

async def redis_example():
#Подключаемся к Redis
    backend = RedisBackend("redis://localhost:6379")
    cache = AsyncCache(backend=backend, default_ttl=300)
    
    await cache.start()
    
#Всё работает так же, как с Memory бэкендом
    await cache.set("key", "value")
    value = await cache.get("key")
    
    await cache.stop()
```

# Продвинутые примеры
### Динамический TTL
```python
#Зависимость от погоды!
from async_simple_cache import acache_with_args

@acache_with_args()
async def get_weather(city: str):
    weather = await fetch_weather(city)
    
#Чем лучше погода, тем дольше кэшируем
    if weather["temp"] > 25:
        ttl = 300  #5 минут для жары
    elif weather["temp"] < 0:
        ttl = 30   #30 секунд для мороза
    else:
        ttl = 120  #2 минуты в остальных случаях
    
    return weather, ttl  #Возвращаем кортеж (данные, ttl)
```

### Кастомный Префикс
```python
@acache(ttl=60, key_prefix="v1:")
async def api_call(user_id: int):
#Кэш с версионированием
    return await make_api_request(user_id)
```

### Инвалидация Кеша
```python
async def update_user(user_id: int, data: dict):
#Обновляем в БД
    await db.update_user(user_id, data)
    
#Инвалидируем кэш
    cache = AsyncCache()
    await cache.start()
    await cache.delete(f"user:{user_id}")
    await cache.stop()
```

# API Справочник
| Метод                         | Параметры                                    | Возврат  | Описание               |
|:-----------------------------:|:-------------------------------------------- |:--------:|:---------------------- |
| start()                       | -                                            | None     | Запуск кэширования     |
| stop()                        | -                                            | None     | Остановка кэширования  |
| get(key)                      | key: str                                     | Any/None | Получение значений     |
| set(key, value, ttl)          | key: str, value: Any, ttl: int | None        | None     | Сохранение значений    |
| delete(key)                   | key: str                                     | bool     | Удаление ключей        |
| exists(key)                   | key: str                                     | bool     | Проверка существования |
| get_or_set(key, factory, ttl) | key: str, factory: Callable, ttl: int | None | Any      | Получение или создание |
| clear()                       | -                                            | None     | Очистка всего кеша     |
| stats()                       | -                                            | dict     | Получение статистики   |

---

## Декораторы
| Декоратор         | Параметры              | Описание                              |
|:-----------------:|:---------------------- |:------------------------------------- |
| @acache           | ttl, cache, key_prefix | Базовое кэширование функций           |
| @acache_with_args | ttl, cache             | Динамический TTL на основе результата |

---

## Бэкенды
| Бэкенд        | Описание            | Когда использовать                   |
|:-------------:|:-------------------:|:------------------------------------ |
| MemoryBackend | In-memory хранилище | Разработка, тесты, небольшие проекты |
| RedisBackend  | Redis хранилище     | Production, распределенные системы   |

---

# Архитектура
**Компоненты системы:**

| Уровень | Компонент | Ответственность |
|---------|-----------|-----------------|
| 1 | Декораторы | `@acache`, `@acache_with_args` |
| 2 | AsyncCache Core | Управление ключами, TTL, логика кэша |
| 3 | Backend Interface | Единый API для всех хранилищ |
| 4 | Memory Backend | In-memory хранение с автоочисткой |
| 5 | Redis Backend | Redis хранение для production |
**Поток данных:**
Запрос → Декоратор → Core → Бэкенд → Хранилище
↓
Результат


# Производительность
| Операция     | Memory Backend | Redis Backend |
|:------------:|:--------------:|:-------------:|
| set()        | ~0.5 µs        | ~50 µs        |
| get() (hit)  | ~0.3 µs        | ~40 µs        |
| get() (miss) | ~0.2 µs        | ~35 µs        |
| delete()     | ~0.3 µs        | ~45 µs        |

---
Тесты проводились на Python 3.11, Intel i7, Redis 7.0

# 🤝 Внесение вклада
- Мы приветствуем вклад в проект!
- Форкните репозиторий
- Создайте ветку для фичи (git checkout -b feature/amazing-feature)
- Закоммитьте изменения (git commit -m 'Add amazing feature')
- Запушьте в ветку (git push origin feature/amazing-feature)
- Откройте Pull Request

### Разработка
```bash
# Клонируйте репозиторий
git clone https://github.com/mintlygit/Async-Simple-Cache.git
cd async-simple-cache

#Установите зависимости для разработки
make install-dev

#Запустите тесты
make test

#Проверьте качество кода
make lint
```

### 📝 Лицензия
Проект распространяется под лицензией MIT. Смотрите файл LICENSE для подробностей.

### 🙏 Благодарности
- Всем контрибьюторам проекта
- Python сообществу за отличные инструменты
- Вам за использование библиотеки! ⭐
