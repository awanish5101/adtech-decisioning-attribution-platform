"""
In-memory Redis-style sliding window frequency capper.
"""
import time
import threading
from typing import Dict, List


class FrequencyCapper:
    def __init__(self, window_seconds: int = 3600):
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        # key: f"{user_id}:{campaign_id}" -> list of timestamps
        self._impressions: Dict[str, List[float]] = {}

    def is_capped(self, user_id: str, campaign_id: str, max_impressions: int) -> bool:
        with self._lock:
            key = f"{user_id}:{campaign_id}"
            now = time.time()
            cutoff = now - self.window_seconds

            timestamps = self._impressions.get(key, [])
            # Filter out timestamps older than sliding window
            valid_timestamps = [t for t in timestamps if t > cutoff]
            self._impressions[key] = valid_timestamps

            return len(valid_timestamps) >= max_impressions

    def record_impression(self, user_id: str, campaign_id: str):
        with self._lock:
            key = f"{user_id}:{campaign_id}"
            now = time.time()
            if key not in self._impressions:
                self._impressions[key] = []
            self._impressions[key].append(now)

    def reset(self):
        with self._lock:
            self._impressions.clear()


frequency_capper = FrequencyCapper()
