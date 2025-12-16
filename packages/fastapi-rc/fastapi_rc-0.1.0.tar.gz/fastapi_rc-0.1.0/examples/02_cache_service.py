"""
ⒸAngelaMos | 2025
02_cache_service.py

Advanced usage with CacheService wrapper
"""

import uvicorn
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
)
from pydantic import (
    BaseModel,
    Field,
)

from fastapi_rc import (
    cachemanager,
    RedisClient,
    CacheService,
)


class User(BaseModel):
    """
    User model
    """
    id: str
    email: str
    name: str
    role: str


class UserCreate(BaseModel):
    """
    User creation schema
    """
    email: str = Field(..., min_length = 3)
    name: str = Field(..., min_length = 1)
    role: str = "user"


class UserUpdate(BaseModel):
    """
    User update schema
    """
    name: str | None = None
    role: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize Redis with production config
    """
    cachemanager.init(
        redis_url = "redis://localhost:6379/0",
        max_connections = 50,
        socket_timeout = 5.0,
        socket_connect_timeout = 2.0,
        health_check_interval = 30,
    )
    yield
    await cachemanager.close()


app = FastAPI(lifespan = lifespan)


async def get_user_cache(redis: RedisClient) -> CacheService[User]:
    """
    Custom cache dependency for users

    10 minute TTL with jitter to prevent stampedes
    """
    return CacheService(
        redis,
        namespace = "users",
        model = User,
        default_ttl = 600,
        use_jitter = True,
        prefix = "api",
        version = "v1",
    )


UserCache = Annotated[CacheService[User], Depends(get_user_cache)]


async def fetch_user_from_db(user_id: str) -> User:
    """
    Simulate database fetch
    """
    if user_id == "999":
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )

    return User(
        id = user_id,
        email = f"user{user_id}@example.com",
        name = f"User {user_id}",
        role = "user",
    )


@app.get("/users/{user_id}", response_model = User)
async def get_user(user_id: str, user_cache: UserCache):
    """
    Get user with cache-aside pattern

    Automatically caches miss, returns cached hit
    """
    user = await user_cache.get_or_set(
        identifier = user_id,
        factory = lambda: fetch_user_from_db(user_id),
        ttl = 600,
    )

    return user


@app.post(
    "/users",
    response_model = User,
    status_code = status.HTTP_201_CREATED
)
async def create_user(data: UserCreate, user_cache: UserCache):
    """
    Create user and cache immediately
    """
    user = User(
        id = "new_123",
        email = data.email,
        name = data.name,
        role = data.role,
    )

    await user_cache.set(
        identifier = user.id,
        value = user,
        ttl = 600,
    )

    return user


@app.put("/users/{user_id}", response_model = User)
async def update_user(
    user_id: str,
    data: UserUpdate,
    user_cache: UserCache,
):
    """
    Update user and proactively invalidate cache
    """
    existing = await user_cache.get(user_id)
    if not existing:
        existing = await fetch_user_from_db(user_id)

    updated = existing.model_copy(
        update = data.model_dump(exclude_unset = True)
    )

    await user_cache.set(user_id, updated)

    return updated


@app.delete("/users/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, user_cache: UserCache):
    """
    Delete user and invalidate cache
    """
    deleted = await user_cache.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found in cache",
        )


@app.post("/users/{user_id}/invalidate")
async def invalidate_user_cache(user_id: str, user_cache: UserCache):
    """
    Manually invalidate all user related cache entries
    """
    deleted = await user_cache.delete(user_id)

    pattern_count = await user_cache.invalidate_pattern(f"{user_id}:*")

    return {
        "invalidated": deleted,
        "pattern_invalidated": pattern_count,
    }


@app.get("/cache/stats")
async def cache_stats(user_cache: UserCache):
    """
    Get cache statistics for monitoring
    """
    user_exists = await user_cache.exists("1")
    user_ttl = await user_cache.get_ttl("1") if user_exists else None

    return {
        "namespace": user_cache.namespace,
        "prefix": user_cache.prefix,
        "version": user_cache.version,
        "default_ttl": user_cache.default_ttl,
        "jitter_enabled": user_cache.use_jitter,
        "sample_key_exists": user_exists,
        "sample_key_ttl": user_ttl,
    }


if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
