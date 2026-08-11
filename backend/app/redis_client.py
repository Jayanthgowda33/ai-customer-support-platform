import json
from typing import Optional

import redis

from app.config import settings

_redis = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> redis.Redis:
    return _redis


def cache_conversation_history(conversation_id: str, history: list, ttl_seconds: int = 3600) -> None:
    _redis.set(f"conv:{conversation_id}:history", json.dumps(history), ex=ttl_seconds)


def get_cached_history(conversation_id: str) -> Optional[list]:
    raw = _redis.get(f"conv:{conversation_id}:history")
    return json.loads(raw) if raw else None


def rate_limit_ok(key: str, limit: int = 30, window_seconds: int = 60) -> bool:
    """Simple fixed-window rate limiter, e.g. per-customer chat spam protection."""
    current = _redis.incr(key)
    if current == 1:
        _redis.expire(key, window_seconds)
    return current <= limit
