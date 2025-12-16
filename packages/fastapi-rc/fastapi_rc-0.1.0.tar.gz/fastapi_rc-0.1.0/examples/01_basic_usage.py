"""
ⒸAngelaMos | 2025
01_basic_usage.py

Basic fastapi-rc usage - simple cache aside pattern
"""

import json
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_rc import (
    cachemanager,
    RedisClient,
)


class Product(BaseModel):
    """
    Product model
    """
    id: str
    name: str
    price: float
    in_stock: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize Redis on startup, close on shutdown
    """
    cachemanager.init(
        redis_url = "redis://localhost:6379/0",
        max_connections = 50,
    )
    yield
    await cachemanager.close()


app = FastAPI(lifespan = lifespan)


async def fetch_product_from_db(product_id: str) -> dict:
    """
    Simulate database fetch
    """
    return {
        "id": product_id,
        "name": f"Product {product_id}",
        "price": 99.99,
        "in_stock": True,
    }


@app.get("/products/{product_id}")
async def get_product(product_id: str, redis: RedisClient):
    """
    Get product with cache-aside pattern
    """
    cache_key = f"products:{product_id}"

    cached = await redis.get(cache_key)
    if cached:
        return {
            "product": json.loads(cached),
            "cached": True,
        }

    product_data = await fetch_product_from_db(product_id)

    await redis.set(cache_key, json.dumps(product_data), ex = 300)

    return {
        "product": product_data,
        "cached": False,
    }


@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product: Product,
    redis: RedisClient,
):
    """
    Update product and invalidate cache
    """
    cache_key = f"products:{product_id}"

    await redis.delete(cache_key)

    return {
        "product": product,
        "cache_invalidated": True,
    }


@app.get("/health/redis")
async def redis_health():
    """
    Check Redis health
    """
    if not cachemanager.is_available:
        return {"status": "unavailable"}

    if await cachemanager.ping():
        return {"status": "healthy"}

    return {"status": "unhealthy"}


if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
