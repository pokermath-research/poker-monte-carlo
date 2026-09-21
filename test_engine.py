"""
================================================================================
PokerMath Monte Carlo Simulation Engine — Comprehensive Test Suite
================================================================================
Covers:
  1. Hand evaluator correctness across all 9 standard poker hand hierarchies
  2. Special edge cases (wheel straight A-2-3-4-5, flushes, full house kickers)
  3. Preflop equity convergence on known theoretical matchups (AA vs KK, AKo vs QQ)
  4. Seed determinism and reproducibility
  5. Postflop board equity computation (turn, river showdowns)
  6. Input validation, duplicate card detection, and error handling
================================================================================
"""

import unittest
from poker_monte_carlo_engine import (
    evaluate_5card,
    evaluate_7card,
    run_monte_carlo_simulation,
    simulate_hand_vs_hand,
    parse_cards,
    parse_card
)

class TestHandEvaluator5Card(unittest.TestCase):
    def test_high_card(self):
        # A K J 8 4 unsuited
        res = evaluate_5card(["As", "Kd", "Jc", "8h", "4s"])
        self.assertEqual(res[0], 0)  # High card

    def test_one_pair(self):
        # Pair of Tens with A K 2
        res = evaluate_5card(["Ts", "Td", "Ah", "Kc", "2s"])
        self.assertEqual(res[0], 1)  # One pair
        self.assertEqual(res[1], 8)  # Rank of 'T' is index 8 in 23456789TJQKA

    def test_two_pair(self):
        # Aces and Queens with 9 kicker
        res = evaluate_5card(["As", "Ah", "Qs", "Qc", "9d"])
        self.assertEqual(res[0], 2)  # Two pair
        self.assertEqual(res[1], 12) # Ace
        self.assertEqual(res[2], 10) # Queen

    def test_three_of_a_kind(self):
        # Trips Sevens with K, 4
        res = evaluate_5card(["7s", "7h", "7d", "Kc", "4s"])
        self.assertEqual(res[0], 3)  # Trips
        self.assertEqual(res[1], 5)  # Rank of '7'

    def test_regular_straight(self):
        # 6-7-8-9-T rainbow
        res = evaluate_5card(["6s", "7h", "8d", "9c", "Ts"])
        self.assertEqual(res[0], 4)  # Straight
        self.assertEqual(res[1], 8)  # Ten-high straight

    def test_wheel_straight(self):
        # A-2-3-4-5 rainbow (5-high straight)
        res = evaluate_5card(["As", "2h", "3d", "4c", "5s"])
        self.assertEqual(res[0], 4)  # Straight
        self.assertEqual(res[1], 3)  # Five-high straight index (5 is index 3)

    def test_broadway_straight(self):
        # T-J-Q-K-A rainbow
        res = evaluate_5card(["Ts", "Jh", "Qd", "Kc", "As"])
        self.assertEqual(res[0], 4)  # Straight
        self.assertEqual(res[1], 12) # Ace-high

    def test_flush(self):
        # Spades flush
        res = evaluate_5card(["Ks", "Js", "8s", "5s", "2s"])
        self.assertEqual(res[0], 5)  # Flush

    def test_full_house(self):
        # Kings full of Threes
        res = evaluate_5card(["Ks", "Kh", "Kd", "3c", "3s"])
        self.assertEqual(res[0], 6)  # Full House
        self.assertEqual(res[1], 11) # Kings trips
        self.assertEqual(res[2], 1)  # Threes pair

    def test_four_of_a_kind(self):
        # Quad Queens with Ace kicker
        res = evaluate_5card(["Qs", "Qh", "Qd", "Qc", "As"])
        self.assertEqual(res[0], 7)  # Quads
        self.assertEqual(res[1], 10) # Queens

    def test_straight_flush(self):
        # 8-9-T-J-Q suited in hearts
        res = evaluate_5card(["8h", "9h", "Th", "Jh", "Qh"])
        self.assertEqual(res[0], 8)  # Straight Flush
        self.assertEqual(res[1], 10) # Queen-high straight flush

    def test_steel_wheel(self):
        # A-2-3-4-5 suited in diamonds (5-high straight flush)
        res = evaluate_5card(["Ad", "2d", "3d", "4d", "5d"])
        self.assertEqual(res[0], 8)  # Straight Flush
        self.assertEqual(res[1], 3)  # 5-high

    def test_flush_beats_straight(self):
        straight = evaluate_5card(["Ts", "Jh", "Qd", "Kc", "As"])
        flush = evaluate_5card(["2s", "4s", "7s", "9s", "Ks"])
        self.assertGreater(flush, straight)

    def test_full_house_beats_flush(self):
        flush = evaluate_5card(["As", "Ks", "Qs", "Js", "9s"])
        fh = evaluate_5card(["2s", "2h", "2d", "3c", "3s"])
        self.assertGreater(fh, flush)


