# Fixed Income Mini Risk Monitor

An independent educational portfolio project in Python for basic fixed-income portfolio analysis and risk monitoring.

## Independent-project disclaimer
This is an independently created sample project for portfolio demonstration purposes only. It is **not** affiliated with, endorsed by, or connected to DoubleLine or any employer. It does **not** use proprietary data, private systems, internal models, or non-public information. All data included here is synthetic and simplified.

## What it does
Given a small synthetic bond portfolio and scenario inputs, the project:
- loads holdings from CSV
- computes portfolio-level metrics
  - market value
  - weighted yield
  - weighted duration
  - weighted spread
  - sector exposure
  - rating exposure
- runs simple scenario stress tests using duration and spread duration approximations
- compares portfolio sector weights to a synthetic benchmark
- flags simple risk issues such as concentration, low credit quality, and long duration
- generates a reproducible text report

## Why this is relevant
This project is designed to be relevant to internships involving:
- portfolio and security analysis
- basic risk analysis
- monitoring sector trends
- ad hoc research support
- quantitative macro/scenario thinking

## Project structure
- `src/fimr/models.py` - data structures and validation
- `src/fimr/io_utils.py` - CSV/JSON loading helpers
- `src/fimr/analytics.py` - portfolio analytics and risk calculations
- `src/fimr/report.py` - text report generation
- `main.py` - CLI entry point
- `data/holdings.csv` - synthetic sample portfolio
- `data/scenarios.json` - synthetic scenario shocks
- `data/benchmark_sector_weights.json` - synthetic benchmark sector weights
- `tests/` - unit tests

## Setup
Requires Python 3.11+ or similar modern Python 3.

No external packages are needed.

## Reproducible demo
Run:

```bash
python -m unittest discover -s tests -p 'test*.py' && python main.py --holdings data/holdings.csv --scenarios data/scenarios.json --benchmark data/benchmark_sector_weights.json
```

You can also run only the report:

```bash
python main.py --holdings data/holdings.csv --scenarios data/scenarios.json --benchmark data/benchmark_sector_weights.json
```

## Expected output
The script prints a text report with:
- portfolio summary metrics
- sector and rating breakdowns
- scenario stress estimates
- benchmark-relative sector differences
- simple risk flags

## Evaluation approach
This project is intentionally simple and transparent.

Suggested evaluation criteria:
1. **Correctness**
   - weights sum to 1 within tolerance
   - weighted averages match hand-check calculations
   - scenario P&L signs are directionally sensible
2. **Code quality**
   - small functions
   - input validation
   - deterministic outputs
3. **Testing**
   - covers analytics, risk flags, scenario calculations, and edge cases
4. **Relevance**
   - directly demonstrates fixed-income-oriented portfolio analysis concepts

## Key assumptions
- Price is per 100 par.
- Market value = par amount * price / 100.
- Approximate rate P&L uses modified duration: `-duration * rate_change * market_value`.
- Approximate spread P&L uses spread duration: `-spread_duration * spread_change * market_value`.
- Yield and spread are expressed as decimals in input data.
- Ratings are treated categorically with a simple investment-grade / high-yield split.
- Simple concentration checks are independent:
  - single-position concentration is based on the largest security weight
  - sector concentration is based on the largest sector weight

## Limitations
- Not a production risk engine.
- Uses simplified duration-based linear approximations only.
- No convexity, key-rate duration, optionality, prepayment, liquidity, or default modeling.
- No live market data.
- No security-level cash-flow modeling.
- Rating normalization is intentionally basic.
- Benchmark and scenarios are synthetic, not investable or predictive.

## Sample data notes
All sample holdings, sectors, prices, yields, durations, spreads, and scenarios are synthetic and for demonstration only.
