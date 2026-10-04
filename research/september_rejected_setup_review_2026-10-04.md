# September 2026 Rejected-Setup Review

Date: 4 October 2026

## Purpose

This review continues the September research without changing the core strategy.

The current repository pipeline was re-audited against the uploaded `SPX500_1m(1).csv` dataset. The goal was to identify where rejected setups fail and whether the rejection is caused mainly by missing confirmation, timing, or the 45-minute window.

This is historical/paper research only. No live orders are involved.

## Step 1 — Re-run the current pipeline exactly

The September sample contains 19 valid 09:45 sessions.

Using the current repository definitions:

- 3-minute execution candles
- 15 execution candles after the 09:45 anchor
- 5-candle liquidity-sweep lookback
- structure and displacement confirmation
- FVG formation
- FVG midpoint retest
- first fully confirmed signal per session

The detailed sweep audit found 39 liquidity-sweep observations.

The exact current pipeline reproduced **1 first fully confirmed September signal**, on:

- 11 September 2026 — long

That signal remained open inside the 45-minute evaluation window.

The earlier research note reported 2 confirmed September signals. That count could not be reproduced against the current repository code and current dataset, so this review treats the exact current pipeline result of **1** as the authoritative research result.

## Step 2 — Classify every rejected sweep

The 39 sweep observations were classified by the first point where the current confirmation chain failed.

| Failure stage | Sweep paths |
|---|---:|
| Structure/displacement not fully confirmed on the required candle | 30 |
| Structure + displacement reached, but no matching FVG | 3 |
| FVG formed, but no retest inside 45 minutes | 5 |
| Fully confirmed | 1 |
| **Total** | **39** |

The largest group is therefore rejected before the FVG stage.

This means the September problem is not simply that the FVG retest rule is too strict. Most sweep paths never become a complete structure + displacement confirmation under the current definitions.

## Step 3 — Test whether same-candle confirmation is the main problem

The current pipeline requires the same post-sweep candle to satisfy:

1. expected market structure, and
2. displacement.

As a diagnostic only, the rejected 30 paths were checked to see whether structure and directional displacement appeared later on separate candles.

Results:

- 18 had neither a later matching structure nor later directional displacement.
- 6 had structure but no later directional displacement.
- 3 had directional displacement but no matching structure.
- 3 had both somewhere later, but not in the required sequence.
- Only **1 of the 30** could satisfy a relaxed structure-then-displacement sequence.

That one case still did not reach a complete FVG/retest setup.

Research conclusion: the same-candle requirement is **not the main explanation** for the low September signal count.

No rule was changed.

## Step 4 — Check whether the 45-minute window is rejecting otherwise developing FVG setups

Five paths reached a matching FVG but did not retest it during the 45-minute window.

The same FVG zones were then observed beyond the normal window as a diagnostic only.

Findings:

- 9 September: the FVG was first retested immediately after the 45-minute window.
- 17 September: the FVG was first retested about 15 minutes after the 45-minute window.
- 10 September: the FVG still did not retest within the extended 90-minute observation.

This is evidence that the 45-minute window can reject setups that continue developing after the official window.

However, this is **not enough evidence to change the 45-minute model**. It only identifies a timing sensitivity that should be tested on a larger sample.

## Step 5 — Research decision

The evidence now separates the problem into two parts:

### Main rejection source

Most September sweep paths fail before FVG because the required structure/displacement confirmation does not complete.

### Secondary timing issue

Some setups reach an FVG but retest after the 45-minute window.

### What we are NOT doing

- No new filter.
- No new entry rule.
- No change from 09:45.
- No change from 45 minutes.
- No change to the displacement threshold.
- No live trading logic.
- No attempt to force an 80% win rate.

### Next research direction

The next useful test is to expand this rejected-setup classification across the full available dataset rather than changing the strategy from September alone.

The purpose will be to answer:

> Are the September rejection patterns normal behaviour of the model, or are they unusual to this month?

Only after that larger-sample test should any rule be considered for modification.

## Reproducibility

Dataset:

- `SPX500_1m(1).csv`
- 180,320 one-minute rows
- 26 March 2026 to 25 September 2026
- 19 valid September 09:45 sessions

Repository logic reviewed:

- `strategy/liquidity.py`
- `strategy/market_structure.py`
- `strategy/displacement.py`
- `strategy/fvg.py`
- `strategy/pipeline.py`
- `backtest/session.py`

No strategy source files were changed during this review.
