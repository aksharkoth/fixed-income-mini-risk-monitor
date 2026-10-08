import unittest

from src.fimr.report import build_report


class ReportTests(unittest.TestCase):
    def test_build_report_contains_sections(self):
        metrics = {
            "holding_count": 2,
            "total_market_value": 200.0,
            "weighted_yield": 0.05,
            "weighted_duration": 3.0,
            "weighted_spread_duration": 1.75,
            "weighted_spread": 0.005,
            "sector_weights": {"Government": 0.5, "Corporate": 0.5},
            "rating_weights": {"AAA": 0.5, "BBB": 0.5},
            "quality_split": {"investment_grade": 1.0, "high_yield": 0.0, "other": 0.0},
        }
        scenarios = {"up": {"total_pnl": -6.0, "return_estimate": -0.03}}
        benchmark_diff = {"Government": 0.1, "Corporate": -0.1}
        flags = ["No simple threshold breaches detected under configured checks."]
        report = build_report(metrics, scenarios, benchmark_diff, flags)
        self.assertIn("Portfolio summary", report)
        self.assertIn("Sector weights", report)
        self.assertIn("Scenario stress estimates", report)
        self.assertIn("Risk flags", report)
        self.assertIn("Disclaimer", report)


if __name__ == "__main__":
    unittest.main()
