import json, inspect
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
from functools import wraps
from app.core.config import settings


async_redis_client = Redis.from_url(settings.redis_caching_url, decode_responses=True)


async def get_cache(key: str):
    data = await async_redis_client.get(key)
    
    return json.loads(data) if data else None


async def set_cache(key: str, data: dict, expire: int = 60):
    await async_redis_client.set(key, json.dumps(data), ex=expire)


async def delete_cache(key: str):
    await async_redis_client.delete(key)


async def delete_cache_pattern(pattern: str):
    keys = async_redis_client.scan_iter(match=pattern)
    
    async for key in keys:
        await async_redis_client.delete(key)


def cache(key: str, ttl: int = 30):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            
            signature = inspect.signature(function)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments
            
            try:
                final_key = key.format(**all_args)
            except KeyError as e:
                print(f"Cache key error: {e}")
                final_key = key
            
            data = await get_cache(final_key)
            
            if data:
                print(f"Loading {final_key} from cache...")
                return data
            else:
                print(f"Loading {final_key} from the database...")
                if inspect.iscoroutinefunction(function):
                    result = await function(*args, **kwargs)
                else:
                    result = function(*args, **kwargs)
                
                await set_cache(final_key, jsonable_encoder(result), ttl)
                return result
            
        return wrapper
    return decorator
                









