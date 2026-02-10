"""Redis client for storing and retrieving simulation data."""

import json
import redis
from django.conf import settings
from typing import Optional, Dict, Any


class RedisClient:
    """Client for managing simulation data in Redis."""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = 86400  # Time-to-live in seconds (24 hours for demo without Celery)

    def store_device_data(self, device_id: int, data: Dict[str, Any]):
        """Store current device simulation data."""
        key = f"device:{device_id}:current"
        self.redis.setex(key, self.ttl, json.dumps(data))

    def get_device_data(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve current device simulation data."""
        key = f"device:{device_id}:current"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_device_storage(self, device_id: int, storage_data: Dict[str, Any]):
        """Store storage device data (batteries, EVs)."""
        key = f"device:{device_id}:storage"
        self.redis.setex(key, self.ttl, json.dumps(storage_data))

    def get_device_storage(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve storage device data."""
        key = f"device:{device_id}:storage"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_ev_last_seen(self, device_id: int, last_seen_data: Dict[str, Any]):
        """Store EV last seen data for offline tracking."""
        key = f"device:{device_id}:last_seen"
        # Longer TTL for last_seen data (1 day)
        self.redis.setex(key, 86400, json.dumps(last_seen_data))

    def get_ev_last_seen(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve EV last seen data."""
        key = f"device:{device_id}:last_seen"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def store_user_stats(self, user_id: int, stats: Dict[str, Any]):
        """Store aggregated user energy statistics."""
        key = f"user:{user_id}:energy_stats"
        self.redis.setex(key, self.ttl, json.dumps(stats))

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve aggregated user energy statistics."""
        key = f"user:{user_id}:energy_stats"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def get_all_device_keys(self, pattern: str = "device:*:current") -> list:
        """Get all device keys matching pattern."""
        return self.redis.keys(pattern)

    def delete_key(self, key: str):
        """Delete a specific key."""
        self.redis.delete(key)
