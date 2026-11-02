from dataclasses import dataclass
from .models import Bundle, ConflictType, Decision

@dataclass
class Resolution:
    decision: Decision
    selected: Bundle
    candidate: Bundle
    reason: str

class ConflictDetectionEngine:
    def detect(self, old: Bundle, new: Bundle) -> ConflictType:
        if old.event_id != new.event_id:
            return ConflictType.NONE
        if old.claim.strip().casefold() == new.claim.strip().casefold():
            return ConflictType.NONE
        if new.conflict_type != ConflictType.NONE:
            return new.conflict_type
        # Conservative heuristic: metadata can explicitly identify relation.
        relation = new.metadata.get("relation")
        if relation == "refinement":
            return ConflictType.REFINEMENT
        if relation == "supersedes":
            return ConflictType.SUPERSESSION
        return ConflictType.DIRECT_CONTRADICTION

class ConflictResolutionEngine:
    def __init__(self, freshness_weight=0.40, evidence_weight=0.60, update_margin=0.03):
        if abs(freshness_weight + evidence_weight - 1.0) > 1e-9:
            raise ValueError("freshness_weight + evidence_weight must equal 1")
        self.freshness_weight = freshness_weight
        self.evidence_weight = evidence_weight
        self.update_margin = update_margin

    def evaluate(self, old: Bundle, new: Bundle, conflict_type: ConflictType) -> Resolution:
        old.utility = self.freshness_weight * old.freshness_score + self.evidence_weight * old.evidence_score
        new.utility = self.freshness_weight * new.freshness_score + self.evidence_weight * new.evidence_score
        old.priority = old.utility
        new.priority = new.utility

        # A valid explicit supersession can replace the old bundle when utility is not materially worse.
        if conflict_type == ConflictType.SUPERSESSION and new.utility >= old.utility - self.update_margin:
            return Resolution(Decision.UPDATE, new, new, "Explicit supersession accepted within utility margin")
        if conflict_type == ConflictType.REFINEMENT and new.utility >= old.utility - self.update_margin:
            return Resolution(Decision.UPDATE, new, new, "Refinement accepted within utility margin")
        if new.utility > old.utility + self.update_margin:
            return Resolution(Decision.ACCEPT, new, new, "Candidate has higher combined evidence/freshness utility")
        if new.bundle_id == old.bundle_id:
            return Resolution(Decision.REJECT, old, new, "Duplicate bundle")
        return Resolution(Decision.RETAIN_OLD, old, new, "Existing bundle has equal or better utility")
