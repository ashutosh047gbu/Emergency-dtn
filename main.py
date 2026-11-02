import argparse
from dtn.simulation import run_demo, run_simulation

def main():
    parser = argparse.ArgumentParser(description="Emergency DTN conflict/freshness prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run a deterministic conflict-resolution demonstration")
    sim = sub.add_parser("simulate", help="Run a small store-carry-forward simulation")
    sim.add_argument("--nodes", type=int, default=5)
    sim.add_argument("--steps", type=int, default=12)
    sim.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    if args.command == "demo":
        run_demo()
    else:
        run_simulation(nodes=args.nodes, steps=args.steps, seed=args.seed)

if __name__ == "__main__":
    main()
