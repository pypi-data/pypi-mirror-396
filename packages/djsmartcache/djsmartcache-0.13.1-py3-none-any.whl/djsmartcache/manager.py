import json
from django.core import serializers
from django.apps import apps
from django.conf import settings
from .utils import get_redis_client, make_key, add_jitter
from .conf import DEFAULT_TTL, USE_REDIS_LOCK, LOCK_TIMEOUT, PUBSUB_CHANNEL

r = None

def get_redis_client_cached():
    global r
    if r is None:
        r = get_redis_client()
    return r

def _model_label(model):
    return f"{model._meta.app_label}.{model.__name__}"

def fetch_version(model_label: str, pk: str) -> int:
    rc = get_redis_client_cached()
    val = rc.get(f"{model_label}:{pk}:version")
    try:
        return int(val)
    except (TypeError, ValueError):
        return 1

def build_cache_key_for_model(model, pk):
    model_label = _model_label(model)
    ver = fetch_version(model_label, pk)
    return f"{model_label}:{pk}:v{ver}"

def get_or_set(model, pk, ttl=None, loader=None):
    """
    Read-through cache for a given model and pk. If loader provided, it will be
    used to fetch the object instead of hitting the ORM.
    Returns model instance or None.
    """
    rc = get_redis_client_cached()
    key = build_cache_key_for_model(model, pk)

    raw = rc.get(key)
    if raw:
        # cached JSON serialization
        try:
            objs = list(serializers.deserialize('json', raw))
            return next(objs).object
        except Exception:
            # corrupted cache — invalidate and continue
            try:
                rc.delete(key)
            except Exception:
                pass

    lock_key = f"lock:{key}"
    lock = None
    got_lock = False
    try:
        if USE_REDIS_LOCK:
            lock = rc.lock(lock_key, timeout=LOCK_TIMEOUT)
            got_lock = lock.acquire(blocking=True)
        if got_lock:
            # double-check
            raw = rc.get(key)
            if raw:
                try:
                    objs = list(serializers.deserialize('json', raw))
                    return next(objs).object
                except Exception:
                    rc.delete(key)

            # fetch from loader or ORM
            try:
                if loader:
                    obj = loader()
                else:
                    obj = model.objects.get(pk=pk)
            except model.DoesNotExist:
                # cache negative result for a short time
                rc.set(key, json.dumps(None), ex=60)
                return None

            ser = serializers.serialize('json', [obj])
            rc.set(key, ser, ex=add_jitter(ttl or DEFAULT_TTL))
            return obj
        else:
            # failed to obtain lock — brief waiting read
            for _ in range(5):
                raw = rc.get(key)
                if raw:
                    try:
                        objs = list(serializers.deserialize('json', raw))
                        return next(objs).object
                    except Exception:
                        break
            # last resort: read DB
            if loader:
                return loader()
            return model.objects.get(pk=pk)
    finally:
        if lock and got_lock:
            try:
                lock.release()
            except Exception:
                pass

def invalidate(model, pk):
    """Bump version and publish invalidation to pubsub channel."""
    rc = get_redis_client_cached()
    model_label = _model_label(model)
    new_ver = rc.incr(f"{model_label}:{pk}:version")
    payload = json.dumps({"model": model_label, "pk": str(pk), "version": new_ver})
    try:
        rc.publish(PUBSUB_CHANNEL, payload)
    except Exception:
        pass

# Utility export for package users
def get_redis_client():
    return get_redis_client_cached()
