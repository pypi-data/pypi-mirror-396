"""
ⒸAngelaMos | 2025
__init__.py

fastapi-rc: Enterprise grade Redis caching for FastAPI
"""

__version__ = "0.1.0"

from fastapi_rc.client import (
    CacheManager,
    cachemanager,
)
from fastapi_rc.service import CacheService
from fastapi_rc.dependencies import (
    get_redis_client,
    get_cache_service,
    RedisClient,
    CacheServiceDep,
)
from fastapi_rc.keys import (
    build_cache_key,
    get_ttl_with_jitter,
    invalidate_pattern,
)

__all__ = [
    "CacheManager",
    "CacheService",
    "CacheServiceDep",
    "RedisClient",
    "build_cache_key",
    "cachemanager",
    "get_cache_service",
    "get_redis_client",
    "get_ttl_with_jitter",
    "invalidate_pattern",
]
