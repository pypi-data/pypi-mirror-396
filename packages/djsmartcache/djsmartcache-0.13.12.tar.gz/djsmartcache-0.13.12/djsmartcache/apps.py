from django.apps import AppConfig
from django.conf import settings

class SmartcacheConfig(AppConfig):
    name = 'djsmartcache'
    verbose_name = 'SmartCache'

    def ready(self):
        # register signals
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass

        # start pubsub listener in-process if enabled
        if getattr(settings, 'SMARTCACHE_START_LISTENER', True):
            try:
                from .listener import start_listener
                start_listener()
            except Exception:
                pass
