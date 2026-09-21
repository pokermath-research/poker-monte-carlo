"""
Automated unit tests for PokerMath Monte Carlo equity engine.
"""
import unittest
from poker_monte_carlo_engine import run_monte_carlo_simulation

class TestPokerMonteCarlo(unittest.TestCase):
    def test_aa_vs_kk(self):
        # Known preflop equity of AA vs KK is ~81.7% to ~82.3%
        res = run_monte_carlo_simulation("As Ah", "Ks Kh", trials=20000)
        hero_win = res.get('hero_equity', res.get('win_rate', 0.0))
        self.assertTrue(0.79 <= hero_win <= 0.85, f"AA vs KK expected ~0.82, got {hero_win}")

    def test_coinflip_ak_vs_qq(self):
        # Classic coinflip: AKo vs QQ is ~43% to ~45% for AKo
        res = run_monte_carlo_simulation("Ac Kh", "Qs Qd", trials=20000)
        hero_win = res.get('hero_equity', res.get('win_rate', 0.0))
        self.assertTrue(0.40 <= hero_win <= 0.48, f"AKo vs QQ expected ~0.44, got {hero_win}")

if __name__ == '__main__':
    unittest.main()
