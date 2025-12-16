# fastapi-rc

**Redis caching for FastAPI with full control and clean DI patterns.**

Unlike basic FastAPI cache packages, `fastapi-rc` gives you **three levels of flexibility**:

1. **Direct Redis client** - Full control for complex operations
2. **CacheService wrapper** - Common patterns made easy (cache-aside, invalidation, TTL management)
3. **FastAPI DI integration** - Clean dependency injection that flows naturally with your existing patterns

Zero magic, zero lock in. Just Redis primitives with FastAPI native patterns.

---

## Why fastapi-rc?

**Problem with existing packages:**
- `fastapi-cache2` forces decorator magic (limited flexibility)
- Direct `redis-py` requires boilerplate for every endpoint
- Most packages lack enterprise features (connection pooling, retries, health checks, invalidation)

**fastapi-rc solves this:**
- ✅ Production-ready from day 1 (connection pooling, retries, graceful degradation)
- ✅ Three levels of control (direct client, service wrapper, custom per-domain caches)
- ✅ Type-safe with Pydantic models (`CacheService[User]`)
- ✅ FastAPI-native DI (looks like your database sessions)
- ✅ Configurable everything (no hardcoded settings)

---

## Installation

```bash
pip install fastapi-rc
```

Requires Python 3.12+ and includes `hiredis` for 2-3x performance boost.

---

## Quick Start

### 1. Initialize in your FastAPI lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_rc import cachemanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cachemanager.init(
        redis_url="redis://localhost:6379/0",
        max_connections=50,
        socket_timeout=5.0,
    )
    yield
    # Shutdown
    await cachemanager.close()

app = FastAPI(lifespan=lifespan)
```

### 2. Use in routes

```python
from fastapi import APIRouter
from fastapi_rc import RedisClient, CacheServiceDep

router = APIRouter()

# Pattern 1: Direct Redis (full control)
@router.get("/users/{user_id}")
async def get_user(user_id: str, redis: RedisClient):
    cached = await redis.get(f"users:{user_id}")
    if cached:
        return {"user": json.loads(cached), "cached": True}

    user = await fetch_user_from_db(user_id)
    await redis.set(f"users:{user_id}", json.dumps(user), ex=300)
    return {"user": user, "cached": False}


# Pattern 2: CacheService (common patterns)
@router.get("/products")
async def list_products(cache: CacheServiceDep):
    products = await cache.get_or_set(
        identifier="all_products",
        factory=lambda: fetch_all_products_from_db(),
        ttl=600
    )
    return products
```

---

## Usage Patterns

### Pattern 1: Direct Redis Client (Maximum Control)

```python
from fastapi_rc import RedisClient

@router.post("/batch")
async def batch_operation(redis: RedisClient):
    # Pipeline for bulk operations
    async with redis.pipeline(transaction=False) as pipe:
        for item in items:
            pipe.set(f"item:{item.id}", item.json(), ex=300)
        await pipe.execute()

    # Pattern-based invalidation
    async for key in redis.scan_iter("users:123:*"):
        await redis.delete(key)
```

### Pattern 2: CacheService Wrapper (Common Patterns)

```python
from fastapi_rc import CacheService, RedisClient
from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str

@router.get("/users/{user_id}")
async def get_user(user_id: str, redis: RedisClient):
    user_cache = CacheService(
        redis,
        namespace="users",
        model=User,
        default_ttl=600,
        use_jitter=True  # Prevents cache stampedes
    )

    # Cache-aside pattern (auto-fetch if missing)
    user = await user_cache.get_or_set(
        identifier=user_id,
        factory=lambda: db.get_user(user_id)
    )
    return user
```

### Pattern 3: Custom Per-Domain Cache

```python
# Custom dependency for your facet/domain
from typing import Annotated
from fastapi import Depends

async def get_gym_cache(redis: RedisClient) -> CacheService:
    return CacheService(
        redis,
        namespace="gym",
        default_ttl=1800,  # 30 minutes
        prefix="myapp",
        version="v1"
    )

GymCache = Annotated[CacheService, Depends(get_gym_cache)]

@router.get("/gym/stats/{user_id}")
async def get_gym_stats(user_id: str, gym_cache: GymCache):
    stats = await gym_cache.get_or_set(
        identifier=user_id,
        factory=lambda: calculate_gym_stats(user_id)
    )
    return stats
```

---

## Advanced Features

### Cache Invalidation

```python
# Proactive deletion on write
@router.put("/users/{user_id}")
async def update_user(user_id: str, data: UserUpdate, redis: RedisClient):
    updated = await db.update_user(user_id, data)

    # Delete exact keys
    await redis.delete(f"users:{user_id}")

    # Pattern-based invalidation
    async for key in redis.scan_iter(f"users:{user_id}:*"):
        await redis.delete(key)

    return updated


# Or with CacheService
@router.delete("/products/{product_id}")
async def delete_product(product_id: str, redis: RedisClient):
    product_cache = CacheService(redis, "products")

    # Delete specific entry
    await product_cache.delete(product_id)

    # Invalidate all related entries
    count = await product_cache.invalidate_pattern(f"{product_id}:*")

    return {"deleted": True, "cache_invalidated": count}
