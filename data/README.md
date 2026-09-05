# Historical Market Data

Place historical OHLCV CSV files here for research only.

Expected columns:

```text
timestamp,open,high,low,close,volume
```

The timestamps should be timezone-aware where possible. The strategy converts timestamps to `Africa/Johannesburg` when evaluating the model's SAST observation times.

Do not commit broker credentials, API keys, account information, or private trading records to this repository.

Recommended validation before backtesting:

- Confirm timestamps are ordered.
- Confirm there are no duplicate candles.
- Confirm OHLC values are valid.
- Confirm the instrument and timeframe are known.
- Record the data source and date range used for every experiment.
