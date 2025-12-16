=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

----

[Unreleased]
============

Nothing yet.

----

[0.1.0] - 2025-12-13
====================

Initial release.

Added
-----

- ``CacheManager`` for Redis connection lifecycle management
- ``CacheService`` generic wrapper for cache-aside patterns with Pydantic models
- FastAPI dependency injection via ``RedisClient`` and ``CacheServiceDep``
- Automatic connection pooling with configurable limits (10-200 connections)
- Built-in retry logic with exponential backoff (handles ConnectionError, TimeoutError)
- Health check support via ``ping()`` method
- TTL jitter to prevent cache stampedes (``get_ttl_with_jitter``)
- Pattern-based cache invalidation using SCAN (``invalidate_pattern``)
- Type-safe Pydantic model caching with automatic serialization
- Pipeline support for batch operations
- Key generation utilities (``build_cache_key``)
- Comprehensive README with usage patterns
- Full type hints and mypy compatibility
- Production-ready error handling with graceful degradation

Features
--------

- Three levels of control: direct Redis client, CacheService wrapper, custom per-domain caches
- Zero external dependencies beyond redis[hiredis], fastapi, and pydantic
- Clean FastAPI-native DI patterns that mirror database session management
- Configurable key prefixes and versioning for cache invalidation strategies
- Support for query parameter hashing in cache keys
