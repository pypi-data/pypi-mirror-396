"""
File-based TTL cache for astronomical data with JSON serialization.

This cache is intentionally minimal: it stores one JSON file per key
and enforces a TTL on read. It is suitable for development and
lightweight deployments; replaceable with sqlite/redis when needed.
Works with any astronomical dataset, not just Horizons.
"""
import os
import json
import time
import hashlib
from typing import Optional, Any, Dict


def _safe_key_to_filename(cache_dir: str, key: str) -> str:
    # use a hash to avoid filesystem-unfriendly characters
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(cache_dir, f"{h}.json")


class FileCache:
    def __init__(self, cache_dir: str = None, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), ".nexuscache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.ttl_seconds = int(ttl_seconds)

    def set(self, key: str, value: Any) -> None:
        path = _safe_key_to_filename(self.cache_dir, key)
        payload = {"ts": time.time(), "value": value}
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
        except Exception:
            # fail silently for now; cache is advisory
            pass

    def get(self, key: str) -> Optional[Any]:
        path = _safe_key_to_filename(self.cache_dir, key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            ts = float(payload.get("ts", 0))
            if (time.time() - ts) > self.ttl_seconds:
                try:
                    os.remove(path)
                except Exception:
                    pass
                return None
            return payload.get("value")
        except Exception:
            return None

    def invalidate(self, key: str) -> None:
        path = _safe_key_to_filename(self.cache_dir, key)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    def get_cache_info(self) -> Dict[str, Any]:
        entries = 0
        for fn in os.listdir(self.cache_dir):
            if fn.endswith('.json'):
                entries += 1
        return {"entry_count": entries, "ttl_seconds": self.ttl_seconds}
