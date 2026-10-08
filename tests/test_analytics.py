import unittest

from src.fimr.analytics import compare_to_benchmark, portfolio_metrics, risk_flags, scenario_analysis, weighted_average
from src.fimr.models import BondHolding


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.holdings = [
            BondHolding("A", "Government", "AAA", 100, 100, 0.04, 2.0, 0.0, 0.0),
            BondHolding("B", "Corporate", "BBB", 100, 100, 0.06, 4.0, 3.5, 0.01),
        ]

    def test_weighted_average(self):
        self.assertAlmostEqual(weighted_average(self.holdings, "yield_to_worst"), 0.05)

    def test_portfolio_metrics_basic(self):
        metrics = portfolio_metrics(self.holdings)
        self.assertEqual(metrics["holding_count"], 2)
        self.assertAlmostEqual(metrics["total_market_value"], 200.0)
        self.assertAlmostEqual(metrics["weighted_duration"], 3.0)
        self.assertAlmostEqual(sum(metrics["sector_weights"].values()), 1.0)
        self.assertAlmostEqual(sum(metrics["rating_weights"].values()), 1.0)

    def test_scenario_analysis_direction(self):
        scenarios = {"up": {"rate_change": 0.01, "spread_change": 0.0}}
        result = scenario_analysis(self.holdings, scenarios)
        self.assertLess(result["up"]["total_pnl"], 0)
        self.assertLess(result["up"]["return_estimate"], 0)

    def test_compare_to_benchmark(self):
        diffs = compare_to_benchmark({"Government": 0.6, "Corporate": 0.4}, {"Government": 0.5, "Corporate": 0.5})
        self.assertAlmostEqual(diffs["Government"], 0.1)
        self.assertAlmostEqual(diffs["Corporate"], -0.1)

    def test_risk_flags_none(self):
        diversified_holdings = [
            BondHolding("A", "Government", "AAA", 100, 100, 0.04, 2.0, 0.0, 0.0),
            BondHolding("B", "Corporate", "BBB", 100, 100, 0.06, 4.0, 3.5, 0.01),
            BondHolding("C", "Securitized", "AA", 100, 100, 0.05, 3.0, 2.0, 0.008),
            BondHolding("D", "Municipal", "A", 100, 100, 0.045, 3.5, 1.5, 0.006),
        ]
        metrics = portfolio_metrics(diversified_holdings)
        flags = risk_flags(metrics)
        self.assertTrue(any("No simple threshold breaches" in f for f in flags))

    def test_risk_flags_trigger(self):
        holdings = [
            BondHolding("X", "Corporate", "BB", 100, 100, 0.08, 7.0, 6.5, 0.03),
            BondHolding("Y", "Corporate", "BB", 10, 100, 0.08, 7.0, 6.5, 0.03),
        ]
        metrics = portfolio_metrics(holdings)
        flags = risk_flags(metrics)
        self.assertTrue(any("Single-position concentration" in f for f in flags))
        self.assertTrue(any("Sector concentration" in f for f in flags))
        self.assertTrue(any("duration exceeds 6.0" in f for f in flags))
        self.assertTrue(any("High-yield exposure exceeds 35%" in f for f in flags))

    def test_risk_flags_largest_position_alone_is_not_concentration_breach(self):
        balanced_single_name_holding_fixture = [
            BondHolding("A", "Government", "AAA", 250, 100, 0.04, 2.0, 0.0, 0.0),
            BondHolding("B", "Corporate", "BBB", 250, 100, 0.06, 4.0, 3.5, 0.01),
            BondHolding("C", "Securitized", "AA", 250, 100, 0.05, 3.0, 2.0, 0.008),
            BondHolding("D", "Municipal", "A", 250, 100, 0.045, 3.5, 1.5, 0.006),
        ]
        metrics = portfolio_metrics(balanced_single_name_holding_fixture)
        self.assertAlmostEqual(metrics["largest_position_weight"], 0.25)
        self.assertLessEqual(max(metrics["sector_weights"].values()), 0.25)
        flags = risk_flags(metrics)
        self.assertFalse(any("Single-position concentration" in f for f in flags))

    def test_single_position_above_boundary_triggers_across_multiple_sectors(self):
        holdings = [
            BondHolding("A", "Government", "AAA", 260, 100, 0.04, 2.0, 0.0, 0.0),
            BondHolding("B", "Corporate", "BBB", 240, 100, 0.06, 4.0, 3.5, 0.01),
            BondHolding("C", "Securitized", "AA", 250, 100, 0.05, 3.0, 2.0, 0.008),
            BondHolding("D", "Municipal", "A", 250, 100, 0.045, 3.5, 1.5, 0.006),
        ]
        metrics = portfolio_metrics(holdings)
        self.assertAlmostEqual(metrics["largest_position_weight"], 0.26)
        flags = risk_flags(metrics)
        self.assertTrue(any("Single-position concentration" in flag for flag in flags))
        self.assertFalse(any("Sector concentration" in flag for flag in flags))

    def test_risk_flags_single_name_concentration_with_one_sector_still_triggers(self):
        holdings = [
            BondHolding("ONLY_BIG", "Corporate", "BBB", 300, 100, 0.05, 4.0, 3.0, 0.01),
            BondHolding("ONLY_SMALL", "Corporate", "BBB", 50, 100, 0.05, 4.0, 3.0, 0.01),
            BondHolding("ONLY_SMALLER", "Corporate", "BBB", 25, 100, 0.05, 4.0, 3.0, 0.01),
        ]
        metrics = portfolio_metrics(holdings)
        flags = risk_flags(metrics)
        self.assertTrue(any("Single-position concentration" in f for f in flags))
        self.assertTrue(any("Sector concentration" in f for f in flags))

    def test_risk_flags_regression_original_fixture_was_actually_a_single_name_breach(self):
        metrics = portfolio_metrics(self.holdings)
        self.assertAlmostEqual(metrics["largest_position_weight"], 0.5)
        self.assertEqual(metrics["sector_weights"], {"Corporate": 0.5, "Government": 0.5})
        flags = risk_flags(metrics)
        self.assertTrue(any("Single-position concentration" in f for f in flags))
        self.assertTrue(any("Sector concentration" in f for f in flags))

    def test_scenario_analysis_zero_shock(self):
        scenarios = {"flat": {"rate_change": 0.0, "spread_change": 0.0}}
        result = scenario_analysis(self.holdings, scenarios)
        self.assertAlmostEqual(result["flat"]["pnl_rate"], 0.0)
        self.assertAlmostEqual(result["flat"]["pnl_spread"], 0.0)
        self.assertAlmostEqual(result["flat"]["total_pnl"], 0.0)
        self.assertAlmostEqual(result["flat"]["return_estimate"], 0.0)

    def test_compare_to_benchmark_includes_missing_sectors_from_both_sides(self):
        diffs = compare_to_benchmark(
            {"Government": 0.4, "Corporate": 0.6},
            {"Government": 0.5, "Municipal": 0.5},
        )
        self.assertAlmostEqual(diffs["Government"], -0.1)
        self.assertAlmostEqual(diffs["Corporate"], 0.6)
        self.assertAlmostEqual(diffs["Municipal"], -0.5)


if __name__ == "__main__":
    unittest.main()
