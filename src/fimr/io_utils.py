from __future__ import annotations

import csv
import json
from typing import Dict, List

from .models import BondHolding


REQUIRED_COLUMNS = {
    "identifier",
    "sector",
    "rating",
    "par_amount",
    "price",
    "yield_to_worst",
    "modified_duration",
    "spread_duration",
    "spread",
}


def load_holdings_csv(path: str) -> List[BondHolding]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")

        holdings = []
        for row in reader:
            holdings.append(
                BondHolding(
                    identifier=row["identifier"].strip(),
                    sector=row["sector"].strip(),
                    rating=row["rating"].strip(),
                    par_amount=float(row["par_amount"]),
                    price=float(row["price"]),
                    yield_to_worst=float(row["yield_to_worst"]),
                    modified_duration=float(row["modified_duration"]),
                    spread_duration=float(row["spread_duration"]),
                    spread=float(row["spread"]),
                )
            )
    if not holdings:
        raise ValueError("holdings file contains no rows")
    return holdings


def load_scenarios(path: str) -> Dict[str, Dict[str, float]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        raise ValueError("scenarios must be a non-empty object")
    for name, scenario in data.items():
        if not isinstance(scenario, dict):
            raise ValueError(f"scenario {name} must be an object")
        if "rate_change" not in scenario or "spread_change" not in scenario:
            raise ValueError(f"scenario {name} missing required keys")
    return data


def load_benchmark_weights(path: str) -> Dict[str, float]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        raise ValueError("benchmark weights must be a non-empty object")
    total = 0.0
    for sector, weight in data.items():
        if not sector.strip():
            raise ValueError("benchmark sector names must be non-empty")
        if weight < 0:
            raise ValueError("benchmark weights cannot be negative")
        total += float(weight)
    if total <= 0:
        raise ValueError("benchmark weights sum must be positive")
    return {k: float(v) for k, v in data.items()}
