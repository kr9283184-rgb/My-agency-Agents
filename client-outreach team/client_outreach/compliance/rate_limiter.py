import time
import threading
from collections import defaultdict
from datetime import datetime, timedelta

from client_outreach.config import Config


class RateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._history: dict[str, list[float]] = defaultdict(list)
        self._limits = {
            "email": Config.RATE_LIMIT_EMAIL,
            "whatsapp": Config.RATE_LIMIT_WHATSAPP,
            "linkedin": Config.RATE_LIMIT_LINKEDIN,
            "facebook": Config.RATE_LIMIT_FACEBOOK,
            "twitter": Config.RATE_LIMIT_TWITTER,
            "instagram": Config.RATE_LIMIT_FACEBOOK,
        }

    def can_send(self, channel: str) -> bool:
        limit = self._limits.get(channel, 10)
        cutoff = time.time() - 3600
        with self._lock:
            self._history[channel] = [
                t for t in self._history[channel] if t > cutoff
            ]
            return len(self._history[channel]) < limit

    def record_send(self, channel: str):
        with self._lock:
            self._history[channel].append(time.time())

    def wait_if_needed(self, channel: str):
        if not self.can_send(channel):
            limit = self._limits.get(channel, 10)
            cutoff = time.time() - 3600
            with self._lock:
                self._history[channel] = [
                    t for t in self._history[channel] if t > cutoff
                ]
            while not self.can_send(channel):
                time.sleep(30)

    def remaining(self, channel: str) -> int:
        limit = self._limits.get(channel, 10)
        cutoff = time.time() - 3600
        with self._lock:
            self._history[channel] = [
                t for t in self._history[channel] if t > cutoff
            ]
            return max(0, limit - len(self._history[channel]))
