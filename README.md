# Time-Based Trading Robot

A research and backtesting project that converts Kabelo Gopane's original 45-minute time-based trading model into objective, testable rules.

> **Important:** This project is for research, backtesting, and paper-trading education. It does not guarantee profitable trading and does not place real-money trades.

## Core Model

**Time decides WHEN to analyze. Price decides WHAT to do. Liquidity decides WHERE to target.**

The model studies market behavior around repeated 45-minute time windows, with the New York session anchor at **09:45 South Africa time**.

### Primary time windows

| Time | Role |
|---|---|
| 08:45 | Pre-New York Open observation |
| 09:45 | Primary New York Open anchor |
| 10:45 | Post-open reaction |
| 11:45 | Follow-through / structure check |
| 12:45 | Midday observation |
| 13:45 | Early afternoon observation |
| 15:45 | Pre-close observation |

## Strategy Logic

The robot does **not** assume that 09:45 automatically means BUY or SELL.

1. Detect the time anchor.
2. Record the anchor high and low.
3. Observe price delivery after the anchor.
4. Classify bullish, bearish, or neutral structure.
5. Measure liquidity and displacement.
6. Wait for objective confirmation.
7. Define a hypothetical entry and invalidation.
8. Define a target using a testable rule.
9. Evaluate the setup bar-by-bar in the backtester.
10. Record performance in R-multiples.

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
- 45-minute observation-time logic
- 09:45 anchor detection
- Anchor range classification
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
│   └── reports.py
├── risk/
│   └── risk_manager.py
└── tests/
    └── test_strategy.py
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

## Development Roadmap

### Phase 1 — Research Engine
- [x] Create dedicated repository
- [x] Document the original model
- [x] Build time-window engine
- [x] Build 09:45 anchor detector
- [x] Build market-structure rules
- [x] Build liquidity detector
- [x] Build displacement detector
- [x] Build entry and target logic
- [x] Build first backtesting engine
- [x] Add automated tests
- [ ] Add historical market-data loader
- [ ] Add session-by-session backtest runner
- [ ] Add CSV trade journal output

### Phase 2 — Validation
- Test the rules across a large historical sample.
- Measure setup frequency, win rate, average R, drawdown, and losing streaks.
- Test whether each rule improves results or only adds complexity.
- Avoid changing rules after seeing individual historical outcomes without recording the change first.

### Phase 3 — Signal Engine
- Convert validated rules into repeatable signals.
- Add setup classification and confidence metrics.
- Produce clear trade journals and performance reports.

### Phase 4 — Paper Trading
- Connect signals to a paper-trading workflow.
- Monitor performance without real-money execution.

## Design Principle

The most important rule is to preserve the original idea instead of forcing a generic ICT or SMC strategy onto the system. ICT/SMC concepts are supporting measurements; the **45-minute time model remains the primary framework**.

We are not claiming to know a hidden market algorithm. We are building a measurable system that tests the user's hypothesis about how price behaves around these time windows.

## Status

**Current stage: Phase 1 — Foundation + first executable backtesting components.**

**Next milestone: Historical data loader + full session backtest runner.**
