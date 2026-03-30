import pytest
import asyncio
from async_simple_cache.backends.memory import MemoryBackend
from async_simple_cache.backends.redis_backend import RedisBackend
from async_simple_cache.core import AsyncCache


class TestMemoryBackend:
    
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        backend = MemoryBackend()
        
        await backend.set("key1", "value1")
        result = await backend.get("key1")
        assert result == "value1"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        backend = MemoryBackend()
        result = await backend.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        backend = MemoryBackend(cleanup_interval=1)
        await backend.start()
        
        await backend.set("key", "value", ttl=1)
        result = await backend.get("key")
        assert result == "value"
        
        await asyncio.sleep(1.1)
        result = await backend.get("key")
        assert result is None
        
        await backend.stop()
    
    @pytest.mark.asyncio
    async def test_delete(self):
        backend = MemoryBackend()
        
        await backend.set("key", "value")
        assert await backend.exists("key") is True
        
        result = await backend.delete("key")
        assert result is True
        assert await backend.exists("key") is False
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        backend = MemoryBackend()
        result = await backend.delete("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_clear(self):
        backend = MemoryBackend()
        
        await backend.set("key1", "value1")
        await backend.set("key2", "value2")
        
        stats = await backend.stats()
        assert stats["total_entries"] == 2
        
        await backend.clear()
        stats = await backend.stats()
        assert stats["total_entries"] == 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        backend = MemoryBackend()
        
        await backend.set("key1", "value1", ttl=1)
        await backend.set("key2", "value2")  # без TTL
        
        await asyncio.sleep(1.1)
        
        cleaned = await backend.cleanup()
        assert cleaned == 1
        
        assert await backend.get("key1") is None
        assert await backend.get("key2") == "value2"
    
    @pytest.mark.asyncio
    async def test_stats(self):
        backend = MemoryBackend()
        
        await backend.set("key1", "value1", ttl=1)
        await backend.set("key2", "value2")
        await backend.set("key3", "value3", ttl=100)
        
        stats = await backend.stats()
        assert stats["total_entries"] == 3
        assert stats["active_entries"] == 3
        
        await asyncio.sleep(1.1)
        await backend.cleanup()
        
        stats = await backend.stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2


class TestRedisBackend:
    
    @pytest.mark.asyncio
    async def test_connection(self):
        backend = RedisBackend()
        is_connected = await backend.ping()
        
        if not is_connected:
            pytest.skip("Redis не доступен")
        
        assert await backend.ping() is True
    
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        await backend.set("test_key", "test_value")
        result = await backend.get("test_key")
        assert result == "test_value"
        
        await backend.delete("test_key")
    
    @pytest.mark.asyncio
    async def test_set_with_ttl(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        await backend.set("ttl_key", "value", ttl=2)
        
        result = await backend.get("ttl_key")
        assert result == "value"
        
        await asyncio.sleep(2.1)
        result = await backend.get("ttl_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_many(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        mapping = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        await backend.set_many(mapping)
        
        for key, value in mapping.items():
            result = await backend.get(key)
            assert result == value
        
        await backend.delete_many(list(mapping.keys()))
    
    @pytest.mark.asyncio
    async def test_delete_many(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        keys = ["del1", "del2", "del3"]
        for key in keys:
            await backend.set(key, "value")
        
        deleted = await backend.delete_many(keys)
        assert deleted == 3
        
        for key in keys:
            assert await backend.exists(key) is False
    
    @pytest.mark.asyncio
    async def test_increment(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        counter_key = "counter"
        
        value = await backend.increment(counter_key)
        assert value == 1
        
        value = await backend.increment(counter_key, 5)
        assert value == 6
        
        value = await backend.increment(counter_key, -2)
        assert value == 4
        
        await backend.delete(counter_key)
    
    @pytest.mark.asyncio
    async def test_expire(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        await backend.set("expire_key", "value")
        result = await backend.expire("expire_key", 10)
        assert result is True
        
        ttl = await backend.get_ttl("expire_key")
        assert ttl is not None and 0 < ttl <= 10
        
        await backend.delete("expire_key")
    
    @pytest.mark.asyncio
    async def test_keys(self):
        backend = RedisBackend(prefix="test_pattern:")
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        test_keys = ["user:1", "user:2", "post:1", "post:2"]
        for key in test_keys:
            await backend.set(key, "value")
        
        user_keys = await backend.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys
        
        # Очищаем
        await backend.clear()
    
    @pytest.mark.asyncio
    async def test_clear(self):
        backend = RedisBackend(prefix="test_clear:")
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        for i in range(5):
            await backend.set(f"key{i}", f"value{i}")
        
        keys = await backend.keys("*")
        assert len(keys) == 5
        
        await backend.clear()
        
        keys = await backend.keys("*")
        assert len(keys) == 0
    
    @pytest.mark.asyncio
    async def test_close(self):
        backend = RedisBackend()
        
        if not await backend.ping():
            pytest.skip("Redis не доступен")
        
        await backend.set("close_test", "value")
        await backend.close()
        
        #После закрытия должны быть ошибки, но не упадёт
        #Создаем новое соединение для очистки
        new_backend = RedisBackend()
        await new_backend.delete("close_test")
        await new_backend.close()


class TestBackendIntegration:
    
    @pytest.mark.asyncio
    async def test_memory_backend_integration(self):
        cache = AsyncCache(backend=MemoryBackend(), default_ttl=5)
        await cache.start()
        
        await cache.set("test", "value")
        assert await cache.get("test") == "value"
        
        stats = await cache.stats()
        assert stats["active_entries"] == 1
        
        await cache.stop()
    
    @pytest.mark.asyncio
    async def test_redis_backend_integration(self):
        redis_backend = RedisBackend()
        
        if not await redis_backend.ping():
            pytest.skip("Redis не доступен")
        
        cache = AsyncCache(backend=redis_backend, default_ttl=5)
        await cache.start()
        
        await cache.set("integration_test", "redis_value")
        result = await cache.get("integration_test")
        assert result == "redis_value"
        
        stats = await cache.stats()
        assert stats["backend"] == "redis"
        
       