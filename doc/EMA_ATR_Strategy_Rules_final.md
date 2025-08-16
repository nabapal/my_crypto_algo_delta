# EMA + ATR Strategy FINAL (Based on v2)

## Core Logic
- Uses EMA and ATR for trade signals and stop-loss.
- Entry: Long if EMA9 > EMA20, Short if EMA9 < EMA20.
- Trailing stop: 
    - For short: min(SL, EMA9)
    - For long: max(SL, EMA20)

## Parameters
- EMA9, EMA20 (exponential moving averages)
- ATR (Average True Range, or stddev proxy)

## Trade Entry
- Long: If EMA9 > EMA20
- Short: If EMA9 < EMA20

## Trade Management
- Trailing stop for long: max(SL, EMA20)
- Trailing stop for short: min(SL, EMA9)

## Benefits
- Simple, robust trend-following logic
- No additional filters or indicators
- Proven best performance in backtests

## Notes
- This is the finalized version, selected after robust comparison of all strategy variants.
- For details on performance, see the comparison summary CSV and analysis script.
