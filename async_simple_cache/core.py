import asyncio
import hashlib
import json
from typing import Optional, Any, Callable, Awaitable, TypeVar, Generic
from .backends.memory import MemoryBackend

T = TypeVar('T')

class AsyncCache(Generic[T]):
    
    def __init__(self, backend=None, default_ttl: Optional[int] = None):
### ===================================================================
###        Инициализация кэша
###        Args:
###            backend: Бэкенд хранилища (по умолчанию MemoryBackend)
###            default_ttl: TTL по умолчанию в секундах
### ===================================================================
        self.backend = backend or MemoryBackend()
        self.default_ttl = default_ttl
        self._running = False
    
    async def start(self):
        if hasattr(self.backend, 'start'):
            await self.backend.start()
        self._running = True
    
    async def stop(self):
        if hasattr(self.backend, 'stop'):
            await self.backend.stop()
        if hasattr(self.backend, 'close'):
            await self.backend.close()
        self._running = False
    
    def _make_key(self, *args, **kwargs) -> str:
        sorted_kwargs = sorted(kwargs.items())
        
        key_data = {
            'args': args,
            'kwargs': dict(sorted_kwargs)
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[T]:
        if not self._running:
            raise RuntimeError("Cache is not running. Call start() first.")
        return await self.backend.get(key)
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None):
        if not self._running:
            raise RuntimeError("Cache is not running. Call start() first.")
        ttl = ttl if ttl is not None else self.default_ttl
        await self.backend.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        return await self.backend.delete(key)
    
    async def exists(self, key: str) -> bool:
        return await self.backend.exists(key)
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: Optional[int] = None
    ) -> T:
### ===================================================================
###        Получить значение или создать через factory функцию       
###        Args:
###            key: Ключ кэша
###            factory: Асинхронная функция для создания значения
###            ttl: TTL для нового значения            
###        Returns:
###            Значение из кэша или новое
### ===================================================================
        value = await self.get(key)
        if value is not None:
            return value
        
        value = await factory()
        await self.set(key, value, ttl)
        return value
    
    async def clear(self):
        await self.backend.clear()
    
    async def cleanup(self):
        await self.backend.cleanup()
    
    async def stats(self) -> dict:
        return await self.backend.stats()