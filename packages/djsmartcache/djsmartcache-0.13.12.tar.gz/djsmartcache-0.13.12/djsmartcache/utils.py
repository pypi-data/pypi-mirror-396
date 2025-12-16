import json
import hashlib
import random
import time
from typing import Any
import redis

from .conf import REDIS_URL, JITTER_PCT

_redis_client = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

def make_key(base: str, *args, **kwargs) -> str:
    """Create a stable cache key by hashing args and kwargs to avoid poisoning."""
    payload = {
        "args": args,
        "kwargs": kwargs,
    }
    h = hashlib.sha1(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    return f"{base}:{h}"

def add_jitter(ttl: int) -> int:
    if not ttl or JITTER_PCT <= 0:
        return ttl
    jitter = int(ttl * JITTER_PCT)
    if jitter <= 0:
        return ttl
    return ttl + random.randint(-jitter, jitter)

def current_milli() -> int:
    return int(time.time() * 1000)
