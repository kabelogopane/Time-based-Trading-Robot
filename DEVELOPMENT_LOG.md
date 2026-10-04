# Trading Robot Development Log

This file records the development history of the trading-robot project. The purpose is to show the actual progression of the research, backtesting, strategy development and application work over time.

The log will be updated whenever meaningful work is completed. Results are recorded honestly, including unsuccessful tests and limitations.

---

## 23 September 2026 — Project Progress Review

### Work Completed

Today I reviewed the current state of my two trading-robot repositories:

- **Time-based-Trading-Robot**
- **Trading-Robot-App-2.0**

The purpose of the review was to understand how far the overall project has progressed and how the research project and application project fit together.

### Project Structure

#### 1. Time-based-Trading-Robot

This repository contains the research and strategy-development work.

The strategy is based on:

- 09:45 anchor
- 45-minute time windows
- Price delivery
- Liquidity
- Confirmation
- Backtesting
- Regime analysis
- Historical and paper simulation

The project has developed through testing and refinement rather than being built around a predetermined performance target.

#### 2. Trading-Robot-App-2.0

This repository represents the application side of the project.

The goal is to turn the trading research and results into a more user-friendly application interface where the strategy, analysis and future testing can be presented clearly.

### Current Research Status

Previous backtesting produced:

- **40 trading sessions**
- **13 wins**
- **25 losses**
- **2 open trades**

These results are treated as research findings rather than proof that the strategy is profitable.

A key principle of the project is to avoid changing the rules simply to produce a desired win rate. Improvements should be based on identifiable weaknesses in the existing strategy and then tested against historical data.

### Main Progress Today

Today's work was primarily a **project-status and development review**.

I confirmed that the project has evolved beyond the initial idea of a simple trading robot. It now consists of:

**Strategy → Rules → Historical Data → Backtesting → Diagnostics → Regime Analysis → Application**

This gives the project a clearer development structure and makes it easier to document future improvements.

### Next Development Focus

1. Continue improving the backtesting engine.
2. Test strategy changes against historical data.
3. Continue regime analysis.
4. Document every meaningful strategy change.
5. Connect research results to the application interface.
6. Improve the application's usability and presentation.
7. Add clearer performance and diagnostic views.
8. Continue testing without artificially targeting a specific win rate.
9. Maintain a daily development history.

### Project Philosophy

The objective is not simply to build a robot that produces attractive results.

The objective is to build a **transparent, testable and reproducible trading-research system** where every important change can be traced back to a specific development decision and its effect can be measured.

---

**Development status:** Active

**Last documented work:** 23 September 2026

**Related application repository:** Trading-Robot-App-2.0


---

## 4 October 2026 — September 2026 Data and Strategy Funnel Review

### Work Completed

Today I continued the historical research using the uploaded `SPX500_1m(1).csv` one-minute dataset.

The purpose was to understand why the current 09:45 time-based model produced very few September setups before changing any strategy rules.

### Data Review

- 180,320 one-minute OHLCV rows were available.
- Data coverage: 26 March 2026 to 25 September 2026.
- 19 September sessions contained a valid 09:45 anchor.
- The September sample passed the basic OHLC validation checks.

### Five Research Steps Completed

#### 1. September session audit

The September sample was separated from the wider dataset and checked using the existing 09:45 anchor and 3-minute execution structure.

#### 2. Confirmation funnel analysis

The current 45-minute execution window was examined stage by stage:

- 39 liquidity-sweep observations.
- 39 sweep paths reached matching structure checks.
- 13 reached displacement.
- 9 matching FVG formations were identified.
- 3 FVG retest candidates were found.
- The current first-signal-per-session pipeline produced 2 confirmed session signals.

The confirmed signals were on 11 September and 17 September. Both remained open within the defined 45-minute evaluation window.

Therefore September produced 0 closed wins and 0 closed losses under the current rules.

#### 3. Bottleneck identification

The strongest restriction appears late in the confirmation chain, especially the FVG retest requirement.

This does not prove that the FVG rule is wrong. It shows that the combined confirmation chain is highly restrictive on this sample.

No extra filter was added.

#### 4. Execution-window sensitivity test

Exploratory windows were checked without changing the entry logic:

| Window | Signals | Closed Wins | Closed Losses | Net R |
|---|---:|---:|---:|---:|
| 45 minutes | 2 | 0 | 0 | 0 |
| 60 minutes | 4 | 0 | 1 | -1 |
| 75 minutes | 6 | 1 | 1 | +1 |
| 90 minutes | 9 | 2 | 2 | +2 |

These results are too small to justify selecting a new window.

#### 5. Displacement sensitivity test

The 45-minute window was checked with displacement thresholds of 0.50, 0.60, 0.70 and 0.80.

All four produced the same two first confirmed September signals. Therefore the September lack of signals is not mainly caused by the 0.70 displacement threshold.

### Research Decision

The core strategy was **not changed** today.

The next investigation should inspect the rejected September setups and determine whether they are:

1. valid non-setups under the existing rules,
2. missed opportunities caused by a rigid rule definition, or
3. cases where a rule is measuring the wrong thing.

The project will continue to avoid adding filters simply to increase the reported win rate.

### Documentation

A detailed review was added to:

`research/september_funnel_review_2026-10-04.md`

### Development Principle

Today's main finding is that **more filtering is not automatically better**. Before adding another rule, the existing confirmation chain needs to be understood and tested against the actual rejected sessions.

**Development status:** Active
**Research mode:** Historical / paper simulation only
