import json, redis, inspect
from fastapi.encoders import jsonable_encoder
from functools import wraps
from app.core.config import settings


redis_client = redis.from_url(settings.redis_caching_url, decode_responses=True)


def get_cache(key: str):
    data = redis_client.get(key)
    
    return json.loads(data) if data else None


def set_cache(key: str, data: dict, expire: int = 60):
    redis_client.set(key, json.dumps(data), ex=expire)


def delete_cache(key: str):
    redis_client.delete(key)


def delete_cache_pattern(pattern: str):
    keys = redis_client.scan_iter(match=pattern)
    
    for key in keys:
        redis_client.delete(key)


def cache(key: str, ttl: int = 30):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            
            signature = inspect.signature(function)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments
            
            try:
                final_key = key.format(**all_args)
            except KeyError as e:
                print(f"Cache key error: {e}")
                final_key = key
            
            data = get_cache(final_key)
            
            if data:
                print(f"Loading {final_key} from cache...")
                return data
            else:
                print(f"Loading {final_key} from the database...")
                result = function(*args, **kwargs)
                set_cache(final_key, jsonable_encoder(result), ttl)
                return result
            
        return wrapper
    return decorator
                









