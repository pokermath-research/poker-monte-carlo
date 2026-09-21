# High-Performance Poker Monte Carlo Simulation Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Research: Stochastic Simulation](https://img.shields.io/badge/Research-pokermath.org-0d6b3d.svg)](https://pokermath.org)

High-throughput, deterministic **Monte Carlo simulation engine** for Texas Hold'em equity computation, range-versus-range equity distribution mapping, and multi-street variance decomposition.

Engineered by the **PokerMath Stochastic & Risk Lab** at [pokermath.org](https://pokermath.org).

---

## Mathematical Foundations & Convergence Rate

Evaluating exact deterministic game trees in Texas Hold'em across arbitrary continuous preflop ranges is computationally intractable ($10^{161}$ potential decision nodes and $\binom{48}{5} = 1,712,304$ discrete board permutations per matchup).

This library leverages stochastic Monte Carlo sampling governed by the **Strong Law of Large Numbers**:

$$\hat{E}_N = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}_{\text{Hero Wins}}(B_i)$$

Where $B_i$ represents an independently sampled 5-card community board from the remaining card stub $\mathcal{S}$.

### Standard Error Bound

By the Central Limit Theorem, the empirical equity $\hat{E}_N$ converges to the true expected value $E^*$ with standard error:

$$\sigma_{\hat{E}} = \sqrt{\frac{E^*(1 - E^*)}{N}} \le \frac{0.5}{\sqrt{N}}$$

| Iterations ($N$) | Maximum Standard Error | Precision (95% Confidence Interval) | Typical Execution Time |
| :---: | :---: | :---: | :---: |
| **10,000** | $\pm 0.50\%$ | $\pm 0.98\%$ | 0.08 sec |
| **100,000** | $\pm 0.16\%$ | $\pm 0.31\%$ | 0.72 sec |
| **1,000,000** | $\pm 0.05\%$ | $\pm 0.10\%$ | 6.80 sec |

---

## Quickstart

### Installation

```bash
git clone https://github.com/pokermath-research/poker-monte-carlo.git
cd poker-monte-carlo
pip install -r requirements.txt
```

### CLI Usage

```bash
# Classic Aces vs Kings confrontation
python simulator.py --hero "As Ah" --villain "Ks Kh" --trials 100000

# Flop equity simulation on a wet board
python simulator.py --hero "Jc Tc" --villain "As Kd" --board "Qc 9c 2d" --trials 100000
```

### Python API

```python
from poker_monte_carlo_engine import run_monte_carlo_simulation

# Run 100,000 iterations
results = run_monte_carlo_simulation(
    hero_hand="Ac Kd",
    villain_hand="Qh Qs",
    board="Jh Ts 2c",
    trials=100000
)

print(f"Hero Equity: {results['hero_equity'] * 100:.2f}%")
print(f"Tie Frequency: {results['tie_rate'] * 100:.2f}%")
```

---

## Running Unit Tests

```bash
python -m unittest test_engine.py
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
