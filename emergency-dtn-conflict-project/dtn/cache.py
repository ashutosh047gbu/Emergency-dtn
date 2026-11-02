from collections import OrderedDict
from .models import Bundle

class MessageCache:
    """Bounded cache keyed by bundle_id, evicting lowest priority/oldest first."""
    def __init__(self, capacity=100):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = int(capacity)
        self._bundles = OrderedDict()
        self.audit_log = []

    def __len__(self):
        return len(self._bundles)

    def all(self):
        return list(self._bundles.values())

    def get(self, bundle_id):
        return self._bundles.get(bundle_id)

    def find_event(self, event_id):
        return [b for b in self._bundles.values() if b.event_id == event_id]

    def insert(self, bundle: Bundle):
        if bundle.bundle_id in self._bundles:
            self.audit_log.append({"action": "DUPLICATE", "bundle_id": bundle.bundle_id})
            return False
        evicted = None
        if len(self._bundles) >= self.capacity:
            evicted = min(self._bundles.values(), key=lambda b: (b.priority, b.timestamp))
            del self._bundles[evicted.bundle_id]
            self.audit_log.append({"action": "EVICT", "bundle_id": evicted.bundle_id})
        self._bundles[bundle.bundle_id] = bundle
        self.audit_log.append({"action": "INSERT", "bundle_id": bundle.bundle_id})
        return {"inserted": True, "evicted": evicted.bundle_id if evicted else None}

    def replace_event_bundle(self, old: Bundle, new: Bundle):
        self._bundles.pop(old.bundle_id, None)
        result = self.insert(new)
        self.audit_log.append({"action": "REPLACE_EVENT", "old": old.bundle_id, "new": new.bundle_id})
        return result

    def remove(self, bundle_id):
        if bundle_id in self._bundles:
            del self._bundles[bundle_id]
            self.audit_log.append({"action": "REMOVE", "bundle_id": bundle_id})
            return True
        return False
