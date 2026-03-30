import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
from ..types import CacheEntry

class MemoryBackend:
    
    def __init__(self, cleanup_interval: int = 60):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task = None
    
    async def start(self):
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self.cleanup()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                return entry.value
            elif entry:
                # Удаляем истекшую запись
                del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expires_at = None
        if ttl is not None:
            from datetime import timedelta
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        async with self._lock:
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                return True
            return False
    
    async def cleanup(self):
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)
    
    async def clear(self):
        async with self._lock:
            self._cache.clear()
    
    async def stats(self) -> dict:
        async with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired)
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired,
            }