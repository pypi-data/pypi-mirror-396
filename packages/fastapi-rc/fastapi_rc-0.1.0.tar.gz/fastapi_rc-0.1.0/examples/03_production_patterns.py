"""
ⒸAngelaMos | 2025
03_production_patterns.py

Caching patterns for enterprise applications
"""

import json
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
    get_ttl_with_jitter,
)


class Product(BaseModel):
    """
    Product model
    """
    id: str
    name: str
    category: str
    price: float
    in_stock: bool
    created_at: datetime


class ProductList(BaseModel):
    """
    Paginated product list
    """
    items: list[Product]
    total: int
    page: int
    per_page: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Production lifespan with full configuration
    """
    cachemanager.init(
        redis_url = "redis://localhost:6379/0",
        max_connections = 100,
        socket_timeout = 5.0,
        socket_connect_timeout = 2.0,
        health_check_interval = 30,
        decode_responses = True,
    )
    yield
    await cachemanager.close()


app = FastAPI(
    title = "Product API with Redis Caching",
    lifespan = lifespan,
)


async def get_product_cache(redis: RedisClient) -> CacheService[Product]:
    """
    Product cache with 15 minute TTL
    """
    return CacheService(
        redis,
        namespace = "products",
        model = Product,
        default_ttl = 900,
        use_jitter = True,
        prefix = "api",
        version = "v1",
    )


ProductCache = Annotated[CacheService[Product], Depends(get_product_cache)]


async def fetch_product_from_db(product_id: str) -> Product:
    """
    Simulate expensive database query
    """
    return Product(
        id = product_id,
        name = f"Product {product_id}",
        category = "electronics",
        price = 299.99,
        in_stock = True,
        created_at = datetime.now(),
    )


async def fetch_products_from_db(
    category: str | None,
    page: int,
    per_page: int,
) -> ProductList:
    """
    Simulate expensive database query with filters
    """
    products = [
        Product(
            id = str(i),
            name = f"{category or 'General'} Product {i}",
            category = category or "general",
            price = 99.99 * i,
            in_stock = i % 2 == 0,
            created_at = datetime.now(),
        ) for i in range((page - 1) * per_page, page * per_page)
    ]

    return ProductList(
        items = products,
        total = 100,
        page = page,
        per_page = per_page,
    )


@app.get("/products/{product_id}", response_model = Product)
async def get_product(product_id: str, product_cache: ProductCache):
    """
    Pattern 1: Simple cache-aside with CacheService
    """
    product = await product_cache.get_or_set(
        identifier = product_id,
        factory = lambda: fetch_product_from_db(product_id),
    )

    return product


@app.get("/products", response_model = ProductList)
async def list_products(
    category: str | None = None,
    page: int = Query(default = 1,
                      ge = 1),
    per_page: int = Query(default = 20,
                          ge = 1,
                          le = 100),
    redis: RedisClient = Depends(),
):
    """
    Pattern 2: Query parameter caching with hash
    """
    product_cache = CacheService(
        redis,
        namespace = "products",
        default_ttl = 300,
        prefix = "api",
        version = "v1",
    )

    products = await product_cache.get_or_set(
        identifier = "list",
        factory = lambda: fetch_products_from_db(category, page, per_page),
        params = {
            "category": category,
            "page": page,
            "per_page": per_page
        },
        ttl = 180,
    )

    return products


@app.post("/products/batch", status_code = status.HTTP_201_CREATED)
async def batch_create_products(
    products: list[Product],
    redis: RedisClient
):
    """
    Pattern 3: Batch caching with Redis pipeline
    """
    async with redis.pipeline(transaction = False) as pipe:
        for product in products:
            cache_key = f"api:v1:products:{product.id}"
            pipe.set(
                cache_key,
                product.model_dump_json(),
                ex = get_ttl_with_jitter(900),
            )
        await pipe.execute()

    return {
        "created": len(products),
        "cached": True,
    }


@app.put("/products/{product_id}/stock")
async def update_stock(
    product_id: str,
    in_stock: bool,
    redis: RedisClient,
):
    """
    Pattern 4: Granular cache invalidation
    """
    product_key = f"api:v1:products:{product_id}"

    cached = await redis.get(product_key)
    if cached:
        product_data = json.loads(cached)
        product_data["in_stock"] = in_stock
        await redis.set(product_key, json.dumps(product_data), ex = 900)

    async for key in redis.scan_iter("api:v1:products:list:*"):
        await redis.delete(key)

    return {"product_id": product_id, "in_stock": in_stock}


@app.delete("/categories/{category_id}")
async def delete_category(category_id: str, redis: RedisClient):
    """
    Pattern 5: Cascade invalidation on category deletion
    """
    count = 0

    async for key in redis.scan_iter(
            f"api:v1:products:*:*category*{category_id}*"):
        await redis.delete(key)
        count += 1

    return {
        "category_deleted": category_id,
        "cache_entries_invalidated": count,
    }


@app.get("/cache/info")
async def cache_info(redis: RedisClient):
    """
    Production monitoring endpoint
    """
    info = await redis.info()

    total_hits = info.get("keyspace_hits", 0)
    total_misses = info.get("keyspace_misses", 1)
    hit_rate = (total_hits / (total_hits + total_misses)) * 100

    return {
        "server": {
            "version": info.get("redis_version",
                                "unknown"),
            "uptime_days": info.get("uptime_in_days",
                                    0),
            "connected_clients": info.get("connected_clients",
                                          0),
        },
        "memory": {
            "used_memory_human": info.get("used_memory_human",
                                          "unknown"),
            "maxmemory_human": info.get("maxmemory_human",
                                        "unlimited"),
        },
        "stats": {
            "total_commands": info.get("total_commands_processed",
                                       0),
            "keyspace_hits": total_hits,
            "keyspace_misses": total_misses,
            "hit_rate_percent": round(hit_rate,
                                      2),
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host = "0.0.0.0",
        port = 8000,
        log_level = "info",
    )
