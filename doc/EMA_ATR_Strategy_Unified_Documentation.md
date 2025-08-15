# EMA + ATR Strategy Unified Documentation (v1, v2, v3)

## Overview
This document describes the rules and logic for all three versions of the EMA + ATR strategy, as implemented in the unified trading and backtesting system. Each version uses a different trailing stop logic, controlled by the `STRATEGY_VERSION` parameter in `config.py`.

---

## Common Entry Rules

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

---

## Common Exit Rules
- Stop Loss (SL) is hit: exit at SL
- Take Profit (TP) is hit: exit at TP
- Trailing SL (if enabled): see version-specific logic below

---

## Trailing Stop Logic by Version

### v1
- **Long:** SL is trailed up to max(SL, EMA20)
- **Short:** SL is trailed down to min(SL, EMA20)

### v2
- **Long:** SL is trailed up to max(SL, EMA20)
- **Short:** SL is trailed down to min(SL, EMA9)

### v3
- **Long:** SL is trailed up to max(SL, EMA9)
- **Short:** SL is trailed down to min(SL, EMA20)

---

## Additional Notes
- Indicators: EMA9, EMA20, ATR
- Swing points: recent swing high/low used for SL
- Risk per trade: 2% of current capital
- All parameters (periods, multipliers, etc.) are configurable in `config.py`
- Backtest tracks portfolio value, P&L, drawdown, and trade statistics
- Strategy version is selected via `STRATEGY_VERSION` in `config.py` and applies to both backtest and live trading

---

## Backtest Performance Summary (as of August 15, 2025)

| Version | Total Trades | Win Rate | Total P&L | Final Capital | Total Return | Max Drawdown |
|---------|--------------|----------|-----------|---------------|--------------|--------------|
| v1      | 1090         | 27.06%   | $458.09   | $958.09       | +91.62%      | 57.69%       |
| v2      | 1346         | 27.79%   | $706.24   | $1,206.24     | +141.25%     | 66.10%       |
| v3      | 1417         | 28.09%   | $238.08   | $738.08       | +47.62%      | 46.20%       |

> For detailed trade logs and further analysis, see the backtest output CSV files in `data/ema_atr_strategy/`.

---

## Version Control
- To switch strategy logic, set `STRATEGY_VERSION = "v1"`, `"v2"`, or `"v3"` in `config.py`.
- The unified codebase ensures all logic is maintained in a single place for easier updates and testing.

---

_Last updated: August 15, 2025_
