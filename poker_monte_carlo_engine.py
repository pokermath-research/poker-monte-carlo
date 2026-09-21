"""
================================================================================
APPLIED PROBABILITY INSTITUTE // POKER MATHEMATICS RESEARCH DIVISION
Texas Hold'em 1,326 Preflop Equity Matrix & Monte Carlo Simulation Engine
================================================================================
Open-Source License: MIT
Dataset: poker-preflop-equity-matrix-1326.csv
Website: https://pokermath.org
================================================================================
"""

import os
import sys
import csv
import random
import itertools
from collections import defaultdict, Counter
import argparse
import time

RANKS = "23456789TJQKA"
SUITS = ["s", "h", "d", "c"]
RANK_ORDER = {r: i for i, r in enumerate(RANKS)}

def parse_card(card_str):
    """Normalize and validate a 2-character card representation (e.g. 'As', 'td' -> 'As', 'Td')."""
    if not isinstance(card_str, str) or len(card_str) != 2:
        raise ValueError(f"Invalid card format: '{card_str}'. Expected 2 characters like 'As', 'Kd'.")
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    if rank not in RANK_ORDER:
        raise ValueError(f"Invalid card rank: '{rank}' in '{card_str}'. Valid ranks: {RANKS}")
    if suit not in SUITS:
        raise ValueError(f"Invalid card suit: '{suit}' in '{card_str}'. Valid suits: s, h, d, c")
    return rank + suit

def parse_cards(cards_input):
    """
    Parses a string or list of cards into a list of normalized 2-character cards.
    Examples:
      'As Ah' -> ['As', 'Ah']
      'AsAh' -> ['As', 'Ah']
      ['As', 'Ah'] -> ['As', 'Ah']
      '' -> []
    """
    if not cards_input:
        return []
    if isinstance(cards_input, list):
        return [parse_card(c) for c in cards_input]
    if isinstance(cards_input, str):
        cleaned = cards_input.strip()
        if not cleaned:
            return []
        # If separated by spaces or commas
        if " " in cleaned or "," in cleaned:
            tokens = [t.strip() for t in cleaned.replace(",", " ").split() if t.strip()]
            return [parse_card(t) for t in tokens]
        # Continuous string like 'AsAh' or 'QdJcTs'
        if len(cleaned) % 2 == 0:
            return [parse_card(cleaned[i:i+2]) for i in range(0, len(cleaned), 2)]
        raise ValueError(f"Cannot parse card sequence: '{cards_input}'")
    raise TypeError(f"Expected list or str for cards, got {type(cards_input)}")

