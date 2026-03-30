"""
ASC - Умный кэш для асинхронных функций к вашим услугам
"""

from .core import AsyncCache
from .decorators import acache, acache_with_args
from .backends.memory import MemoryBackend
from .backends.redis_backend import RedisBackend

__version__ = "0.1.0"
__all__ = [
    "AsyncCache",
    "acache",
    "acache_with_args",
    "MemoryBackend",
    "RedisBackend",
]