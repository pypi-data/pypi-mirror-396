from functools import wraps
from .manager import get_or_set

def smart_cached(model=None, pk_arg='pk', ttl=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if model is None:
                return func(*args, **kwargs)
            pk = kwargs.get(pk_arg)
            if pk is None:
                # attempt to find pk from positional args if user passed index
                try:
                    if isinstance(pk_arg, int):
                        pk = args[pk_arg]
                except Exception:
                    pass
            if pk is None:
                return func(*args, **kwargs)
            obj = get_or_set(model, pk, ttl=ttl)
            if obj is None:
                return func(*args, **kwargs)
            return obj
        return wrapper
    return decorator
