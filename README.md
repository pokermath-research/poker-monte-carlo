# High-Performance Poker Monte Carlo Simulation Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Tests: 26 Passing](https://img.shields.io/badge/Tests-26%20Passing-brightgreen.svg)](https://github.com/pokermath-research/poker-monte-carlo)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-blue.svg)](https://github.com/pokermath-research/poker-monte-carlo)

High-throughput, reproducible **Monte Carlo simulation engine** for Texas Hold'em equity computation, range-versus-range equity distribution mapping, and multi-street variance decomposition. Zero external dependencies (pure Python standard library).

Engineered by the **PokerMath Stochastic & Risk Lab** at [pokermath.org](https://pokermath.org).

---

## Mathematical Foundations & Convergence Rate

Evaluating exact deterministic game trees in Texas Hold'em across arbitrary continuous preflop ranges is computationally intensive ($\binom{48}{5} = 1,712,304$ discrete board permutations per matchup).

This engine leverages stochastic Monte Carlo sampling governed by the **Strong Law of Large Numbers**:

$$\hat{E}_N = \frac{1}{N} \sum_{i=1}^{N} \left( \mathbb{I}_{\text{Hero Wins}}(B_i) + \frac{1}{2}\mathbb{I}_{\text{Tie}}(B_i) \right)$$

Where $B_i$ represents an independently sampled community board from the remaining card stub $\mathcal{S}$.

### Standard Error Bound

By the Central Limit Theorem, the empirical equity $\hat{E}_N$ converges to the true expected value $E^*$ with standard error:

$$\sigma_{\hat{E}} = \sqrt{\frac{E^*(1 - E^*)}{N}} \le \frac{0.5}{\sqrt{N}}$$

| Iterations ($N$) | Maximum Standard Error | Precision (95% Confidence Interval) | Typical Execution Time |
| :---: | :---: | :---: | :---: |
| **10,000** | $\pm 0.50\%$ | $\pm 0.98\%$ | ~0.8s |
| **100,000** | $\pm 0.16\%$ | $\pm 0.31\%$ | ~6.5s |
| **1,000,000** | $\pm 0.05\%$ | $\pm 0.10\%$ | ~65s |

---

## Quickstart

### Installation

```bash
git clone https://github.com/pokermath-research/poker-monte-carlo.git
cd poker-monte-carlo
```

No external packages required (zero dependencies).

### CLI Usage

```bash
# Classic Aces vs Kings confrontation (deterministic with --seed)
python simulator.py --hero "As Ah" --villain "Ks Kh" --trials 50000 --seed 42

# Flop equity simulation on a wet board
python simulator.py --hero "Jc Tc" --villain "As Kd" --board "Qc 9c 2d" --trials 50000 --seed 42

# Quick benchmark
python poker_monte_carlo_engine.py --benchmark
```

### Python API

```python
from poker_monte_carlo_engine import run_monte_carlo_simulation

# Run 50,000 deterministic iterations with seed=42
results = run_monte_carlo_simulation(
    hero_hand="Ac Kd",
    villain_hand="Qh Qs",
    board="Jh Ts 2c",
    trials=50000,
    seed=42
)

print(f"Hero Equity: {results['hero_equity_pct']}% ({results['hero_wins']:,} wins)")
print(f"Villain Equity: {results['villain_equity_pct']}% ({results['villain_wins']:,} wins)")
print(f"Tie Rate: {results['tie_rate'] * 100:.2f}%")
print(f"Elapsed: {results['elapsed_seconds']}s")
```

---

## Test Suite & Verification

The test suite contains 26 comprehensive unit tests covering:
- Hand ranking hierarchy across all 9 standard poker hand classes (High Card to Straight Flush)
- Special edge cases: Wheel straight (A-2-3-4-5), broadway straights, flushes vs straights, full house tie-breakers
- 7-card best 5-card evaluation
- Deterministic reproducibility: exact identical win counts verified when using identical RNG seeds
- Convergence sanity on theoretical matchups ($AA$ vs $KK$, $AKo$ vs $QQ$, $AK$ vs $AQ$)
- Flop and turn community board runouts
- Duplicate card detection and invalid input validation

Run tests:
```bash
python -m unittest test_engine.py -v
```

---

## Academic Citation

```bibtex
@software{pokermath_monte_carlo_2026,
  author = {{PokerMath Research Group}},
  title = {Stochastic Monte Carlo Range Equity Engine for Imperfect Information Games},
  year = {2026},
  url = {https://github.com/pokermath-research/poker-monte-carlo}
}
```
