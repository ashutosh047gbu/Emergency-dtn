import math
import time
from .models import Bundle

class FreshnessManager:
    """Exponential decay; half_life_seconds is the time to reach freshness 0.5."""
    def __init__(self, half_life_seconds=3600.0, max_future_skew_seconds=120.0):
        if half_life_seconds <= 0:
            raise ValueError("half_life_seconds must be positive")
        self.half_life_seconds = float(half_life_seconds)
        self.max_future_skew_seconds = float(max_future_skew_seconds)

    def score(self, bundle: Bundle, now=None) -> float:
        now = time.time() if now is None else float(now)
        # A timestamp too far in the future is treated as invalid/stale.
        if bundle.timestamp > now + self.max_future_skew_seconds:
            return 0.0
        age = max(0.0, now - bundle.timestamp)
        value = math.exp(-math.log(2) * age / self.half_life_seconds)
        return round(min(1.0, max(0.0, value)), 6)
