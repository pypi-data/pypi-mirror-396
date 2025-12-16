"""
ⒸAngelaMos | 2025
client.py
"""

import logging
import contextlib
from collections.abc import AsyncIterator

import redis.asyncio as redis
from redis.asyncio import (
    Redis,
    ConnectionPool,
)
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialWithJitterBackoff
from redis.exceptions import (
    TimeoutError,
    ConnectionError,
    BusyLoadingError,
)


logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages Redis connections and client lifecycle
    """
    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    def init(
        self,
        redis_url: str | None = None,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 2.0,
        health_check_interval: int = 30,
        decode_responses: bool = True,
    ) -> None:
        """
        Initialize Redis connection pool and client

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            max_connections: Maximum number of connections in pool (10-200)
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            health_check_interval: Health check ping interval in seconds
            decode_responses: Auto-decode bytes to strings
        """
        if redis_url is None:
            logger.warning(
                "Redis URL not provided - cache will be disabled"
            )
            return

        retry = Retry(
            backoff = ExponentialWithJitterBackoff(base = 1, cap = 10),
            retries = 5,
            supported_errors = (
                ConnectionError,
                TimeoutError,
                BusyLoadingError,
            ),
        )

        self._pool = ConnectionPool.from_url(
            redis_url,
            max_connections = max_connections,
            socket_timeout = socket_timeout,
            socket_connect_timeout = socket_connect_timeout,
            socket_keepalive = True,
            health_check_interval = health_check_interval,
            decode_responses = decode_responses,
            retry = retry,
        )

        self._client = Redis.from_pool(self._pool)
        logger.info(
            f"Redis connection pool initialized (max_connections={max_connections})"
        )

    async def close(self) -> None:
        """
        Close Redis client and dispose of connection pool
        """
        if self._client:
            await self._client.aclose()
            self._client = None
            self._pool = None
            logger.info("Redis connection pool closed")

    async def ping(self) -> bool:
        """
        Health check - ping Redis server
        """
        if not self._client:
            return False

        try:
            return await self._client.ping()
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            return False

    @property
    def client(self) -> Redis:
        """
        Get Redis client instance
        """
        if self._client is None:
            raise RuntimeError("CacheManager is not initialized")
        return self._client

    @property
    def is_available(self) -> bool:
        """
        Check if Redis is available
        """
        return self._client is not None

    @contextlib.asynccontextmanager
    async def pipeline(
        self,
        transaction: bool = True
    ) -> AsyncIterator[redis.client.Pipeline]:
        """
        Context manager for Redis pipeline operations
        """
        if not self._client:
            raise RuntimeError("CacheManager is not initialized")

        async with self._client.pipeline(transaction = transaction) as pipe:
            yield pipe


cachemanager = CacheManager()
