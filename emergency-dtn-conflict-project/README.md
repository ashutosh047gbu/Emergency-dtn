# Conflict-Aware Evidence and Freshness Management for Emergency DTN Messaging

A runnable Python prototype based on the supplied architecture diagram. It models a mobile Delay-Tolerant Network (DTN) where nodes store, carry, and forward emergency message bundles during intermittent connectivity and prolonged partitions.

## Features

- **Evidence manager:** source trust, evidence strength, and metadata validation.
- **Freshness manager:** exponential temporal decay using bundle timestamp and configurable half-life.
- **Conflict detection:** identifies direct contradiction, refinement, and supersession for bundles sharing an event ID.
- **Resolution engine:** combines freshness and evidence into a utility score and chooses accept, update, reject, or retain-old.
- **Store-carry-forward cache:** bounded cache with priority-based eviction and deduplication.
- **Contact-based dissemination:** transfers eligible bundles when nodes meet; no continuous network connection is assumed.
- **Audit log:** records decisions and cache operations.
- **CLI demo and unit tests:** standard library only; no third-party packages required.

## Requirements

- Python 3.10+ (Python 3.12+ recommended)
- No external dependencies

## Run

From this directory:

```bash
python main.py demo
python main.py simulate --nodes 5 --steps 12 --seed 7
python -m unittest discover -s tests -v
```

## Project structure

```text
emergency-dtn-conflict/
├── main.py
├── dtn/
│   ├── __init__.py
│   ├── models.py
│   ├── evidence.py
│   ├── freshness.py
│   ├── conflict.py
│   ├── cache.py
│   ├── node.py
│   └── simulation.py
├── tests/
│   └── test_project.py
└── docs/
    └── design.md
```

## Message format

Each bundle has a globally unique `bundle_id`, a shared `event_id` for related reports, `timestamp`, `source_id`, `evidence_strength` in `[0, 1]`, a claim, and a conflict type. Related bundles with the same `event_id` are compared; unrelated events are not treated as conflicts.

## Decision policy

The prototype computes:

`utility = freshness_weight * freshness_score + evidence_weight * evidence_score`

Default weights are 0.40 freshness and 0.60 evidence. A candidate is accepted if it has higher utility and either resolves the conflict type or exceeds the incumbent by the configured margin. Otherwise, the incumbent is retained. The thresholds are configurable in `dtn/conflict.py`.

Conflict types:
- `DIRECT_CONTRADICTION`: claims disagree about the same fact.
- `REFINEMENT`: a report adds detail to an earlier report.
- `SUPERSESSION`: a newer authoritative report replaces an earlier one.

This is a research prototype, not a safety-certified emergency messaging system. Production deployment should add cryptographic signatures, authenticated identities, replay protection, clock-skew handling, privacy controls, persistent storage, transport integration (e.g. Bundle Protocol), and field testing. The simulation uses synthetic data and does not prove real-world emergency reliability.
