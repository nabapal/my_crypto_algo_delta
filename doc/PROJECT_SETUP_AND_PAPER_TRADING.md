# Crypto Trading Bot Project Documentation

## Project Overview
This project is a modular crypto trading bot designed for paper trading on historical and live data. It supports multiple strategy versions, robust backtesting, and can be extended for live trading. The initial focus is on paper trading using historical data and Delta Exchange API for real-time data.

---

## Requirements

### 1. Software & Tools
- Python 3.8+
- Git (for version control)
- VS Code or any Python IDE
- Delta Exchange API credentials (for live data)

### 2. Python Packages
- pandas
- numpy
- matplotlib
- requests (for API calls)
- scipy

Install all dependencies with:
```
pip install -r requirements.txt
```

---

## Project Structure
- `strategies/`: Contains all strategy logic (unified and archived versions)
- `backtests/`: Scripts for running backtests
- `data/`: Historical and generated trade data
- `doc/`: Documentation
- `config.py`: All configuration parameters
- `compare_strategy_performance_fresh.py`: Script to compare strategy results

---

## Step-by-Step Setup

### 1. Clone the Repository
```
git clone <your-repo-url>
cd <project-folder>
```

### 2. Set Up Python Environment
```
python -m venv .venv
.venv\Scripts\activate  # On Windows
```

### 3. Install Requirements
```
pip install -r requirements.txt
```

### 4. Configure Parameters
- Edit `config.py` to set capital, risk, strategy version, and data paths.
- Set your Delta Exchange API credentials if using live data.

### 5. Run Backtests
```
python backtests/backtest_ema_atr_strategy_unified.py
```

### 6. Compare Strategies
```
python compare_strategy_performance_fresh.py
```

### 7. (Optional) Fetch Data from Delta Exchange
- Use the Delta Exchange API to fetch historical or live data.
- Integrate API calls in your data pipeline (see below).

---

## Delta Exchange API Integration
- Register for an account and generate API keys on Delta Exchange.
- Use the `requests` library to fetch data:

```python
import requests
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
url = 'https://api.delta.exchange/v2/...'  # See Delta Exchange API docs
headers = {'api-key': API_KEY}
response = requests.get(url, headers=headers)
data = response.json()
```
- Parse and save the data to `data/raw_data/` for use in backtests.

---

## Next Steps
- Extend the bot for live paper trading using Delta Exchange WebSocket or REST API.
- Add order management and position tracking modules.
- Implement logging and error handling.
- (Optional) Prepare for real trading by adding authentication and risk controls.

---

## References
- Delta Exchange API Docs: https://docs.delta.exchange/
- Python requests: https://docs.python-requests.org/
- pandas: https://pandas.pydata.org/

---

For further customization or automation, update the strategy logic and data pipeline as needed.
