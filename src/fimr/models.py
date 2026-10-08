from __future__ import annotations

from dataclasses import dataclass


VALID_RATINGS = {
    "AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"
}


@dataclass(frozen=True)
class BondHolding:
    identifier: str
    sector: str
    rating: str
    par_amount: float
    price: float
    yield_to_worst: float
    modified_duration: float
    spread_duration: float
    spread: float

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier must be non-empty")
        if not self.sector.strip():
            raise ValueError("sector must be non-empty")
        if self.rating not in VALID_RATINGS:
            raise ValueError(f"unsupported rating: {self.rating}")
        if self.par_amount <= 0:
            raise ValueError("par_amount must be positive")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.modified_duration < 0:
            raise ValueError("modified_duration cannot be negative")
        if self.spread_duration < 0:
            raise ValueError("spread_duration cannot be negative")
        if self.yield_to_worst < 0:
            raise ValueError("yield_to_worst cannot be negative")
        if self.spread < 0:
            raise ValueError("spread cannot be negative")

    @property
    def market_value(self) -> float:
        return self.par_amount * self.price / 100.0
