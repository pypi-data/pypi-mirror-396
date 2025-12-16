import threading
import json
from .utils import get_redis_client
from .conf import PUBSUB_CHANNEL

class PubSubListener(threading.Thread):
    daemon = True

    def __init__(self):
        super().__init__(daemon=True)
        self.redis = get_redis_client()
        self._stopped = threading.Event()

    def run(self):
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(PUBSUB_CHANNEL)
        for msg in pubsub.listen():
            if self._stopped.is_set():
                break
            try:
                data = msg.get('data')
                if not data:
                    continue
                payload = json.loads(data)
                model = payload.get('model')
                pk = payload.get('pk')
                version = payload.get('version')
                if model and pk and version:
                    # set local version value so readers will build keys with it
                    self.redis.set(f"{model}:{pk}:version", int(version))
            except Exception:
                continue

    def stop(self):
        self._stopped.set()

_listener = None
def start_listener():
    global _listener
    if _listener is None:
        _listener = PubSubListener()
        _listener.start()

def stop_listener():
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
