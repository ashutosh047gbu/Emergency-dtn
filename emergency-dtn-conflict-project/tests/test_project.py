import unittest
from dtn.models import Bundle, ConflictType, Decision
from dtn.node import DTNNode
from dtn.freshness import FreshnessManager
from dtn.evidence import EvidenceManager
from dtn.cache import MessageCache

class ProjectTests(unittest.TestCase):
    def test_freshness_decays(self):
        fm = FreshnessManager(half_life_seconds=100)
        b = Bundle("e", "claim", "s", 0.8, timestamp=900)
        self.assertGreater(fm.score(b, now=900), fm.score(b, now=1000))
        self.assertAlmostEqual(fm.score(b, now=1000), 0.5, places=5)

    def test_future_timestamp_rejected_as_stale(self):
        fm = FreshnessManager(half_life_seconds=100, max_future_skew_seconds=10)
        b = Bundle("e", "claim", "s", 0.8, timestamp=200)
        self.assertEqual(fm.score(b, now=100), 0.0)

    def test_evidence_score_bounds(self):
        em = EvidenceManager({"trusted": 1.0})
        b = Bundle("e", "claim", "trusted", 1.0)
        self.assertEqual(em.score(b), 1.0)

    def test_invalid_signature_zeroes_evidence(self):
        em = EvidenceManager({"trusted": 1.0})
        b = Bundle("e", "claim", "trusted", 1.0, metadata={"signature_valid": False})
        self.assertEqual(em.score(b), 0.0)

    def test_conflict_update_prefers_fresher_stronger_report(self):
        node = DTNNode("n1", source_trust={"weak": 0.2, "strong": 1.0}, freshness_half_life=1000)
        old = Bundle("incident", "road closed", "weak", 0.3, timestamp=900)
        new = Bundle("incident", "road open", "strong", 1.0, timestamp=1000,
                     conflict_type=ConflictType.DIRECT_CONTRADICTION)
        node.receive(old, now=1000)
        result = node.receive(new, now=1000)
        self.assertIn(result["decision"], (Decision.ACCEPT.value, Decision.UPDATE.value))
        self.assertEqual(node.cache.find_event("incident")[0].bundle_id, new.bundle_id)

    def test_cache_capacity(self):
        cache = MessageCache(capacity=1)
        a = Bundle("a", "A", "s", 0.8, priority=0.2)
        b = Bundle("b", "B", "s", 0.8, priority=0.8)
        cache.insert(a)
        cache.insert(b)
        self.assertEqual(len(cache), 1)
        self.assertIsNotNone(cache.get(b.bundle_id))

    def test_duplicate_claim_is_not_duplicated(self):
        node = DTNNode("n")
        a = Bundle("e", "same claim", "s1", 0.8, timestamp=100)
        b = Bundle("e", "same claim", "s2", 0.9, timestamp=101)
        node.receive(a, now=101)
        result = node.receive(b, now=101)
        self.assertEqual(result["decision"], Decision.REJECT.value)
        self.assertEqual(len(node.cache.find_event("e")), 1)

    def test_store_carry_forward(self):
        a, b = DTNNode("a"), DTNNode("b")
        bundle = Bundle("e", "evacuate north", "a", 0.9, timestamp=100)
        a.receive(bundle, now=100)
        result = a.forward_to(b, now=100)
        self.assertEqual(result["transferred"], 1)
        self.assertEqual(len(b.cache), 1)

if __name__ == "__main__":
    unittest.main()
