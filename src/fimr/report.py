from __future__ import annotations

from typing import Dict, List


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def _fmt_num(x: float) -> str:
    return f"{x:,.2f}"


def build_report(
    metrics: Dict[str, object],
    scenario_results: Dict[str, Dict[str, float]],
    benchmark_diff: Dict[str, float],
    flags: List[str],
) -> str:
    lines: List[str] = []
    lines.append("FIXED INCOME MINI RISK MONITOR")
    lines.append("=" * 32)
    lines.append("")
    lines.append("Portfolio summary")
    lines.append(f"- Holdings: {metrics['holding_count']}")
    lines.append(f"- Total market value: {_fmt_num(float(metrics['total_market_value']))}")
    lines.append(f"- Weighted yield: {_fmt_pct(float(metrics['weighted_yield']))}")
    lines.append(f"- Weighted duration: {float(metrics['weighted_duration']):.2f}")
    lines.append(f"- Weighted spread duration: {float(metrics['weighted_spread_duration']):.2f}")
    lines.append(f"- Weighted spread: {_fmt_pct(float(metrics['weighted_spread']))}")
    lines.append("")

    lines.append("Sector weights")
    for sector, weight in metrics["sector_weights"].items():
        lines.append(f"- {sector}: {_fmt_pct(weight)}")
    lines.append("")

    lines.append("Rating weights")
    for rating, weight in metrics["rating_weights"].items():
        lines.append(f"- {rating}: {_fmt_pct(weight)}")
    lines.append("")

    lines.append("Credit quality split")
    for name, weight in metrics["quality_split"].items():
        lines.append(f"- {name}: {_fmt_pct(weight)}")
    lines.append("")

    lines.append("Scenario stress estimates")
    for name, values in scenario_results.items():
        lines.append(
            f"- {name}: total_pnl={_fmt_num(values['total_pnl'])}, "
            f"return_estimate={_fmt_pct(values['return_estimate'])}"
        )
    lines.append("")

    lines.append("Sector weights vs synthetic benchmark")
    for sector, diff in benchmark_diff.items():
        sign = "+" if diff >= 0 else ""
        lines.append(f"- {sector}: {sign}{_fmt_pct(diff)}")
    lines.append("")

    lines.append("Risk flags")
    for flag in flags:
        lines.append(f"- {flag}")
    lines.append("")
    lines.append("Disclaimer: educational independent project using synthetic data and simplified assumptions.")
    return "\n".join(lines)
