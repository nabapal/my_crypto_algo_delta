# EMA + ATR Strategy Rules

## Entry Rules

### Long Entry
- EMA9 crosses above EMA20 (EMA9 > EMA20)
- Close price is above EMA9
- ATR is not NaN
- Calculate stop loss (SL) as: recent swing low - ATR_MULTIPLIER * ATR
- Calculate risk: entry price - SL
- Take profit (TP): entry price + (risk * RISK_REWARD_RATIO)
- Position size: 2% of capital / risk (if risk > 0)

### Short Entry
- EMA9 crosses below EMA20 (EMA9 < EMA20)
- Close price is below EMA9
- ATR is not NaN
- Calculate stop loss (SL) as: recent swing high + ATR_MULTIPLIER * ATR
- Calculate risk: SL - entry price
- Take profit (TP): entry price - (risk * RISK_REWARD_RATIO)
- Position size: 2% of capital / risk (if risk > 0)

## Exit Rules
- Stop Loss (SL) is hit: exit at SL
- Take Profit (TP) is hit: exit at TP
- Trailing SL (if enabled):
    - For long: SL is trailed up to max(SL, EMA20)
    - For short: SL is trailed down to min(SL, EMA20)

## Additional Notes
- Indicators: EMA9, EMA20, ATR
- Swing points: recent swing high/low used for SL
- Risk per trade: 2% of current capital
- All parameters (periods, multipliers, etc.) are configurable in config.py
- Backtest tracks portfolio value, P&L, drawdown, and trade statistics
