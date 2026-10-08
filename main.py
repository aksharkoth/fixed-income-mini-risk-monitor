from __future__ import annotations

import argparse
from src.fimr.analytics import compare_to_benchmark, portfolio_metrics, risk_flags, scenario_analysis
from src.fimr.io_utils import load_benchmark_weights, load_holdings_csv, load_scenarios
from src.fimr.report import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fixed Income Mini Risk Monitor")
    parser.add_argument("--holdings", required=True, help="Path to holdings CSV")
    parser.add_argument("--scenarios", required=True, help="Path to scenarios JSON")
    parser.add_argument("--benchmark", required=True, help="Path to benchmark sector weights JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    holdings = load_holdings_csv(args.holdings)
    scenarios = load_scenarios(args.scenarios)
    benchmark = load_benchmark_weights(args.benchmark)

    metrics = portfolio_metrics(holdings)
    scenario_results = scenario_analysis(holdings, scenarios)
    benchmark_diff = compare_to_benchmark(metrics["sector_weights"], benchmark)
    flags = risk_flags(metrics)

    report = build_report(metrics, scenario_results, benchmark_diff, flags)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
