
import redis
import json
from typing import Any, Optional

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache."""
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, expiry: int = 300):
        """Store data in cache with expiry in seconds."""
        self.redis_client.setex(key, expiry, json.dumps(value))

    def delete(self, key: str):
        """Delete data from cache."""
        self.redis_client.delete(key)

    def clear(self):
        """Clear all cache data."""
        self.redis_client.flushdb()

    def get_or_set(self, key: str, func, expiry: int = 300) -> Any:
        """Get data from cache or set it if not present."""
        data = self.get(key)
        if data is None:
            data = func()
            self.set(key, data, expiry)
        return data
