#!/usr/bin/env python3
"""
PokerMath CLI Monte Carlo Range vs Range Simulator.
"""
import argparse
from poker_monte_carlo_engine import run_monte_carlo_simulation

def main():
    parser = argparse.ArgumentParser(description="Deterministic Monte Carlo Equity Engine for Texas Hold'em")
    parser.add_argument("--hero", type=str, default="As Ah", help="Hero hole cards (e.g. 'As Ah' or 'AsAh')")
    parser.add_argument("--villain", type=str, default="Ks Kh", help="Villain hole cards (e.g. 'Ks Kh' or 'KsKh')")
    parser.add_argument("--board", type=str, default="", help="Known community cards (e.g. 'Qd Jc Ts')")
    parser.add_argument("--trials", type=int, default=100000, help="Number of Monte Carlo iterations (default: 100,000)")
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed for 100% reproducible results")
    args = parser.parse_args()

    results = run_monte_carlo_simulation(args.hero, args.villain, args.board, trials=args.trials, seed=args.seed)

    print("\n" + "=" * 55)
    print("POKERMATH MONTE CARLO RANGE EVALUATION RESULT")
    print("=" * 55)
    print(f"Hero Hand:    {results['hero_hand']}")
    print(f"Villain Hand: {results['villain_hand']}")
    print(f"Board:        {results['board']}")
    print(f"Trials:       {results['trials']:,}")
    if results['seed'] is not None:
        print(f"RNG Seed:     {results['seed']} (Deterministic)")
    print(f"Execution:    {results['elapsed_seconds']}s ({results['iterations_per_sec']:,} boards/sec)")
    print("-" * 55)
    print(f"Hero Equity:    {results['hero_equity_pct']}% ({results['hero_wins']:,} wins)")
    print(f"Villain Equity: {results['villain_equity_pct']}% ({results['villain_wins']:,} wins)")
    print(f"Tie Rate:       {results['tie_rate']*100:.2f}% ({results['ties']:,} ties)")
    print("=" * 55)

if __name__ == '__main__':
    main()
