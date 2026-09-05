# Time-Based Trading Robot

A research and backtesting project that converts Kabelo Gopane's original 45-minute time-based trading model into objective, testable rules.

> **Important:** This project is for research, backtesting, and paper-trading education. It does not guarantee profitable trading and does not place real-money trades.

## Core Model

**Time decides WHEN to analyze. Price decides WHAT to do. Liquidity decides WHERE to target.**

The model studies market behavior around repeated 45-minute time windows, with the New York session anchor at **09:45 South Africa Standard Time (SAST)**.

### Primary time windows

| Time (SAST) | Role |
|---|---|
| 08:45 | Pre-New York Open observation |
| 09:45 | Primary New York Open anchor |
| 10:45 | Post-open reaction |
| 11:45 | Follow-through / structure check |
| 12:45 | Midday session observation |
| 13:45 | Early afternoon observation |
| 15:45 | Pre-close observation |

## Strategy Logic

The robot must **not** assume that 09:45 automatically means BUY or SELL.

1. Detect the time anchor.
2. Build the relevant 45-minute range.
3. Record the anchor high and low.
4. Observe price delivery after the anchor.
5. Determine bullish, bearish, or neutral conditions.
6. Check liquidity and market structure.
7. Wait for objective confirmation.
8. Define a hypothetical entry, invalidation, and target.
9. Record the result for backtesting.

## Supporting Concepts

The project can use these as supporting tools rather than replacing the original time-based model:

- Liquidity highs and lows
- Fair Value Gaps (FVGs)
- Order blocks
- Breakers
- Premium / discount zones
- Displacement
- Market structure

## Project Roadmap

### Phase 1 — Research Engine
- [x] Create dedicated GitHub repository
- [x] Document the original model
- [ ] Build time-window engine
- [ ] Build 09:45 anchor detector
- [ ] Build market-structure rules
- [ ] Build liquidity detector
- [ ] Build entry and target logic
- [ ] Build backtesting engine
- [ ] Add automated tests

### Phase 2 — Signal Engine
- Convert validated rules into repeatable signals.
- Add setup classification and confidence metrics.
- Produce clear trade journals and performance reports.

### Phase 3 — Paper Trading
- Connect signals to a paper-trading workflow.
- Monitor performance without real-money execution.

## Project Structure

```text
Time-based-Trading-Robot/
├── README.md
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
├── tests/
│   └── test_strategy.py
└── requirements.txt
```

## Design Principle

The most important rule is to preserve the user's original idea instead of forcing a generic ICT or SMC strategy onto the system. ICT/SMC concepts are supporting measurements; the **45-minute time model remains the primary framework**.

## Status

**Current stage: Phase 1 — Foundation**

The next implementation milestone is the **09:45 anchor + 45-minute backtesting engine**.
