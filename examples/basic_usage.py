import asyncio
import time
from async_simple_cache import acache, AsyncCache

#Пример 1: Простой декоратор
@acache(ttl=3)
async def slow_function(name: str):
    print(f"Вычисляем для {name}...")
    await asyncio.sleep(1)
    return f"Hello, {name}!"

#Пример 2: Ручное управление кэшем
async def manual_cache_example():
    cache = AsyncCache(default_ttl=5)
    await cache.start()
    
    await cache.set("user:1", {"name": "Alice", "age": 30})
    
    user = await cache.get("user:1")
    print(f"User from cache: {user}")
    
    user2 = await cache.get_or_set(
        "user:2",
        lambda: asyncio.sleep(0.5) or {"name": "Bob", "age": 25}
    )
    print(f"User2: {user2}")
    
    stats = await cache.stats()
    print(f"Cache stats: {stats}")
    
    await cache.stop()

#Пример 3: Использование декоратора
async def decorator_example():
    print("\n--- Декоратор пример ---")
    
    start = time.time()
    result1 = await slow_function("Alice")
    print(f"Результат: {result1}, время: {time.time() - start:.2f}с")
    
    start = time.time()
    result2 = await slow_function("Alice")
    print(f"Результат (кэш): {result2}, время: {time.time() - start:.2f}с")
    
    result3 = await slow_function("Bob")
    print(f"Результат для Bob: {result3}")
    
    print("Ожидайте 3 секунды...")
    await asyncio.sleep(3)
    
    start = time.time()
    result4 = await slow_function("Alice")
    print(f"Результат после TTL: {result4}, время: {time.time() - start:.2f}с")

async def main():
    print("=== ASC Примеры ===\n")
    
    print("Пример ручного управления:")
    await manual_cache_example()
    
    print("\nПример декоратора:")
    await decorator_example()

if __name__ == "__main__":
    asyncio.run(main())