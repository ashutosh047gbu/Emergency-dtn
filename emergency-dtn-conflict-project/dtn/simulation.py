import random
from .node import DTNNode
from .models import ConflictType

def run_demo():
    now = 1_800_000_000.0
    trust = {"responder_A": 0.95, "witness_B": 0.55, "sensor_C": 0.80}
    node = DTNNode("responder_A", source_trust=trust, freshness_half_life=1800)
    old = node.create_bundle("bridge_17", "Bridge is blocked", 0.70,
                             timestamp=now - 2400, metadata={"metadata_complete": True})
    new = node.create_bundle("bridge_17", "Bridge is open", 0.98,
                             timestamp=now - 60, conflict_type=ConflictType.DIRECT_CONTRADICTION,
                             metadata={"metadata_complete": True})
    # Simulate reports from distinct sources by adjusting source IDs.
    old.source_id = "witness_B"
    new.source_id = "responder_A"
    print("=== Emergency DTN conflict-resolution demo ===")
    print("Receive old report:", node.receive(old, now=now))
    print("Receive conflicting report:", node.receive(new, now=now))
    print("\nSelected cache contents:")
    for b in node.cache.all():
        print(f"- event={b.event_id} claim={b.claim!r} evidence={b.evidence_score:.3f} "
              f"freshness={b.freshness_score:.3f} utility={b.utility:.3f}")
    print("\nAudit log:")
    for item in node.audit_log:
        print(item)

def run_simulation(nodes=5, steps=12, seed=7):
    if nodes < 2 or steps < 1:
        raise ValueError("Use at least 2 nodes and 1 step")
    rng = random.Random(seed)
    trust = {f"node_{i}": rng.uniform(0.45, 0.98) for i in range(nodes)}
    network = [DTNNode(f"node_{i}", cache_capacity=30, source_trust=trust,
                       freshness_half_life=3600) for i in range(nodes)]
    base_time = 1_800_000_000.0
    # Seed the network with several emergency reports.
    for event in range(3):
        origin = network[event % nodes]
        bundle = origin.create_bundle(f"incident_{event}", f"Incident {event}: severity moderate",
                                      rng.uniform(0.55, 0.95), timestamp=base_time)
        network[(event + 1) % nodes].receive(bundle, now=base_time)
    decisions = {}
    for step in range(steps):
        now = base_time + step * 300
        a, b = rng.sample(network, 2)
        # Occasionally generate a conflicting update.
        if rng.random() < 0.35:
            event = rng.randrange(3)
            claim = rng.choice([f"Incident {event}: severity high",
                                f"Incident {event}: severity low",
                                f"Incident {event}: severity moderate"])
            sender = a
            bundle = sender.create_bundle(f"incident_{event}", claim, rng.uniform(0.4, 1.0),
                                          timestamp=now,
                                          conflict_type=ConflictType.DIRECT_CONTRADICTION)
            a.receive(bundle, now=now)
        result = a.forward_to(b, now=now)
        for _, outcome in result["decisions"]:
            decision = outcome.get("decision", "UNKNOWN")
            decisions[decision] = decisions.get(decision, 0) + 1
    print(f"Simulation complete: nodes={nodes}, steps={steps}, seed={seed}")
    print("Bundle counts by node:", {n.node_id: len(n.cache) for n in network})
    print("Transfer outcomes:", decisions)
    print("Total audit entries:", sum(len(n.audit_log) + len(n.cache.audit_log) for n in network))
