import json
import os
import tempfile
import unittest

from src.fimr.io_utils import load_benchmark_weights, load_holdings_csv, load_scenarios
from src.fimr.models import BondHolding


class ModelAndIOTests(unittest.TestCase):
    def test_market_value(self):
        h = BondHolding("A", "Government", "AAA", 1000, 99.5, 0.04, 2.0, 0.0, 0.0)
        self.assertAlmostEqual(h.market_value, 995.0)

    def test_invalid_rating(self):
        with self.assertRaises(ValueError):
            BondHolding("A", "Government", "NR", 100, 100, 0.04, 2.0, 0.0, 0.0)

    def test_load_holdings_missing_column(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
            f.write("identifier,sector\nA,Government\n")
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_holdings_csv(path)
        finally:
            os.remove(path)

    def test_load_scenarios_validation(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump({"bad": {"rate_change": 0.01}}, f)
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_scenarios(path)
        finally:
            os.remove(path)

    def test_load_benchmark_weights_validation(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump({"Government": -0.1}, f)
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_benchmark_weights(path)
        finally:
            os.remove(path)

    def test_load_holdings_success(self):
        content = (
            "identifier,sector,rating,par_amount,price,yield_to_worst,modified_duration,spread_duration,spread\n"
            "A,Government,AAA,100,100,0.04,2.0,0.0,0.0\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
            f.write(content)
            path = f.name
        try:
            holdings = load_holdings_csv(path)
            self.assertEqual(len(holdings), 1)
            self.assertEqual(holdings[0].identifier, "A")
        finally:
            os.remove(path)

    def test_load_holdings_empty_file_rows_validation(self):
        content = (
            "identifier,sector,rating,par_amount,price,yield_to_worst,modified_duration,spread_duration,spread\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
            f.write(content)
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_holdings_csv(path)
        finally:
            os.remove(path)

    def test_load_scenarios_success(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump({"base": {"rate_change": 0.0, "spread_change": 0.0}}, f)
            path = f.name
        try:
            scenarios = load_scenarios(path)
            self.assertEqual(scenarios["base"]["rate_change"], 0.0)
            self.assertEqual(scenarios["base"]["spread_change"], 0.0)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
