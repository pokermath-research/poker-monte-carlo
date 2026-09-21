#!/usr/bin/env python3
"""
PokerMath CLI Monte Carlo Range vs Range Simulator.
"""
import argparse
from poker_monte_carlo_engine import run_monte_carlo_simulation

def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Equity Engine for Texas Hold'em")
    parser.add_argument("--hero", type=str, default="As Ah", help="Hero hole cards (e.g. 'As Ah')")
    parser.add_argument("--villain", type=str, default="Ks Kh", help="Villain hole cards (e.g. 'Ks Kh')")
    parser.add_argument("--board", type=str, default="", help="Known community cards (e.g. 'Qd Jc Ts')")
    parser.add_argument("--trials", type=int, default=100000, help="Number of Monte Carlo iterations")
    args = parser.parse_args()

    print(f"Running simulation: Hero [{args.hero}] vs Villain [{args.villain}] | Board [{args.board}] | Trials: {args.trials:,}")
    results = run_monte_carlo_simulation(args.hero, args.villain, args.board, trials=args.trials)
    print("
=== Simulation Results ===")
    for k, v in results.items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
