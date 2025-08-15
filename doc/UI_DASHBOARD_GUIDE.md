# 🚀 Crypto Trading Bot Dashboard

## Overview
A comprehensive web-based dashboard for managing your crypto trading bot, inspired by professional trading platforms like Cryptomaty. This dashboard provides real-time monitoring, strategy configuration, and performance analysis.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-green) ![Version](https://img.shields.io/badge/Version-1.0-blue)

## 🌟 Features

### 📊 **Dashboard Overview**
- **Real-time Status**: Live bot status monitoring
- **Portfolio Metrics**: Current balance, P&L, win rate
- **Performance Cards**: Strategy performance summaries
- **Auto-refresh**: Automatic updates every 30 seconds

### ⚡ **Live Trading Control**
- **Start/Stop Bot**: One-click trading control
- **Position Monitoring**: Real-time position tracking
- **Risk Management**: Live risk metrics display
- **Emergency Controls**: Quick stop functionality

### ⚙️ **Advanced Configuration**
- **Strategy Parameters**: EMA, ATR, Risk-Reward settings
- **Risk Management**: Capital allocation and risk limits
- **API Configuration**: Exchange credentials management
- **Configuration Presets**: Conservative, Aggressive, Scalping modes

### 📈 **Interactive Charts**
- **Candlestick Charts**: Real-time price visualization
- **Technical Indicators**: EMA and ATR overlays
- **Multi-timeframe**: Various chart intervals
- **Trade Signals**: Visual signal markers

### 📋 **Trade Analysis**
- **Trade History**: Detailed trade log with P&L
- **Performance Metrics**: Win rate, average returns
- **Export Capabilities**: CSV and JSON downloads
- **Real-time Updates**: Live trade tracking

## 🚀 Quick Start

### 1. Launch Dashboard
```bash
# Method 1: Using batch file (Windows)
start_dashboard.bat

# Method 2: Using Python launcher
python launch_dashboard.py

# Method 3: Direct Streamlit command
.\.venv\Scripts\python.exe -m streamlit run ui\trading_dashboard.py --server.port 8501
```

### 2. Access Dashboard
Open your browser and navigate to: **http://localhost:8501**

### 3. Configure Settings
1. Go to **Configuration** tab
2. Set your API credentials
3. Adjust strategy parameters
4. Save configuration

### 4. Start Trading
1. Navigate to **Trading** tab
2. Click **▶️ Start Trading**
3. Monitor in **Dashboard** tab

## 📋 Dashboard Sections

### 🏠 **Dashboard Page**
- Strategy management cards
- Performance metrics
- Quick controls
- Status overview

### ⚡ **Trading Page**
- Bot control buttons
- Current position details
- Live monitoring
- Log access

### ⚙️ **Configuration Page**
- **API Settings**: Credentials and endpoints
- **Strategy Parameters**: EMA, ATR, Risk-Reward
- **Risk Management**: Capital and position sizing
- **Advanced Settings**: Presets and backup/restore

### 📊 **Charts Page**
- Real-time candlestick charts
- Technical indicator overlays
- Interactive price analysis
- Signal visualization

### 📋 **Trade History Page**
- Detailed trade log
- P&L analysis
- Performance statistics
- Export functionality

## ⚙️ Configuration Options

### 🔑 **API Settings**
```python
API_KEY = "your_delta_exchange_api_key"
API_SECRET = "your_delta_exchange_api_secret"
BASE_URL = "https://api.india.delta.exchange"
SYMBOL = "BTCUSD"  # Trading pair
```

### 📊 **Strategy Parameters**
```python
EMA_SHORT = 9          # Fast EMA period
EMA_LONG = 20          # Slow EMA period
ATR_PERIOD = 14        # ATR calculation period
ATR_MULTIPLIER = 0.5   # Stop loss multiplier
RISK_REWARD_RATIO = 10 # Risk to reward ratio
TRAILING_SL = True     # Enable trailing stops
```

### 💰 **Risk Management**
```python
PAPER_TRADING_CAPITAL = 500    # Paper trading capital
LIVE_TRADING_CAPITAL = 100     # Live trading capital
MAX_RISK_PER_TRADE = 0.02      # 2% risk per trade
```

## 🎯 **Configuration Presets**

### Conservative Mode
- Higher EMA periods (12/26)
- Larger ATR multiplier (1.0)
- Lower risk (1% per trade)
- Higher risk-reward (15:1)

### Aggressive Mode
- Lower EMA periods (5/15)
- Smaller ATR multiplier (0.3)
- Higher risk (5% per trade)
- Lower risk-reward (5:1)

### Scalping Mode
- Very low EMA periods (3/8)
- Minimal ATR multiplier (0.2)
- Medium risk (3% per trade)
- Quick risk-reward (3:1)

## 🔄 **Real-time Features**

### Auto-refresh Dashboard
- Portfolio balance updates
- Position monitoring
- Performance metrics
- Market data refresh

### Live Trading Signals
- Entry signal detection
- Exit condition monitoring
- Stop loss adjustments
- Take profit tracking

### Status Monitoring
- Bot health checks
- API connectivity
- Data feed status
- Error detection

## 📁 **File Structure**
```
crypto_trading_bot/
├── ui/
│   ├── trading_dashboard.py    # Main dashboard
│   ├── config_manager.py       # Configuration editor
│   └── requirements_ui.txt     # UI dependencies
├── launch_dashboard.py         # Dashboard launcher
├── start_dashboard.bat         # Windows batch file
├── config.py                   # Configuration file
├── paper_trading_bot.py        # Trading bot engine
├── data_feed.py               # Market data handler
└── strategies/                # Trading strategies
```

## 🛠️ **Dependencies**
```
streamlit>=1.28.0
streamlit-autorefresh>=0.0.1
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
streamlit-aggrid>=0.3.4
streamlit-option-menu>=0.3.6
```

## 🔒 **Security Features**
- Password-masked API credentials
- Configuration backups
- Input validation
- Error handling

## 📊 **Performance Monitoring**
- Real-time P&L tracking
- Win rate calculations
- Trade statistics
- Portfolio performance

## 🎨 **UI Features**
- **Responsive Design**: Works on desktop and tablet
- **Dark/Light Themes**: Automatic theme support
- **Interactive Charts**: Plotly-powered visualizations
- **Real-time Updates**: Live data refresh
- **Professional Layout**: Cryptomaty-inspired design

## 🚨 **Error Handling**
- Graceful API failures
- Configuration validation
- Data integrity checks
- User-friendly error messages

## 📈 **Advanced Features**
- Export trade data to CSV/JSON
- Configuration import/export
- Multiple strategy presets
- Backup and restore functionality

## 🔧 **Troubleshooting**

### Dashboard Won't Start
```bash
# Check if streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install streamlit

# Use virtual environment
.\.venv\Scripts\python.exe -m pip install streamlit
```

### Can't Connect to Bot
- Ensure bot is running in background
- Check log files in `/logs` directory
- Verify API credentials in configuration

### Configuration Issues
- Use "Restore from Backup" if config corrupted
- Reset to defaults if needed
- Check validation errors before saving

## 🎯 **Next Steps**
1. **Launch the dashboard**: `start_dashboard.bat`
2. **Configure your settings**: Set API keys and strategy parameters
3. **Start paper trading**: Test with virtual capital
4. **Monitor performance**: Use real-time dashboard
5. **Optimize strategy**: Adjust parameters based on results

---

**🚀 Ready to start professional crypto trading with a beautiful dashboard interface!**