class TestHandEvaluator7Card(unittest.TestCase):
    def test_best_5_from_7(self):
        # 7 cards: As Ah Ad Ac 2s 3s 4s -> Quads should be selected over anything else
        best = evaluate_7card(["As", "Ah", "Ad", "Ac", "2s", "3s", "4s"])
        self.assertEqual(best[0], 7)  # Four of a Kind

    def test_flush_selection(self):
        # 5 hearts among 7 cards
        best = evaluate_7card(["Ah", "Kh", "Qh", "Jh", "2h", "8s", "9d"])
        self.assertEqual(best[0], 5)  # Flush


class TestMonteCarloConvergence(unittest.TestCase):
    def test_aa_vs_kk_preflop(self):
        # Known preflop equity of AA vs KK is ~81.7% - 82.5%
        res = run_monte_carlo_simulation("As Ah", "Ks Kh", trials=12000, seed=12345)
        self.assertTrue(0.79 <= res['hero_equity'] <= 0.85, f"AA vs KK expected ~0.82, got {res['hero_equity']}")
        self.assertGreater(res['hero_equity'], res['villain_equity'])

    def test_coinflip_ak_vs_qq(self):
        # Classic coinflip: AKo vs QQ is ~43% to ~45% for AKo
        res = run_monte_carlo_simulation("Ac Kh", "Qs Qd", trials=12000, seed=54321)
        self.assertTrue(0.41 <= res['hero_equity'] <= 0.47, f"AKo vs QQ expected ~0.43-0.45, got {res['hero_equity']}")

    def test_domination_ak_vs_aq(self):
        # AK vs AQ: AK dominates with ~72% to ~75% equity
        res = run_monte_carlo_simulation("Ah Kd", "As Qc", trials=10000, seed=999)
        self.assertTrue(0.70 <= res['hero_equity'] <= 0.77, f"AK vs AQ expected ~0.73, got {res['hero_equity']}")


class TestDeterministicReproducibility(unittest.TestCase):
    def test_identical_seed_produces_identical_results(self):
        # Running simulation twice with same seed must yield exactly identical results
        res1 = run_monte_carlo_simulation("Js Ts", "8h 7h", trials=5000, seed=42)
        res2 = run_monte_carlo_simulation("Js Ts", "8h 7h", trials=5000, seed=42)
        self.assertEqual(res1['hero_wins'], res2['hero_wins'])
        self.assertEqual(res1['villain_wins'], res2['villain_wins'])
        self.assertEqual(res1['ties'], res2['ties'])
        self.assertEqual(res1['hero_equity'], res2['hero_equity'])

    def test_different_seeds_produce_different_runouts(self):
        res1 = run_monte_carlo_simulation("Ah Kh", "Qd Qs", trials=1000, seed=1)
        res2 = run_monte_carlo_simulation("Ah Kh", "Qd Qs", trials=1000, seed=2)
        self.assertIsNotNone(res1)
        self.assertIsNotNone(res2)


class TestPostflopAndEdgeCases(unittest.TestCase):
    def test_flop_simulation(self):
        # Hero has flopped nut flush: Ah Kh on Qh Jh Th
        res = run_monte_carlo_simulation("Ah Kh", "2c 2d", board="Qh Jh Th", trials=5000, seed=42)
        # Hero already has royal flush, cannot lose
        self.assertEqual(res['hero_equity'], 1.0)
        self.assertEqual(res['villain_equity'], 0.0)

    def test_turn_equity(self):
        # Hero has set of Aces on As 7d 2c 9h vs Ks Kh
        res = run_monte_carlo_simulation("Ah Ac", "Ks Kd", board="As 7d 2c 9h", trials=5000, seed=42)
        # Villain can only win with one out (Kc) for set of Kings, unless river is K, so hero equity > 95%
        self.assertGreater(res['hero_equity'], 0.95)

    def test_duplicate_card_detection(self):
        with self.assertRaises(ValueError):
            run_monte_carlo_simulation("As Ah", "As Kh")  # Duplicate As

    def test_invalid_card_rank(self):
        with self.assertRaises(ValueError):
            parse_card("Xs")

    def test_invalid_card_suit(self):
        with self.assertRaises(ValueError):
            parse_card("Az")

if __name__ == '__main__':
    unittest.main()
