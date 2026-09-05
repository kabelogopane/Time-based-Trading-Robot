# Robot Web App

This folder contains the browser research terminal for the 45-minute time-based model.

## Current status

The chart is a TradingView display and the monitor is a browser demonstration. The browser does **not** receive live market candles and does **not** send broker orders.

The authoritative research engine is the Python backtest pipeline in the repository. Historical OHLCV data must be validated before it is used for research conclusions.

## Intended production architecture

Browser UI → validated data service → Python strategy engine → research results API → browser dashboard.

The data service and API are intentionally not connected yet. This prevents the UI from presenting hard-coded demo values as live signals.
