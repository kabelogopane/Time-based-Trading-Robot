# Time-Based Trading Robot

A research and backtesting project that converts Kabelo Gopane's original 45-minute time-based trading model into objective, testable rules.

> **Important:** This project is for research and paper-simulation education. It does not guarantee profitable trading and does not place real-money trades.

## Core Model

**Time decides WHEN to analyze. Price decides WHAT to do. Liquidity decides WHERE to study the reaction.**

The model studies market behavior around repeated time windows using **U.S. Eastern Time / New York time**. ICT/SMC concepts are supporting measurements only; they do not replace the time model.

### Primary model times

| Time (ET) | Role |
|---|---|
| 08:45 | Pre-open observation |
| 09:45 | Primary anchor |
| 10:45 | Post-open reaction |
| 11:45 | Follow-through / structure check |
| 12:45 | Midday observation |
| 13:45 | Early afternoon observation |
| 15:45 | Pre-close observation |

### 09:45 research windows

For detailed backtesting, the 09:45 anchor can also be decomposed into consecutive 45-minute windows:

`09:45→10:30 → 10:30→11:15 → 11:15→12:00 → 12:00→12:45 → ... → 15:00→15:45`

This is a measurement layer. It lets us test what happens inside each 45-minute period before adding entry rules. The window engine uses `[start, end)` boundaries, so a candle exactly on a boundary belongs to the next window.

## Strategy Logic

The robot does **not** assume that 09:45 automatically means BUY or SELL.

1. Detect the time anchor.
2. Build the 45-minute observation windows.
3. Record each window's OHLC, range, and direction.
4. Observe price delivery after the anchor.
5. Classify bullish, bearish, or neutral structure.
6. Measure liquidity and displacement.
7. Wait for objective confirmation.
8. Define a hypothetical entry and invalidation.
9. Define a target using a testable rule.
10. Evaluate the setup bar-by-bar in the backtester.
11. Record performance in R-multiples.

## Supporting Concepts

These are supporting measurements, not replacements for the original time model:

- Liquidity highs and lows
- Fair Value Gaps (FVGs)
- Order blocks
- Breakers
- Premium / discount zones
- Displacement
- Market structure

## Current Implementation

### Strategy engine
- 45-minute observation-time logic in U.S. Eastern Time
- 09:45 anchor detection
- Consecutive 45-minute window aggregation
- Window OHLC, high/low range, candle count, and direction
- Basic bullish/bearish/neutral structure detection
- Liquidity high/low measurements
- Displacement measurement
- Objective entry qualification
- Risk-to-reward target calculation

### Backtesting engine
- Bar-by-bar hypothetical trade evaluation
- Win/loss/open/ambiguous outcomes
- R-multiple results
- Win rate and net-R reporting
- Conservative handling when stop and target occur in the same candle
- Historical CSV loader and session runner
- Session journal output

### TradingView indicator
- `tradingview/time_based_model.pine` marks the 09:45 ET anchor and anchor high/low.
- It is a visual research tool only and does not place trades.

### Risk layer
- Percentage-risk calculation
- Simulated position sizing
- No broker or real-money execution

## Project Structure

```text
Time-Based-Trading-Robot/
├── README.md
├── requirements.txt
├── config/
│   └── strategy.yaml
├── strategy/
│   ├── time_windows.py
│   ├── anchor.py
│   ├── market_structure.py
│   ├── liquidity.py
│   ├── displacement.py
│   ├── entries.py
│   └── targets.py
├── backtest/
│   ├── engine.py
│   ├── performance.py
│   ├── reports.py
│   ├── journal.py
│   ├── session.py
│   └── time_windows.py
├── data/
│   ├── loader.py
│   └── sample_45m_sessions.csv
├── risk/
│   └── risk_manager.py
├── tradingview/
│   └── time_based_model.pine
├── app/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── run_robot.py
└── tests/
    ├── test_strategy.py
    └── test_time_windows.py
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Run the historical research robot:

```bash
python run_robot.py path/to/your_data.csv
```

The CSV must contain:

```text
 timestamp,open,high,low,close,volume
```

## Development Roadmap

### Phase 1 — Research Engine
- [x] Create dedicated repository
- [x] Document the original model
- [x] Build 09:45 anchor detector
- [x] Build consecutive 45-minute measurement windows
- [x] Build market-structure rules
- [x] Build liquidity detector
- [x] Build displacement detector
- [x] Build entry and target logic
- [x] Build backtesting engine
- [x] Add historical market-data loader
- [x] Add session-by-session backtest runner
- [x] Add research command-line runner
- [x] Add automated tests

### Phase 2 — Validation
- [x] Create a controlled synthetic test dataset.
- [ ] Import a clean real historical OHLCV dataset for research.
- [ ] Test the rules across a large historical sample.
- [ ] Measure setup frequency, win rate, average R, drawdown, and losing streaks.
- [ ] Test whether each rule improves results or only adds complexity.
- [ ] Keep a versioned rule journal so historical results do not silently change the model.

### Phase 3 — Signal Engine
- [x] Add visible dashboard logic using demo data.
- [ ] Replace demo data with validated historical/research data.
- [ ] Add setup classification and confidence metrics.
- [ ] Produce clear trade journals and performance reports.

### Phase 4 — Paper Simulation
- [ ] Connect validated signals to a paper-simulation workflow.
- [ ] Monitor performance without real-money execution.

## Design Principle

The most important rule is to preserve the original idea instead of forcing a generic ICT or SMC strategy onto the system. ICT/SMC concepts are supporting measurements; the **45-minute time model remains the primary framework**.

We are not claiming to know a hidden market algorithm. We are building a measurable system that tests the user's hypothesis about how price behaves around these time windows.

## Status

**Current stage: Phase 2 preparation — time-window engine + backtesting foundation.**

**Next milestone: connect the new 45-minute window observations to liquidity, displacement, and structure measurements, then validate the complete rule set on clean historical data.**
