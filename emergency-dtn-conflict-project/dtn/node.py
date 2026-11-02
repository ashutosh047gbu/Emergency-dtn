import time
from .models import Bundle, ConflictType, Decision
from .evidence import EvidenceManager
from .freshness import FreshnessManager
from .conflict import ConflictDetectionEngine, ConflictResolutionEngine
from .cache import MessageCache

class DTNNode:
    def __init__(self, node_id, cache_capacity=100, source_trust=None,
                 freshness_half_life=3600, freshness_weight=0.40, evidence_weight=0.60):
        self.node_id = str(node_id)
        self.cache = MessageCache(cache_capacity)
        self.evidence = EvidenceManager(source_trust)
        self.freshness = FreshnessManager(freshness_half_life)
        self.detector = ConflictDetectionEngine()
        self.resolver = ConflictResolutionEngine(freshness_weight, evidence_weight)
        self.audit_log = []

    def _score(self, bundle, now=None):
        bundle.evidence_score = self.evidence.score(bundle)
        bundle.freshness_score = self.freshness.score(bundle, now)
        bundle.utility = self.resolver.freshness_weight * bundle.freshness_score + self.resolver.evidence_weight * bundle.evidence_score
        bundle.priority = bundle.utility

    def receive(self, bundle: Bundle, now=None):
        now = time.time() if now is None else now
        if self.cache.get(bundle.bundle_id):
            return {"decision": Decision.REJECT.value, "reason": "Duplicate bundle ID"}
        self._score(bundle, now)
        related = self.cache.find_event(bundle.event_id)
        if not related:
            result = self.cache.insert(bundle)
            self.audit_log.append({"node": self.node_id, "decision": Decision.ACCEPT.value, "bundle_id": bundle.bundle_id})
            return {"decision": Decision.ACCEPT.value, "reason": "First bundle for event", "cache": result}

        # Compare against the highest-utility incumbent for this event.
        old = max(related, key=lambda b: b.utility)
        conflict_type = self.detector.detect(old, bundle)
        if conflict_type == ConflictType.NONE:
            # Same claim/event: keep one copy to avoid cache duplication.
            self.audit_log.append({"node": self.node_id, "decision": Decision.REJECT.value, "bundle_id": bundle.bundle_id})
            return {"decision": Decision.REJECT.value, "reason": "Duplicate claim for event"}

        result = self.resolver.evaluate(old, bundle, conflict_type)
        if result.selected.bundle_id == bundle.bundle_id:
            self.cache.replace_event_bundle(old, bundle)
        self.audit_log.append({
            "node": self.node_id, "decision": result.decision.value,
            "old_bundle_id": old.bundle_id, "new_bundle_id": bundle.bundle_id,
            "conflict_type": conflict_type.value, "old_utility": round(old.utility, 4),
            "new_utility": round(bundle.utility, 4), "reason": result.reason
        })
        return {"decision": result.decision.value, "reason": result.reason,
                "conflict_type": conflict_type.value, "old_utility": round(old.utility, 4),
                "new_utility": round(bundle.utility, 4)}

    def create_bundle(self, event_id, claim, evidence_strength, timestamp=None,
                     conflict_type=ConflictType.NONE, metadata=None):
        return Bundle(event_id=event_id, claim=claim, source_id=self.node_id,
                      evidence_strength=evidence_strength,
                      timestamp=time.time() if timestamp is None else timestamp,
                      conflict_type=conflict_type, metadata=metadata or {})

    def forward_to(self, other, now=None):
        """Store-carry-forward transfer over a simulated contact."""
        transferred, decisions = 0, []
        for bundle in sorted(self.cache.all(), key=lambda b: b.priority, reverse=True):
            if not other.cache.get(bundle.bundle_id):
                decisions.append((bundle.bundle_id, other.receive(bundle, now=now)))
                transferred += 1
        return {"from": self.node_id, "to": other.node_id, "transferred": transferred, "decisions": decisions}
