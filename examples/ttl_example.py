"""
Примеры использования TTL в ASC
Демонстрация различных стратегий кэширования
"""

import asyncio
import time
from datetime import datetime
from async_simple_cache import acache, acache_with_args, AsyncCache, MemoryBackend


#Пример 1: Фиксированный TTL
@acache(ttl=3)
async def get_current_time_fixed():
    await asyncio.sleep(0.1)  #Симуляция работы
    return datetime.now().isoformat()


#Пример 2: Разный TTL для разных аргументов
class DynamicTTLCache:
    def __init__(self):
        self.cache = AsyncCache()
    
    async def get_user_data(self, user_id: int, priority: str = "normal"):
### =============================================================================
###        Разный TTL в зависимости от приоритета
###        Пользователи кэшируются дольше
### =============================================================================
        ttl_map = {
            "vip": 300,      #5 минут для VIP
            "normal": 60,    #1 минута для обычных
            "guest": 10      #10 секунд для гостей
        }
        ttl = ttl_map.get(priority, 60)
        
        key = f"user:{user_id}:{priority}"
        
        return await self.cache.get_or_set(
            key,
            lambda: self._fetch_user_from_db(user_id, priority),
            ttl=ttl
        )
    
    async def _fetch_user_from_db(self, user_id: int, priority: str):
        print(f"  📡 Загрузка пользователя {user_id} (приоритет: {priority}) из БД...")
        await asyncio.sleep(0.5)
        return {
            "id": user_id,
            "name": f"User_{user_id}",
            "priority": priority,
            "fetched_at": datetime.now().isoformat()
        }


#Пример 3: Адаптивный TTL на основе данных
@acache_with_args()
async def get_weather(city: str):
### =============================================================================
###    Кэширует погоду с разным TTL в зависимости от температуры
###    Если погода хорошая - кэшируем дольше
### =============================================================================
    print(f"  🌤️  Запрос погоды для {city}...")
    await asyncio.sleep(0.3)  #Симуляция API запроса
    
#Симуляция разных температур
    weather_data = {
        "Moscow": {"temp": -5, "condition": "снег"},
        "London": {"temp": 10, "condition": "дождь"},
        "Dubai": {"temp": 35, "condition": "солнечно"},
        "Tokyo": {"temp": 20, "condition": "облачно"},
    }
    
    data = weather_data.get(city, {"temp": 15, "condition": "unknown"})
    
#Адаптивный TTL: чем лучше погода, тем дольше кэшируем
    if data["temp"] > 25:
        custom_ttl = 300  #5 минут для жаркой погоды
    elif data["temp"] < 0:
        custom_ttl = 30   #30 секунд для холодной
    else:
        custom_ttl = 120  #2 минуты для нормальной
    
    return data, custom_ttl


#Пример 4: Скользящий TTL (обновление при доступе)
class SlidingTTLCache:
### =============================================================================
###    Кэш со скользящим TTL - время жизни обновляется при каждом доступе
### =============================================================================
    def __init__(self, default_ttl: int = 60):
        self.cache = AsyncCache()
        self.default_ttl = default_ttl
    
    async def get(self, key: str, factory, ttl: int = None):
### =============================================================================
###        Получить значение, обновляя TTL при каждом успешном доступе
### =============================================================================
        ttl = ttl or self.default_ttl
        value = await self.cache.get(key)
        
        if value is not None:
#Обновляем TTL при доступе
            await self.cache.set(key, value, ttl)
            print(f"  🔄 Обновлен TTL для ключа {key}")
            return value
        
#Создаем новое значение
        value = await factory()
        await self.cache.set(key, value, ttl)
        return value
    
    async def start(self):
        await self.cache.start()
    
    async def stop(self):
        await self.cache.stop()


