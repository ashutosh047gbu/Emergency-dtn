from .models import Bundle

class EvidenceManager:
    """Scores evidence using source trust, reported strength, and metadata checks."""
    def __init__(self, source_trust=None):
        self.source_trust = dict(source_trust or {})
        self.default_trust = 0.5

    def score(self, bundle: Bundle) -> float:
        trust = self.source_trust.get(bundle.source_id, self.default_trust)
        trust = min(1.0, max(0.0, float(trust)))
        strength = min(1.0, max(0.0, bundle.evidence_strength))
        metadata_factor = 1.0
        if bundle.metadata.get("signature_valid") is False:
            metadata_factor = 0.0
        elif bundle.metadata.get("metadata_complete") is False:
            metadata_factor = 0.75
        # Weighted score remains within [0, 1].
        return round((0.65 * strength + 0.35 * trust) * metadata_factor, 6)