```

### TTL Strategies

```python
from fastapi_rc import get_ttl_with_jitter

# Sessions (security-driven)
session_ttl = 1800  # 30 min

# Static config (rarely changes)
config_ttl = 86400  # 24 hrs

# Product catalog (balance freshness + load)
product_ttl = 900  # 15 min

# Search results (high change rate)
search_ttl = 60  # 1 min

# With jitter to prevent stampedes
ttl = get_ttl_with_jitter(base_ttl=300, jitter_percent=0.1)  # 300s ± 30s
```

### Graceful Degradation

```python
# CacheService already handles errors gracefully
@router.get("/users/{user_id}")
async def get_user(user_id: str, redis: RedisClient):
    user_cache = CacheService(redis, "users")

    # Returns None if cache fails (doesn't crash)
    cached = await user_cache.get(user_id)
    if cached:
        return cached

    # Fallback to database
    return await db.get_user(user_id)
```

---

## Configuration

All settings are passed to `cachemanager.init()`:

```python
cachemanager.init(
    redis_url="redis://localhost:6379/0",      # Required
    max_connections=50,                         # Pool size (10-200)
    socket_timeout=5.0,                         # Socket timeout (seconds)
    socket_connect_timeout=2.0,                 # Connect timeout
    health_check_interval=30,                   # Ping interval
    decode_responses=True,                      # Auto-decode bytes to strings
)
```

### CacheService Options

```python
cache = CacheService(
    redis=redis_client,                         # Required: Redis client
    namespace="users",                          # Required: Cache namespace
    model=User,                                 # Optional: Pydantic model for validation
    default_ttl=300,                            # Default: 300 seconds
    use_jitter=True,                            # Add TTL jitter (prevents stampedes)
    prefix="myapp",                             # Key prefix (default: "cache")
    version="v1",                               # Cache version (for invalidation)
)
```

---

## Health Checks

```python
@router.get("/health/redis")
async def redis_health():
    if not cachemanager.is_available:
        return {"status": "unavailable"}

    if await cachemanager.ping():
        return {"status": "healthy"}

    return {"status": "unhealthy"}
```

---

## Testing

Use `fakeredis` for unit tests:

```python
import pytest
from fakeredis import FakeAsyncRedis
from fastapi_rc import cachemanager

@pytest.fixture
async def fake_redis():
    return FakeAsyncRedis()

@pytest.fixture
def app_with_cache(fake_redis):
    # Override real Redis with fake
    cachemanager._client = fake_redis
    yield app
    cachemanager._client = None

def test_cached_endpoint(app_with_cache):
    client = TestClient(app_with_cache)

    # First request - cache miss
    response1 = client.get("/users/123")
    assert response1.json()["cached"] == False

    # Second request - cache hit
    response2 = client.get("/users/123")
    assert response2.json()["cached"] == True
```

---

## API Reference

### `CacheManager`

| Method | Description |
|--------|-------------|
| `init(redis_url, **options)` | Initialize connection pool |
| `close()` | Close all connections |
| `ping()` | Health check (returns bool) |
| `client` | Get Redis client (property) |
| `is_available` | Check if Redis available (property) |
| `pipeline(transaction=True)` | Context manager for pipelines |

### `CacheService[T]`

| Method | Signature | Description |
|--------|-----------|-------------|
| `get` | `(identifier, params=None) -> T \| None` | Get cached value |
| `set` | `(identifier, value, ttl=None, params=None) -> bool` | Set cached value |
| `delete` | `(identifier, params=None) -> bool` | Delete cached value |
| `exists` | `(identifier, params=None) -> bool` | Check if key exists |
| `get_or_set` | `(identifier, factory, ttl=None, params=None) -> T` | Cache-aside pattern |
| `invalidate_pattern` | `(pattern="*") -> int` | Delete keys matching pattern |
| `get_ttl` | `(identifier, params=None) -> int` | Get remaining TTL |

### Utility Functions

| Function | Description |
|----------|-------------|
| `build_cache_key(namespace, identifier, params=None, prefix="cache", version="v1")` | Generate cache keys |
| `get_ttl_with_jitter(base_ttl, jitter_percent=0.1)` | Add random TTL variance |
| `invalidate_pattern(namespace, pattern="*", prefix="cache", version="v1")` | Build invalidation patterns |

---

## Performance Tips

1. **Install with hiredis**: Already included - provides 2-3x performance boost
2. **Connection pooling**: Automatic - no per-request connections
3. **Pipeline bulk operations**: Use `async with redis.pipeline()` for batches
4. **Add jitter to TTL**: Prevents cache stampedes on expiration
5. **Use SCAN not KEYS**: Already used in `invalidate_pattern()`

---

## Examples

See the [examples/](./examples/) directory for full working examples:

- **01_basic_usage.py** - Simple cache-aside with direct Redis
- **02_cache_service.py** - CacheService wrapper patterns
- **03_production_patterns.py** - Enterprise-grade caching strategies
- **04_full_api_example.py** - Complete multi-domain API reference

---

## License

MIT License - see [LICENSE](./LICENSE)

---

## Contributing

Issues and PRs welcome at [github.com/CarterPerez-dev/fastapi-rc](https://github.com/CarterPerez-dev/fastapi-rc)
