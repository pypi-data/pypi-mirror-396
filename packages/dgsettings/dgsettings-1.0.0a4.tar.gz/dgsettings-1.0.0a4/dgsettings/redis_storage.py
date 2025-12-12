import json
from .storage import ConfigStorageBase


class RedisConfigStorage(ConfigStorageBase):
    def __init__(self, redis_client, redis_key: str, auto_reload: bool = False, ts_key: str = None):
        super().__init__(auto_reload=auto_reload)
        self.redis = redis_client
        self.key = redis_key
        self.ts_key = ts_key
        self._last_ts = None

    def load(self) -> dict:
        val = self.redis.get(self.key)
        ts = self.redis.get(self.ts_key) if self.ts_key else None
        if ts is not None:
            self._last_ts = ts
        if not val:
            return {}
        if isinstance(val, bytes):
            val = val.decode('utf-8')
        return json.loads(val)

    def save(self, data: dict):
        self.redis.set(self.key, json.dumps(data))
        if self.ts_key:
            import time
            self.redis.set(self.ts_key, str(int(time.time())))
            self._last_ts = self.redis.get(self.ts_key)

    def has_changed(self) -> bool:
        if not self.auto_reload or not self.ts_key:
            return False
        ts = self.redis.get(self.ts_key)
        changed = ts != self._last_ts
        if changed:
            self._last_ts = ts
        return changed