#Пример 5: Иерархический TTL (несколько уровней кэша)
class HierarchicalTTLCache:
### =============================================================================
###    Двухуровневый кэш: L1 (быстрый, малый TTL) и L2 (медленный, большой TTL)
### =============================================================================
    def __init__(self):
        self.l1_cache = AsyncCache(backend=MemoryBackend(), default_ttl=10)   # 10 секунд
        self.l2_cache = AsyncCache(backend=MemoryBackend(), default_ttl=300)  # 5 минут
    
    async def start(self):
        await self.l1_cache.start()
        await self.l2_cache.start()
    
    async def stop(self):
        await self.l1_cache.stop()
        await self.l2_cache.stop()
    
    async def get(self, key: str, factory):
#Пытаемся получить из L1
        value = await self.l1_cache.get(key)
        if value is not None:
            print(f"  ✅ Данные из L1 кэша (быстрый)")
            return value
        
#Пытаемся получить из L2
        value = await self.l2_cache.get(key)
        if value is not None:
            print(f"  ⚡ Данные из L2 кэша (медленный)")
#Копируем в L1 для быстрого доступа
            await self.l1_cache.set(key, value)
            return value
        
#Загружаем новые данные
        print(f"  💾 Загрузка свежих данных...")
        value = await factory()
        
#Сохраняем в оба уровня
        await self.l1_cache.set(key, value)
        await self.l2_cache.set(key, value)
        
        return value


async def example_1_fixed_ttl():
    print("\n" + "="*50)
    print("📌 Пример 1: Фиксированный TTL (3 секунды)")
    print("="*50)
    
    for i in range(5):
        current_time = await get_current_time_fixed()
        print(f"  Вызов {i+1}: {current_time}")
        
        if i == 2:
            print("  ⏳ Ждем 4 секунды...")
            await asyncio.sleep(4)
        
        await asyncio.sleep(0.5)


async def example_2_dynamic_ttl():
    print("\n" + "="*50)
    print("📌 Пример 2: Динамический TTL (разный для разных приоритетов)")
    print("="*50)
    
    cache = DynamicTTLCache()
    await cache.cache.start()
    
    user_id = 123
    
#Пользователь
    print("\n  Пользователь:")
    for i in range(3):
        user = await cache.get_user_data(user_id, "vip")
        print(f"    Вызов {i+1}: {user['fetched_at'][:19]}")
        await asyncio.sleep(2)
    
#Гость
    print("\n  🚶 Гость:")
    for i in range(3):
        user = await cache.get_user_data(user_id, "guest")
        print(f"    Вызов {i+1}: {user['fetched_at'][:19]}")
        await asyncio.sleep(2)
    
    await cache.cache.stop()


async def example_3_adaptive_ttl():
    print("\n" + "="*50)
    print("📌 Пример 3: Адаптивный TTL (зависит от температуры)")
    print("="*50)
    
    cities = ["Dubai", "Moscow", "London"]
    
    for city in cities:
        print(f"\n  🏙️  Город: {city}")
        
#Первый запрос
        weather = await get_weather(city)
        print(f"    Погода: {weather['temp']}°C, {weather['condition']}")
        
#Второй запрос сразу (должен быть из кэша)
        weather = await get_weather(city)
        print(f"    Повторный запрос (из кэша): {weather['temp']}°C")
        
#Ждем разное время в зависимости от города
        if city == "Dubai":
            print("    ⏳ Ждем 60 секунд (должен быть еще в кэше)...")
            await asyncio.sleep(60)
        elif city == "Moscow":
            print("    ⏳ Ждем 20 секунд (кэш должен истечь)...")
            await asyncio.sleep(20)
        
#Проверяем после ожидания
        weather = await get_weather(city)
        print(f"    После ожидания: {weather['temp']}°C")
        
        await asyncio.sleep(1)


async def example_4_sliding_ttl():
    print("\n" + "="*50)
    print("📌 Пример 4: Скользящий TTL (обновляется при доступе)")
    print("="*50)
    
    cache = SlidingTTLCache(default_ttl=5)
    await cache.start()
    
    async def expensive_computation():
        print("    💻 Выполняем сложные вычисления...")
        await asyncio.sleep(0.5)
        return {"result": 42, "timestamp": time.time()}
    
    key = "sliding_key"
    
