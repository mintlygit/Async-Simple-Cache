import pytest
import asyncio
from async_simple_cache import acache, AsyncCache

@pytest.mark.asyncio
async def test_acache_decorator():
    call_count = 0
    
    @acache(ttl=2)
    async def expensive_function(x: int):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    result1 = await expensive_function(5)
    assert result1 == 10
    assert call_count == 1
    
    result2 = await expensive_function(5)
    assert result2 == 10
    assert call_count == 1
    
    result3 = await expensive_function(10)
    assert result3 == 20
    assert call_count == 2
    
    await asyncio.sleep(2.1)
    
    result4 = await expensive_function(5)
    assert result4 == 10
    assert call_count == 3

@pytest.mark.asyncio
async def test_acache_different_args():
    call_count = 0
    
    @acache()
    async def func(a, b, key="default"):
        nonlocal call_count
        call_count += 1
        return f"{a}-{b}-{key}"
    
    await func(1, 2)
    await func(1, 2)
    assert call_count == 1
    
    await func(1, 2, key="other")
    assert call_count == 2
    
    await func(2, 1)
    assert call_count == 3

@pytest.mark.asyncio
async def test_custom_cache_instance():
    cache1 = AsyncCache(default_ttl=1)
    cache2 = AsyncCache(default_ttl=10)
    
    call_count = 0
    
    @acache(cache=cache1)
    async def func1():
        nonlocal call_count
        call_count += 1
        return "value1"
    
    @acache(cache=cache2)
    async def func2():
        nonlocal call_count
        call_count += 1
        return "value2"
    
    await cache1.start()
    await cache2.start()
    
    await func1()
    await func1()
    await func2()
    await func2()
    
    assert call_count == 2
    
    await cache1.stop()
    await cache2.stop()