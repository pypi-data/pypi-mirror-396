"""
ⒸAngelaMos | 2025
04_full_api_example.py

API example with multi domain caching strategy
"""

import uvicorn
from typing import Annotated
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Depends,
    Query,
    status,
)
from pydantic import BaseModel

from fastapi_rc import (
    cachemanager,
    RedisClient,
    CacheService,
)


class User(BaseModel):
    """
    User entity
    """
    id: str
    email: str
    name: str
    created_at: datetime


class Product(BaseModel):
    """
    Product entity
    """
    id: str
    name: str
    price: float
    stock: int


class Order(BaseModel):
    """
    Order entity with computed total
    """
    id: str
    user_id: str
    product_ids: list[str]
    total: float
    created_at: datetime


class Stats(BaseModel):
    """
    Aggregated statistics
    """
    total_users: int
    total_products: int
    total_orders: int
    revenue: float
    cache_hit_rate: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan with Redis initialization
    """
    cachemanager.init(
        redis_url = "redis://localhost:6379/0",
        max_connections = 100,
        socket_timeout = 5.0,
        health_check_interval = 30,
    )
    yield
    await cachemanager.close()


app = FastAPI(
    title = "E-Commerce API",
    description = "Multi domain caching strategy example",
    version = "1.0.0",
    lifespan = lifespan,
)


async def get_user_cache(redis: RedisClient) -> CacheService[User]:
    """
    User cache: 10 minute TTL (frequently accessed)
    """
    return CacheService(
        redis,
        namespace = "users",
        model = User,
        default_ttl = 600,
        use_jitter = True,
        prefix = "ecommerce",
        version = "v1",
    )


async def get_product_cache(redis: RedisClient) -> CacheService[Product]:
    """
    Product cache: 30 minute TTL (semi-static data)
    """
    return CacheService(
        redis,
        namespace = "products",
        model = Product,
        default_ttl = 1800,
        use_jitter = True,
        prefix = "ecommerce",
        version = "v1",
    )


async def get_order_cache(redis: RedisClient) -> CacheService[Order]:
    """
    Order cache: 5 minute TTL (frequently changing)
    """
    return CacheService(
        redis,
        namespace = "orders",
        model = Order,
        default_ttl = 300,
        use_jitter = True,
        prefix = "ecommerce",
        version = "v1",
    )


UserCache = Annotated[CacheService[User], Depends(get_user_cache)]
ProductCache = Annotated[CacheService[Product], Depends(get_product_cache)]
OrderCache = Annotated[CacheService[Order], Depends(get_order_cache)]


async def fetch_user(user_id: str) -> User:
    """
    Simulate database query
    """
    return User(
        id = user_id,
        email = f"user{user_id}@example.com",
        name = f"User {user_id}",
        created_at = datetime.now(),
    )


async def fetch_product(product_id: str) -> Product:
    """
    Simulate database query
    """
    return Product(
        id = product_id,
        name = f"Product {product_id}",
        price = 99.99,
        stock = 50,
    )


@app.get("/users/{user_id}", response_model = User)
async def get_user(user_id: str, user_cache: UserCache):
    """
    Get user with cache
    """
    return await user_cache.get_or_set(
        identifier = user_id,
        factory = lambda: fetch_user(user_id),
    )


@app.get("/products/{product_id}", response_model = Product)
async def get_product(product_id: str, product_cache: ProductCache):
    """
    Get product with cache
    """
    return await product_cache.get_or_set(
        identifier = product_id,
        factory = lambda: fetch_product(product_id),
    )


@app.post(
    "/orders",
    response_model = Order,
    status_code = status.HTTP_201_CREATED
)
async def create_order(
    user_id: str,
    product_ids: list[str],
    user_cache: UserCache,
    product_cache: ProductCache,
    order_cache: OrderCache,
    redis: RedisClient,
):
    """
    Create order with multi-cache coordination

    Pattern: Cache user, products, then order creation
    """
    user = await user_cache.get_or_set(
        identifier = user_id,
        factory = lambda: fetch_user(user_id),
    )

    products: list[Product] = []
    for product_id in product_ids:
        product = await product_cache.get_or_set(
            identifier = product_id,
            factory = lambda pid = product_id: fetch_product(pid),
        )
        products.append(product)

    total = sum(p.price for p in products)

    order = Order(
        id = "order_123",
        user_id = user.id,
        product_ids = product_ids,
        total = total,
        created_at = datetime.now(),
    )

    await order_cache.set(
        identifier = order.id,
        value = order,
        ttl = 300,
    )

    async for key in redis.scan_iter(
            f"ecommerce:v1:orders:user:{user_id}:*"):
        await redis.delete(key)

    return order


@app.get("/orders/user/{user_id}")
async def get_user_orders(
    user_id: str,
    page: int = Query(default = 1,
                      ge = 1),
    redis: RedisClient = Depends(),
):
    """
    Get user orders with pagination caching
    """
    order_cache = CacheService(
        redis,
        namespace = "orders",
        default_ttl = 180,
        prefix = "ecommerce",
        version = "v1",
    )

    async def fetch_orders():
        return {
            "orders": [
                {
                    "id": f"order_{i}",
                    "user_id": user_id,
                    "total": 99.99 * i,
                } for i in range(1, 6)
            ],
            "page":
            page,
        }

    orders = await order_cache.get_or_set(
        identifier = f"user:{user_id}",
        factory = fetch_orders,
        params = {"page": page},
    )

    return orders


@app.get("/stats", response_model = Stats)
async def get_platform_stats(redis: RedisClient):
    """
    Aggregate stats with 5-minute cache
    """
    cache_key = "ecommerce:v1:stats:platform"

    cached = await redis.get(cache_key)
    if cached:
        return Stats.model_validate_json(cached)

    info = await redis.info()
    total_hits = info.get("keyspace_hits", 0)
    total_misses = info.get("keyspace_misses", 1)
    hit_rate = (total_hits / (total_hits + total_misses)) * 100

    stats = Stats(
        total_users = 1000,
        total_products = 500,
        total_orders = 250,
        revenue = 25000.00,
        cache_hit_rate = round(hit_rate,
                               2),
    )

    await redis.set(cache_key, stats.model_dump_json(), ex = 300)

    return stats


@app.post("/products/{product_id}/stock")
async def update_product_stock(
    product_id: str,
    stock: int,
    product_cache: ProductCache,
    redis: RedisClient,
):
    """
    Update stock and invalidate related caches

    Pattern: Granular + cascade invalidation
    """
    await product_cache.delete(product_id)

    async for key in redis.scan_iter("ecommerce:v1:products:list:*"):
        await redis.delete(key)

    return {
        "product_id": product_id,
        "stock": stock,
        "cache_invalidated": True,
    }


@app.post("/cache/warmup")
async def warmup_cache(
    user_cache: UserCache,
    product_cache: ProductCache,
):
    """
    Warmup cache with frequently accessed items

    Pattern: Pre-populate cache on deployment
    """
    warmed_users = 0
    warmed_products = 0

    for user_id in ["1", "2", "3", "4", "5"]:
        user = await fetch_user(user_id)
        await user_cache.set(user_id, user)
        warmed_users += 1

    for product_id in ["1", "2", "3", "4", "5"]:
        product = await fetch_product(product_id)
        await product_cache.set(product_id, product)
        warmed_products += 1

    return {
        "warmed_users": warmed_users,
        "warmed_products": warmed_products,
    }


@app.delete("/cache/flush/{namespace}")
async def flush_namespace(namespace: str, redis: RedisClient):
    """
    Flush entire cache namespace

    Pattern: Emergency cache invalidation
    """
    count = 0

    async for key in redis.scan_iter(f"ecommerce:v1:{namespace}:*"):
        await redis.delete(key)
        count += 1

    return {
        "namespace": namespace,
        "keys_deleted": count,
    }


@app.get("/health")
async def health_check():
    """
    Basic health check
    """
    redis_healthy = await cachemanager.ping(
    ) if cachemanager.is_available else False

    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "healthy" if redis_healthy else "unavailable",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host = "0.0.0.0",
        port = 8000,
        log_level = "info",
    )