#Первый доступ
    print("\n  Первый доступ:")
    value = await cache.get(key, expensive_computation, ttl=5)
    print(f"    Значение: {value}")
    
#Доступ через 3 секунды (обновит TTL)
    print("\n  Доступ через 3 секунды:")
    await asyncio.sleep(3)
    value = await cache.get(key, expensive_computation, ttl=5)
    print(f"    Значение из кэша: {value}")
    
#Доступ через 4 секунды (должен быть еще в кэше)
    print("\n  Доступ через 4 секунды:")
    await asyncio.sleep(4)
    value = await cache.get(key, expensive_computation, ttl=5)
    print(f"    Значение из кэша: {value}")
    
#Доступ через 6 секунд (кэш должен истечь)
    print("\n  Доступ через 6 секунд:")
    await asyncio.sleep(6)
    value = await cache.get(key, expensive_computation, ttl=5)
    print(f"    Новое значение: {value}")
    
    await cache.stop()


async def example_5_hierarchical_ttl():
    print("\n" + "="*50)
    print("📌 Пример 5: Иерархический TTL (L1: 10с, L2: 300с)")
    print("="*50)
    
    cache = HierarchicalTTLCache()
    await cache.start()
    
    async def fetch_from_source():
        print("    🌐 Загрузка из внешнего источника...")
        await asyncio.sleep(0.5)
        return {"data": "expensive_data", "timestamp": time.time()}
    
    key = "hierarchical_key"
    
#Серия запросов
    for i in range(5):
        print(f"\n  Запрос {i+1}:")
        value = await cache.get(key, fetch_from_source)
        print(f"    Значение: {value['data']}, время: {value['timestamp']:.2f}")
        
        if i == 1:
            print("    ⏳ Ждем 12 секунд (L1 истекает, L2 остается)...")
            await asyncio.sleep(12)
        else:
            await asyncio.sleep(1)
    
    await cache.stop()


async def example_6_batch_operations_with_ttl():
    print("\n" + "="*50)
    print("📌 Пример 6: Массовые операции с разным TTL")
    print("="*50)
    
    cache = AsyncCache(default_ttl=10)
    await cache.start()
    
#Сохраняем несколько значений с разным TTL
    items = {
        "temp_key": 100,      #Временные данные
        "config_key": 200,    #Конфигурация
        "static_key": 999999  #Почти постоянные данные
    }
    
    ttl_map = {
        "temp_key": 5,
        "config_key": 60,
        "static_key": None  #Бесконечный TTL
    }
    
    print("\n  Сохраняем данные с разным TTL:")
    for key, value in items.items():
        ttl = ttl_map.get(key)
        await cache.set(key, value, ttl)
        ttl_text = f"{ttl}с" if ttl else "бесконечно"
        print(f"    {key} = {value} (TTL: {ttl_text})")
    
#Проверяем TTL
    print("\n  Проверяем оставшееся время жизни:")
    for key in items.keys():
        #Получаем оставшееся время (если бы был метод)
        exists = await cache.exists(key)
        print(f"    {key}: существует = {exists}")
    
    print("\n  Ждем 6 секунд...")
    await asyncio.sleep(6)
    
    print("\n  После ожидания:")
    for key in items.keys():
        value = await cache.get(key)
        print(f"    {key}: {value if value else 'истек'}")
    
    await cache.stop()


async def main():
    print("\n" + "🎯" * 20)
    print("DEMO: AsyncSimpleCache - TTL Strategies")
    print("🎯" * 20)
    
    await example_1_fixed_ttl()
    await example_2_dynamic_ttl()
    #await example_3_adaptive_ttl() - Требует много времени
    await example_4_sliding_ttl()
    await example_5_hierarchical_ttl()
    await example_6_batch_operations_with_ttl()
    
    print("\n" + "✨" * 20)
    print("Все примеры завершены!")
    print("✨" * 20)


if __name__ == "__main__":
    asyncio.run(main())