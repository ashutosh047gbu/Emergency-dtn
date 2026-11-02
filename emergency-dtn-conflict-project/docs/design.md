# System Design

## Mapping to the supplied diagram

| Diagram block | Implementation |
|---|---|
| Evidence Manager | `dtn/evidence.py` |
| Freshness Manager | `dtn/freshness.py` |
| Conflict Detection Engine | `dtn/conflict.py:ConflictDetectionEngine` |
| Utility / Resolution | `dtn/conflict.py:ConflictResolutionEngine` |
| Message Cache & Buffer Storage | `dtn/cache.py` |
| Store-Carry-Forward node | `dtn/node.py:DTNNode` |
| Routing/dissemination | `DTNNode.forward_to` and `dtn/simulation.py` |
| Audit / decision history | node and cache `audit_log` lists |

## Processing pipeline

1. A node receives a bundle and validates basic required fields.
2. Evidence is scored from source trust, reported evidence strength, and metadata flags.
3. Freshness is computed with exponential decay: `F(t) = exp(-ln(2) * age / half_life)`.
4. If the event has no cached report, the bundle is inserted.
5. If a report for the same event exists, the detector labels the relation as contradiction, refinement, or supersession.
6. The resolver computes `U = w_f * F + w_e * E`.
7. A sufficiently useful candidate replaces the incumbent; otherwise the old bundle remains.
8. The cache evicts the lowest-priority entry when full and logs each operation.
9. During a contact opportunity, a node forwards cached bundles in descending priority order.

## Important limitations

The conflict detector cannot infer truth from text. It uses explicit relation metadata and a conservative default for differing claims. A real deployment needs a domain-specific contradiction model, authenticated evidence, signed bundles, robust clock synchronization, persistence, and a tested transport protocol. Utility weights and half-life should be calibrated with scenario-based experiments.
