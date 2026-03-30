import functools
from typing import Optional, Callable, Any, TypeVar
from .core import AsyncCache
from .backends.memory import MemoryBackend

_default_cache = None

def get_default_cache():
    global _default_cache
    if _default_cache is None:
        _default_cache = AsyncCache()
    return _default_cache

T = TypeVar('T')

def acache(
    ttl: Optional[int] = None,
    cache: Optional[AsyncCache] = None,
    key_prefix: str = ""
):
### ===================================================================================
###    Декоратор для кэширования асинхронных функций
###    Args:
###        ttl: Время жизни кэша в секундах
###        cache: Экземпляр кэша (используется глобальный по умолчанию)
###        key_prefix: Префикс для ключа кэша   
###    Example:
###        @acache(ttl=60)
###        async def get_user(user_id: int):
###            return await db.fetch_user(user_id)
### ===================================================================================
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_instance = cache or get_default_cache()
            
            if not hasattr(cache_instance, '_running') or not cache_instance._running:
                await cache_instance.start()
            
            key = f"{key_prefix}{func.__name__}:{cache_instance._make_key(*args, **kwargs)}"
            
            cached_value = await cache_instance.get(key)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            await cache_instance.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def acache_with_args(
    ttl: Optional[int] = None,
    cache: Optional[AsyncCache] = None
):
### ===================================================================================
###    Расширенный декоратор для кэширования с возможностью динамического TTL  
###    Позволяет функции вернуть кортеж (value, custom_ttl) 
###    Example:
###        @acache_with_args()
###        async def get_expensive_data():
###            value = await compute()
###            # Кэшируем на 10 секунд если значение маленькое
###            ttl = 10 if value < 100 else 60
###            return value, ttl
### ===================================================================================
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_instance = cache or get_default_cache()
            
            if not hasattr(cache_instance, '_running') or not cache_instance._running:
                await cache_instance.start()
            
            key = f"{func.__name__}:{cache_instance._make_key(*args, **kwargs)}"
            
            cached_value = await cache_instance.get(key)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], (int, type(None))):
                value, custom_ttl = result
                final_ttl = custom_ttl if custom_ttl is not None else ttl
            else:
                value = result
                final_ttl = ttl
            
            await cache_instance.set(key, value, final_ttl)
            return value
        
        return wrapper
    return decorator