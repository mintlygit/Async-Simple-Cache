import json
from typing import Optional, Any
import redis.asyncio as redis

class RedisBackend:
    
    def __init__(self, redis_url: str = "redis://localhost:6379", prefix: str = "acache:"):
        self.redis_url = redis_url
        self.prefix = prefix
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = await redis.from_url(self.redis_url, decode_responses=True)
        return self._client
    
    def _make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        value = await client.get(self._make_key(key))
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        client = await self._get_client()
        serialized = json.dumps(value, default=str)
        await client.set(self._make_key(key), serialized, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        client = await self._get_client()
        result = await client.delete(self._make_key(key))
        return result > 0
    
    async def exists(self, key: str) -> bool:
        client = await self._get_client()
        return await client.exists(self._make_key(key)) > 0
    
    async def cleanup(self):
        pass
    
    async def clear(self):
        client = await self._get_client()
        pattern = f"{self.prefix}*"
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    
    async def stats(self) -> dict:
        client = await self._get_client()
        pattern = f"{self.prefix}*"
        keys = await client.keys(pattern)
        return {
            "total_entries": len(keys),
            "backend": "redis",
        }
    
    async def close(self):
        if self._client:
            await self._client.close()