# How to Start Paper Trading with the Crypto Trading Bot

This guide explains the exact steps to start paper trading using your crypto trading bot, including how to use Delta Exchange API for live data.

---

## 1. Prerequisites
- Complete the setup steps in `PROJECT_SETUP_AND_PAPER_TRADING.md` (clone repo, set up environment, install requirements).
- Make sure you have Delta Exchange API credentials (for live data).

---

## 2. Prepare for Paper Trading

### a. Configure Paper Trading Mode
- Open `config.py`.
- Set your initial capital, risk parameters, and select the strategy version you want to test (e.g., `STRATEGY_VERSION = "v2"`).
- Set the data source:
  - For historical backtest: set the path to your historical CSV in `config.py`.
  - For live paper trading: set up Delta Exchange API credentials in `config.py` or a `.env` file.

### b. (Optional) Fetch Live Data from Delta Exchange
- Use the provided API code sample to fetch live data and save it to `data/raw_data/`.
- You can automate this step with a script that runs at intervals.

---

## 3. Run the Paper Trading Bot

### a. For Historical Paper Trading (Backtest)
```
python backtests/backtest_ema_atr_strategy_unified.py
```
- This will simulate trades using historical data and print/save results.

### b. For Live Paper Trading (Simulated Orders)
- Integrate Delta Exchange API to fetch real-time prices.
- Use the strategy logic to generate buy/sell signals.
- Instead of sending real orders, log simulated trades to a CSV or database.
- Track portfolio value and P&L in real time.

---

## 4. Analyze Results
- Use the comparison script:
```
python compare_strategy_performance_fresh.py
```
- Review trade logs and performance metrics in the `data/ema_atr_strategy/` folder.

---

## 5. (Optional) Next Steps
- Add a scheduler to fetch live data and run the bot at regular intervals.
- Build a dashboard or reporting tool for real-time monitoring.
- When ready, adapt the bot for real trading by connecting order placement endpoints and adding risk controls.

---

## References
- Delta Exchange API Docs: https://docs.delta.exchange/
- Example API usage is in the main project doc.

---

If you need a ready-to-use script for live paper trading or more automation, let me know!
