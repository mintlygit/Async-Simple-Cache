import pytest
import asyncio
from async_simple_cache import AsyncCache, MemoryBackend

@pytest.fixture
async def cache():
    backend = MemoryBackend(cleanup_interval=1)
    cache = AsyncCache(backend=backend, default_ttl=2)
    await cache.start()
    yield cache
    await cache.stop()

@pytest.mark.asyncio
async def test_set_and_get(cache):
    await cache.set("key", "value")
    result = await cache.get("key")
    assert result == "value"

@pytest.mark.asyncio
async def test_ttl_expiration(cache):
    await cache.set("key", "value", ttl=1)
    result = await cache.get("key")
    assert result == "value"
    
    await asyncio.sleep(1.1)
    result = await cache.get("key")
    assert result is None

@pytest.mark.asyncio
async def test_get_or_set(cache):
    called = 0
    
    async def factory():
        nonlocal called
        called += 1
        return "computed_value"
    
    result1 = await cache.get_or_set("key", factory)
    assert result1 == "computed_value"
    assert called == 1
    
    result2 = await cache.get_or_set("key", factory)
    assert result2 == "computed_value"
    assert called == 1

@pytest.mark.asyncio
async def test_delete(cache):
    await cache.set("key", "value")
    assert await cache.exists("key") is True
    
    await cache.delete("key")
    assert await cache.exists("key") is False

@pytest.mark.asyncio
async def test_clear(cache):
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    
    stats = await cache.stats()
    assert stats["active_entries"] == 2
    
    await cache.clear()
    stats = await cache.stats()
    assert stats["active_entries"] == 0