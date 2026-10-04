# September 2026 Research Funnel Review

Date: 4 October 2026

## Purpose

This review uses the uploaded `SPX500_1m(1).csv` dataset to diagnose why the current 09:45 time-based research model produced very few September setups.

This is historical/paper research only. No live orders are involved.

## 1. Data and session audit

The uploaded file contains:

- 180,320 one-minute OHLCV rows.
- Coverage from 26 March 2026 through 25 September 2026.
- 19 September 2026 sessions containing a valid 09:45 anchor.
- September anchor data was available for 1–4, 7–11, 14–18 and 21–25 September.

The September data passed the basic OHLC validation used by the project.

## 2. Current 45-minute funnel

The current execution window is 15 three-minute candles after the 09:45 anchor.

Across the 19 September sessions:

| Stage | Count |
|---|---:|
| Liquidity-sweep observations | 39 |
| Sweep paths reaching matching structure | 39 |
| Paths reaching displacement | 13 |
| Matching FVG formations | 9 |
| FVG retest candidates | 3 |
| First confirmed session signals | 2 |

The two first confirmed session signals occurred on:

- 11 September — long
- 17 September — long

Both remained open inside the defined 45-minute evaluation window. Therefore September produced **0 closed wins and 0 closed losses** under the current rules.

## 3. Main bottleneck

The strongest bottleneck is the final FVG-retouch requirement.

The earlier stages are producing observations, but most potential paths do not reach a qualifying FVG retest before the 45-minute window ends.

This does **not** prove that the FVG rule is wrong. It shows that the current combination of:

liquidity sweep → structure → displacement → FVG → FVG retest

is highly restrictive on this September sample.

No additional filter should be added at this point.

## 4. Window sensitivity test

An exploratory test checked longer execution windows without changing the entry rules.

| 3-minute candles | Time window | Signals | Closed wins | Closed losses | Net R |
|---:|---:|---:|---:|---:|---:|
| 15 | 45 min | 2 | 0 | 0 | 0 |
| 20 | 60 min | 4 | 0 | 1 | -1 |
| 25 | 75 min | 6 | 1 | 1 | +1 |
| 30 | 90 min | 9 | 2 | 2 | +2 |

These results are exploratory only. The sample is too small to select a new window from these numbers.

The important observation is that extending the window creates more opportunities, but it does not automatically create a high-quality strategy.

## 5. Displacement sensitivity

The displacement threshold was checked at 0.50, 0.60, 0.70 and 0.80 for the original 45-minute window.

All four thresholds produced the same two first confirmed September signals.

Therefore the September lack of signals is **not mainly caused by the 0.70 displacement threshold**.

## Research decision

Do not change the core strategy yet.

The next research task should be to inspect the rejected September setups and separate:

1. genuine missed opportunities,
2. setups that fail the model's rules for a valid reason,
3. cases where the current rule definitions are too rigid.

The goal remains to improve trade quality based on evidence, not to force the win rate toward a target.

## Reproducibility note

The analysis was performed against the uploaded one-minute dataset and the repository's current 09:45 / 3-minute execution / liquidity / structure / displacement / FVG pipeline.

No September paper-trade journal results were mixed into the OHLC backtest because the journal records are not equivalent to one-minute OHLC data.
