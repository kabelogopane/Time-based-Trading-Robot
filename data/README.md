# Historical Market Data

Place historical OHLCV CSV files here for research only.

## Required schema

```text
timestamp,open,high,low,close,volume
```

The current research model is configured for **1-minute candles**. One model window is 45 candles, so 45 candles represent 45 minutes only when the source timeframe is 1 minute.

## Timezone

The project uses **U.S. Eastern Time / `America/New_York`** for the model's observation times. The preferred source format is a timezone-aware ISO-8601 timestamp, such as:

```text
2026-07-07T18:59:00+00:00
```

Source timestamps may be in UTC. The research pipeline should convert them to `America/New_York` before evaluating the 08:45, 09:45, 10:45, and later checkpoints.

## Current research dataset target

The first real-data validation target is the **SPX500 1-minute index dataset** from the public GetData Finance GitHub sample:

- Instrument: SPX500 / S&P 500 index feed
- Timeframe: 1 minute
- Schema: `datetime, open, high, low, close, volume`
- Source timestamps: UTC
- Sample coverage currently documented by the source: 2026-02-01 through 2026-07-31
- The source describes the feed as global cash and extended index sessions, not US-hours only.

The dataset is a research input, not proof of exchange-grade execution prices. The exact source/feed must remain documented in experiment results.

## Validation requirements

Before a dataset is used in backtesting, check:

- Confirm the required columns exist.
- Confirm timestamps are parseable and timezone-aware or explicitly localized.
- Confirm timestamps are ordered.
- Confirm there are no duplicate candles.
- Confirm the expected 1-minute interval.
- Check for missing candles within each research session rather than treating normal overnight/session boundaries as errors.
- Confirm OHLC relationships are valid.
- Confirm the instrument and timeframe are known.
- Record the data source, feed type, timezone, and date range used for every experiment.

## Research safety

This repository is for historical research and paper-simulation education. It does not connect to a broker or place real-money trades.

Do not commit broker credentials, API keys, account information, or private trading records to this repository.
