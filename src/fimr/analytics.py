from __future__ import annotations

from typing import Dict, Iterable, List

from .models import BondHolding


IG_RATINGS = {"AAA", "AA", "A", "BBB"}
HY_RATINGS = {"BB", "B", "CCC", "CC", "C", "D"}


def _weights(holdings: Iterable[BondHolding]) -> List[float]:
    holdings = list(holdings)
    total_mv = sum(h.market_value for h in holdings)
    if total_mv <= 0:
        raise ValueError("total market value must be positive")
    return [h.market_value / total_mv for h in holdings]


def weighted_average(holdings: Iterable[BondHolding], attr: str) -> float:
    holdings = list(holdings)
    weights = _weights(holdings)
    return sum(w * getattr(h, attr) for h, w in zip(holdings, weights))


def bucket_weights(holdings: Iterable[BondHolding], attr: str) -> Dict[str, float]:
    holdings = list(holdings)
    total_mv = sum(h.market_value for h in holdings)
    if total_mv <= 0:
        raise ValueError("total market value must be positive")
    result: Dict[str, float] = {}
    for h in holdings:
        key = getattr(h, attr)
        result[key] = result.get(key, 0.0) + h.market_value / total_mv
    return dict(sorted(result.items(), key=lambda kv: (-kv[1], kv[0])))


def quality_split(rating_weights: Dict[str, float]) -> Dict[str, float]:
    ig = sum(weight for rating, weight in rating_weights.items() if rating in IG_RATINGS)
    hy = sum(weight for rating, weight in rating_weights.items() if rating in HY_RATINGS)
    other = max(0.0, 1.0 - ig - hy)
    return {"investment_grade": ig, "high_yield": hy, "other": other}


def portfolio_metrics(holdings: Iterable[BondHolding]) -> Dict[str, object]:
    holdings = list(holdings)
    total_market_value = sum(h.market_value for h in holdings)
    sector_weights = bucket_weights(holdings, "sector")
    rating_weights = bucket_weights(holdings, "rating")
    return {
        "holding_count": len(holdings),
        "total_market_value": total_market_value,
        "weighted_yield": weighted_average(holdings, "yield_to_worst"),
        "weighted_duration": weighted_average(holdings, "modified_duration"),
        "weighted_spread_duration": weighted_average(holdings, "spread_duration"),
        "weighted_spread": weighted_average(holdings, "spread"),
        "sector_weights": sector_weights,
        "rating_weights": rating_weights,
        "quality_split": quality_split(rating_weights),
        "largest_position_weight": max(_weights(holdings)),
    }


def scenario_analysis(holdings: Iterable[BondHolding], scenarios: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    holdings = list(holdings)
    total_mv = sum(h.market_value for h in holdings)
    if total_mv <= 0:
        raise ValueError("total market value must be positive")
    results: Dict[str, Dict[str, float]] = {}
    for name, scenario in scenarios.items():
        rate_change = float(scenario["rate_change"])
        spread_change = float(scenario["spread_change"])
        pnl_rate = sum(-h.modified_duration * rate_change * h.market_value for h in holdings)
        pnl_spread = sum(-h.spread_duration * spread_change * h.market_value for h in holdings)
        total_pnl = pnl_rate + pnl_spread
        results[name] = {
            "pnl_rate": pnl_rate,
            "pnl_spread": pnl_spread,
            "total_pnl": total_pnl,
            "return_estimate": total_pnl / total_mv,
        }
    return results


def compare_to_benchmark(portfolio_sector_weights: Dict[str, float], benchmark_sector_weights: Dict[str, float]) -> Dict[str, float]:
    sectors = set(portfolio_sector_weights) | set(benchmark_sector_weights)
    diffs = {}
    for sector in sectors:
        diffs[sector] = portfolio_sector_weights.get(sector, 0.0) - benchmark_sector_weights.get(sector, 0.0)
    return dict(sorted(diffs.items(), key=lambda kv: (-abs(kv[1]), kv[0])))


def risk_flags(metrics: Dict[str, object]) -> List[str]:
    flags: List[str] = []
    largest = float(metrics["largest_position_weight"])
    duration = float(metrics["weighted_duration"])
    quality = metrics["quality_split"]
    hy = float(quality["high_yield"])
    sectors = metrics["sector_weights"]
    max_sector = max(sectors.values()) if sectors else 0.0

    if largest > 0.25:
        flags.append("Single-position concentration exceeds 25% of market value.")
    if max_sector > 0.45:
        flags.append("Sector concentration exceeds 45% of market value.")
    if duration > 6.0:
        flags.append("Portfolio duration exceeds 6.0 years; interest-rate sensitivity is elevated.")
    if hy > 0.35:
        flags.append("High-yield exposure exceeds 35% of market value.")
    if not flags:
        flags.append("No simple threshold breaches detected under configured checks.")
    return flags
