"""
Atomic event deduplicator preventing duplicate attribution and billing.
"""
import hashlib
import time
import threading
from typing import Dict, Set


class EventDeduplicator:
    def __init__(self, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        # key: event_hash -> expiration_timestamp
        self._seen_events: Dict[str, float] = {}

    def compute_hash(self, event_id: str, event_type: str, user_id: str, campaign_id: str) -> str:
        payload = f"{event_id}:{event_type}:{user_id}:{campaign_id}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def check_and_set(self, event_hash: str) -> bool:
        """
        Returns True if the event is a DUPLICATE, False if it is NEW.
        """
        with self._lock:
            now = time.time()
            # Clean expired opportunistically
            expired = [k for k, exp in self._seen_events.items() if exp < now]
            for k in expired:
                del self._seen_events[k]

            if event_hash in self._seen_events:
                return True

            self._seen_events[event_hash] = now + self.ttl_seconds
            return False

    def reset(self):
        with self._lock:
            self._seen_events.clear()


deduplicator = EventDeduplicator()
