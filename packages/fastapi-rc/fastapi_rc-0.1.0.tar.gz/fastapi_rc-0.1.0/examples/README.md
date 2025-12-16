# fastapi-rc Examples

Examples demonstrating real world usage patterns.

## Running the Examples

All examples are runnable FastAPI applications:

```bash
# Install dependencies
pip install fastapi-rc uvicorn

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Run any example
python examples/01_basic_usage.py
```

Then visit http://localhost:8000/docs for interactive API documentation.

---

## Examples Overview

### 01_basic_usage.py

**Basic cache-aside pattern with direct Redis client**

- Simple get/set caching
- Cache invalidation on updates
- Health check endpoint

**Use when**: You need full control and simple caching logic

---

### 02_cache_service.py

**CacheService wrapper for common patterns**

- Generic `CacheService[T]` with Pydantic models
- Custom cache dependencies per domain
- Full CRUD with automatic cache management
- Pattern-based invalidation
- Cache statistics endpoint

**Use when**: You want cleaner code with built-in cache-aside patterns

---

### 03_production_patterns.py

**Production-ready patterns for enterprise applications**

- Multi-domain caching (products with different TTLs)
- Query parameter caching with automatic hashing
- Batch operations with Redis pipeline
- Granular invalidation strategies
- Cascade invalidation (delete category → invalidate all products)
- Cache warmup on deployment
- Production monitoring endpoint

**Use when**: Building real applications that need robust caching

---

### 04_full_api_example.py

**Complete E-commerce API with advanced caching**

- Multiple cache layers (users, products, orders)
- Different TTL strategies per domain (10min, 30min, 5min)
- Multi-cache coordination (order creation touches 3 caches)
- Aggregate stats with separate caching
- Emergency cache flush endpoints
- Production health checks

**Use when**: You need reference architecture for complex applications

---

## Key Patterns Demonstrated

### 1. Direct Redis Client

```python
from fastapi_rc import RedisClient

@app.get("/items/{id}")
async def get_item(id: str, redis: RedisClient):
    cached = await redis.get(f"items:{id}")
    if cached:
        return json.loads(cached)
    # ...
```

**Best for**: Full control, custom logic, batch operations

### 2. CacheService Wrapper

```python
from fastapi_rc import CacheService, RedisClient

@app.get("/items/{id}")
async def get_item(id: str, redis: RedisClient):
    cache = CacheService(redis, "items", model=Item, default_ttl=600)
    return await cache.get_or_set(id, factory=lambda: fetch_item(id))
```

**Best for**: Standard cache-aside, cleaner code, Pydantic models

### 3. Custom Per-Domain Cache

```python
async def get_user_cache(redis: RedisClient) -> CacheService[User]:
    return CacheService(redis, "users", model=User, default_ttl=600)

UserCache = Annotated[CacheService[User], Depends(get_user_cache)]

@app.get("/users/{id}")
async def get_user(id: str, user_cache: UserCache):
    return await user_cache.get_or_set(id, factory=lambda: fetch_user(id))
```

**Best for**: Consistent caching strategy across your application

---

## Testing the Examples

Each example includes health check endpoints:

```bash
# Basic health
curl http://localhost:8000/health

# Redis-specific health
curl http://localhost:8000/health/redis

# Cache stats (some examples)
curl http://localhost:8000/cache/stats
```

---

## Production Checklist

When adapting these examples for production:

- [ ] Use TLS Redis connection (`rediss://`)
- [ ] Configure authentication
- [ ] Set appropriate `max_connections` (2-3x concurrent requests)
- [ ] Add monitoring for cache hit rate
- [ ] Implement cache warmup on deployment
- [ ] Add proper error handling/logging
- [ ] Use environment variables for configuration
- [ ] Test cache invalidation strategies
- [ ] Monitor memory usage
- [ ] Set up Redis persistence (AOF/RDB)

---

## Next Steps

1. Start with `01_basic_usage.py` to understand fundamentals
2. Move to `02_cache_service.py` to see cleaner patterns
3. Study `03_production_patterns.py` for real-world techniques
4. Reference `04_full_api_example.py` for architecture guidance

Then adapt the patterns that fit your application's needs.