def load_matrix(csv_path="poker-preflop-equity-matrix-1326.csv"):
    """Load the 1,326 starting hand combinations CSV matrix."""
    if not os.path.exists(csv_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, csv_path)
        if os.path.exists(alt_path):
            csv_path = alt_path
        else:
            return None

    rows = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def evaluate_5card(cards):
    """
    Evaluates a 5-card poker hand.
    Returns a comparable tuple (hand_rank, tie_breakers...) where hand_rank is 0..8:
      8: Straight Flush
      7: Four of a Kind
      6: Full House
      5: Flush
      4: Straight
      3: Three of a Kind
      2: Two Pair
      1: One Pair
      0: High Card
    """
    if len(cards) != 5:
        raise ValueError(f"evaluate_5card requires exactly 5 cards, got {len(cards)}")
    
    ranks = sorted([RANK_ORDER[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]

    is_flush = len(set(suits)) == 1

    # Check straight
    is_straight = False
    straight_high = -1
    if len(set(ranks)) == 5:
        if ranks[0] - ranks[4] == 4:
            is_straight = True
            straight_high = ranks[0]
        elif ranks == [12, 3, 2, 1, 0]:  # A-2-3-4-5 wheel straight
            is_straight = True
            straight_high = 3  # 5-high straight

    if is_flush and is_straight:
        return (8, straight_high)

    counts = Counter(ranks)
    # Sort primarily by frequency desc, secondarily by rank desc
    freq = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    if freq[0][1] == 4:
        return (7, freq[0][0], freq[1][0])  # 4 of a kind, kicker

    if freq[0][1] == 3 and freq[1][1] == 2:
        return (6, freq[0][0], freq[1][0])  # Full house (trips rank, pair rank)

    if is_flush:
        return (5, tuple(ranks))

    if is_straight:
        return (4, straight_high)

    if freq[0][1] == 3:
        kickers = tuple(sorted([r for r, c in counts.items() if c == 1], reverse=True))
        return (3, freq[0][0], kickers)

    if freq[0][1] == 2 and freq[1][1] == 2:
        pair1, pair2 = max(freq[0][0], freq[1][0]), min(freq[0][0], freq[1][0])
        kicker = [r for r, c in counts.items() if c == 1][0]
        return (2, pair1, pair2, kicker)

    if freq[0][1] == 2:
        pair = freq[0][0]
        kickers = tuple(sorted([r for r, c in counts.items() if c == 1], reverse=True))
        return (1, pair, kickers)

    return (0, tuple(ranks))

def evaluate_7card(cards):
    """Finds best 5-card hand among 5, 6, or 7 cards."""
    if len(cards) < 5:
        raise ValueError(f"evaluate_7card requires at least 5 cards, got {len(cards)}")
    if len(cards) == 5:
        return evaluate_5card(cards)
    best = (-1,)
    for combo in itertools.combinations(cards, 5):
        score = evaluate_5card(combo)
        if score > best:
            best = score
    return best

def simulate_hand_vs_hand(hand1, hand2, board=None, iterations=10000, seed=None):
    """
    Monte Carlo equity calculation for hand1 vs hand2 with optional known board.
    Supports deterministic reproducibility when seed is passed.
    """
    h1 = parse_cards(hand1)
    h2 = parse_cards(hand2)
    bd = parse_cards(board) if board else []

    if len(h1) != 2 or len(h2) != 2:
        raise ValueError("Each player must have exactly 2 hole cards.")
    if len(bd) > 5:
        raise ValueError(f"Board cannot contain more than 5 cards (got {len(bd)}).")

    all_cards = h1 + h2 + bd
    if len(set(all_cards)) != len(all_cards):
        dups = [c for c, count in Counter(all_cards).items() if count > 1]
        raise ValueError(f"Duplicate card detected in simulation input: {dups}")

    cards_needed = 5 - len(bd)
    full_deck = [r + s for r in RANKS for s in SUITS]
    dead_cards = set(all_cards)
    remaining_deck = [c for c in full_deck if c not in dead_cards]

    # Deterministic RNG if seed provided
    rng = random.Random(seed) if seed is not None else random

    wins1 = 0
    wins2 = 0
    ties = 0

    if cards_needed == 0:
        # Board is complete (river showdown)
        s1 = evaluate_7card(h1 + bd)
        s2 = evaluate_7card(h2 + bd)
        if s1 > s2:
            return 100.0, 0.0, 1, 0, 0
        elif s2 > s1:
            return 0.0, 100.0, 0, 1, 0
        else:
            return 50.0, 50.0, 0, 0, 1

    for _ in range(iterations):
        runout = rng.sample(remaining_deck, cards_needed)
        full_board = bd + runout
        score1 = evaluate_7card(h1 + full_board)
        score2 = evaluate_7card(h2 + full_board)

        if score1 > score2:
            wins1 += 1
        elif score2 > score1:
            wins2 += 1
        else:
            ties += 1

    eq1 = (wins1 + (ties / 2.0)) / iterations * 100.0
    eq2 = (wins2 + (ties / 2.0)) / iterations * 100.0
    return eq1, eq2, wins1, wins2, ties

def run_monte_carlo_simulation(hero_hand, villain_hand, board="", trials=100000, seed=None):
    """
    Public standard API for Monte Carlo simulation.
    Returns structured results dictionary matching API requirements.
    """
    t0 = time.time()
    eq1, eq2, w1, w2, ties = simulate_hand_vs_hand(
        hero_hand, villain_hand, board=board, iterations=trials, seed=seed
    )
    dt = time.time() - t0

    h1_parsed = parse_cards(hero_hand)
    h2_parsed = parse_cards(villain_hand)
    bd_parsed = parse_cards(board)

    return {
        "hero_equity": round(eq1 / 100.0, 4),
        "villain_equity": round(eq2 / 100.0, 4),
        "hero_equity_pct": round(eq1, 2),
        "villain_equity_pct": round(eq2, 2),
        "win_rate": round(w1 / float(trials), 4),
        "villain_win_rate": round(w2 / float(trials), 4),
        "tie_rate": round(ties / float(trials), 4),
        "hero_wins": w1,
        "villain_wins": w2,
        "ties": ties,
        "trials": trials,
        "hero_hand": " ".join(h1_parsed),
        "villain_hand": " ".join(h2_parsed),
        "board": " ".join(bd_parsed) if bd_parsed else "None",
        "elapsed_seconds": round(dt, 3),
        "iterations_per_sec": int(trials / dt) if dt > 0 else trials,
        "seed": seed
    }

def print_dataset_summary(rows):
    """Summarize the preflop equity matrix dataset distribution."""
    total = len(rows)
    print("=" * 76)
    print("APPLIED PROBABILITY INSTITUTE // POKER RESEARCH DATASET SUMMARY")
    print("Study: Texas Hold'em 1,326 Discrete Preflop Equity Matrix")
    print(f"Sample Size: {total:,} Starting Hand Combinations (169 Canonical Classes)")
    print("=" * 76)

    tiers = defaultdict(list)
    for r in rows:
        eq_val = float(r.get("equity_vs_random_pct", r.get("equity_vs_any2", 0.0)))
        tier_name = r.get("tier", "Standard")
        tiers[tier_name].append(eq_val)

    print("\n--- 1. PREFLOP EQUITY DISTRIBUTION BY HAND TIER ---")
    print(f"{'Hand Tier':<22} | {'Combos':<8} | {'% of Range':<12} | {'Mean Eq vs Rand':<16} | {'Range [Min, Max]'}")
    print("-" * 76)
    for t_name in sorted(tiers.keys()):
        eqs = tiers[t_name]
        cnt = len(eqs)
        pct = (cnt / total) * 100.0
        mean_eq = sum(eqs) / cnt
        print(f"{t_name:<22} | {cnt:<8} | {pct:>10.2f}% | {mean_eq:>14.2f}% | [{min(eqs):.2f}%, {max(eqs):.2f}%]")

    suited = [float(r.get("equity_vs_random_pct", 0.0)) for r in rows if r.get("hand_type") == "suited"]
    offsuit = [float(r.get("equity_vs_random_pct", 0.0)) for r in rows if r.get("hand_type") == "offsuit"]
    pairs = [float(r.get("equity_vs_random_pct", 0.0)) for r in rows if r.get("hand_type") == "pair"]

    print("\n--- 2. HAND MORPHOLOGY & SUITEDNESS ADVANTAGE ---")
    print(f"{'Category':<16} | {'Total Combos':<14} | {'Mean Equity vs Rand':<22}")
    print("-" * 76)
    if pairs:
        print(f"{'Pocket Pairs':<16} | {len(pairs):<14} | {sum(pairs)/len(pairs):>20.2f}%")
    if suited:
        print(f"{'Suited Hands':<16} | {len(suited):<14} | {sum(suited)/len(suited):>20.2f}%")
    if offsuit:
        print(f"{'Offsuit Hands':<16} | {len(offsuit):<14} | {sum(offsuit)/len(offsuit):>20.2f}%")

    if suited and offsuit:
        diff = (sum(suited)/len(suited)) - (sum(offsuit)/len(offsuit))
        print(f"\n[+] Empirical Suited Equity Delta: +{diff:.2f}% showdown equity over unsuited equivalents.")
    print("=" * 76)

# Alias for backward compatibility
print_empirical_audit = print_dataset_summary

def main():
    parser = argparse.ArgumentParser(description="PokerMath Monte Carlo Range Simulation Engine")
    parser.add_argument("--hero", type=str, help="Hero hole cards (e.g. 'As Ah')")
    parser.add_argument("--villain", type=str, help="Villain hole cards (e.g. 'Ks Kh')")
    parser.add_argument("--board", type=str, default="", help="Known community cards (e.g. 'Qd Jc Ts')")
    parser.add_argument("--trials", type=int, default=50000, help="Number of Monte Carlo iterations")
    parser.add_argument("--seed", type=int, default=None, help="Deterministic random seed for reproducibility")
    parser.add_argument("--verify", action="store_true", help="Inspect and audit 1,326 dataset distribution")
    parser.add_argument("--benchmark", action="store_true", help="Run high-throughput Monte Carlo benchmark")
    args = parser.parse_args()

    if args.hero and args.villain:
        res = run_monte_carlo_simulation(args.hero, args.villain, board=args.board, trials=args.trials, seed=args.seed)
        print(f"\n[PokerMath Engine] Simulation: {res['hero_hand']} vs {res['villain_hand']} | Board: [{res['board']}]")
        print(f"Iterations: {res['trials']:,} | Elapsed: {res['elapsed_seconds']}s ({res['iterations_per_sec']:,} boards/sec)")
        if args.seed is not None:
            print(f"Deterministic Seed: {args.seed}")
        print("-" * 50)
        print(f"  Hero Equity:    {res['hero_equity_pct']}% ({res['hero_wins']:,} wins)")
        print(f"  Villain Equity: {res['villain_equity_pct']}% ({res['villain_wins']:,} wins)")
        print(f"  Ties:           {res['ties']:,} ({res['tie_rate']*100:.2f}%)")
        return

    if args.benchmark:
        print("\n[PokerMath Engine] Running Monte Carlo Benchmark (AsKs vs QhQc, 100,000 iterations)...")
        res = run_monte_carlo_simulation("As Ks", "Qh Qc", trials=100000, seed=42)
        print(f"Finished in {res['elapsed_seconds']}s ({res['iterations_per_sec']:,} boards/sec)")
        print(f"  AsKs Equity: {res['hero_equity_pct']}% (Expected: ~46.10%)")
        print(f"  QhQc Equity: {res['villain_equity_pct']}% (Expected: ~53.90%)")
        return

    rows = load_matrix()
    if rows:
        print_dataset_summary(rows)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
