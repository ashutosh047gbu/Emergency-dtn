from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import uuid

class ConflictType(str, Enum):
    NONE = "NONE"
    DIRECT_CONTRADICTION = "DIRECT_CONTRADICTION"
    REFINEMENT = "REFINEMENT"
    SUPERSESSION = "SUPERSESSION"

class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    UPDATE = "UPDATE"
    REJECT = "REJECT"
    RETAIN_OLD = "RETAIN_OLD"

@dataclass
class Bundle:
    event_id: str
    claim: str
    source_id: str
    evidence_strength: float
    timestamp: float = field(default_factory=time.time)
    conflict_type: ConflictType = ConflictType.NONE
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence_score: float = 0.0
    freshness_score: float = 0.0
    utility: float = 0.0
    priority: float = 0.0

    def __post_init__(self):
        self.evidence_strength = min(1.0, max(0.0, float(self.evidence_strength)))
        if not self.event_id.strip():
            raise ValueError("event_id must not be empty")
        if not self.claim.strip():
            raise ValueError("claim must not be empty")
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")

    def to_dict(self):
        return {
            "bundle_id": self.bundle_id, "event_id": self.event_id,
            "claim": self.claim, "source_id": self.source_id,
            "evidence_strength": self.evidence_strength, "timestamp": self.timestamp,
            "conflict_type": self.conflict_type.value,
            "evidence_score": self.evidence_score, "freshness_score": self.freshness_score,
            "utility": self.utility, "priority": self.priority, "metadata": self.metadata,
        }
