"""django-smartcache package
Expose public API here.
"""
from .manager import get_or_set, invalidate, get_redis_client
from .decorators import smart_cached

__all__ = ["get_or_set", "invalidate", "get_redis_client", "smart_cached"]