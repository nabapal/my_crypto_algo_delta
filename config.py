# Delta Exchange Live Trading Configuration

# API Credentials
API_KEY = "KnYntWNAW018WFO0ykvoUZLpl5XLpy"
API_SECRET = "Iw38M8Bma1LA4Lw73iAB32yX5tv4Nxb1cJm4h2tmVwpNMy4P2CcmSV40eaov"

# API Endpoints
BASE_URL = "https://api.india.delta.exchange"
WEBSOCKET_URL = "wss://socket.india.delta.exchange"

# Trading Configuration
SYMBOL = "BTCUSD"
PRODUCT_ID = 27  # BTCUSD Perpetual Futures


# Strategy Parameters (from successful backtest)
EMA_SHORT = 9
EMA_LONG = 20
ATR_PERIOD = 14
ATR_MULTIPLIER = 0.5
RISK_REWARD_RATIO = 10

# Backtest Data File
BACKTEST_DATA_FILE = "data/raw_data/btc_1h_historical_20250813_230350.csv"

# Strategy version selector for backtest script
STRATEGY_VERSION = "v2"  # Options: "v1", "v2", "v3"

# Trailing Stop Loss setting for strategy
TRAILING_SL = True

# Position Sizing
INITIAL_CAPITAL = 100  # USD - Default/Live trading capital
PAPER_TRADING_CAPITAL = 500  # USD - Paper trading starting capital
LIVE_TRADING_CAPITAL = 100   # USD - Live trading starting capital (smaller for safety)
MAX_RISK_PER_TRADE = 0.02  # 2% per trade

