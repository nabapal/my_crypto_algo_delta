# Crypto Trading Bot with EMA/ATR Strategy

🚀 A comprehensive crypto trading bot with Streamlit dashboard, paper trading, and multiple strategy versions.

## 🌟 Features

- **📊 Real-time Dashboard**: Streamlit-based UI with live monitoring
- **📈 EMA/ATR Strategy**: Three strategy versions (v1, v2, v3) with different trailing stop logic
- **💰 Paper Trading**: Risk-free testing with detailed session tracking
- **🔍 Comprehensive Logging**: Session IDs, trade tracking, and UTC timestamps
- **⚙️ Configuration Management**: Easy strategy switching and parameter tuning
- **📱 Responsive UI**: Professional Cryptomaty-inspired interface

## 🚀 Deployment on Fly.io

### Prerequisites
1. **Add Payment Method**: Go to [Fly.io Billing](https://fly.io/dashboard/nabapal-pal-gmail-com/billing) and add a credit card
2. **Fly CLI**: Already installed ✅

### Quick Deploy
```bash
# Deploy to Fly.io
flyctl deploy

# Monitor your app
flyctl logs
flyctl status
```

### Manual Setup
```bash
# Launch app (if not done automatically)
flyctl launch --no-deploy

# Set environment variables (optional)
flyctl secrets set API_KEY=your_api_key
flyctl secrets set API_SECRET=your_api_secret

# Deploy
flyctl deploy

# Open your app
flyctl open
```

## 🏃‍♂️ Local Development

### Setup
```bash
# Clone repository
git clone https://github.com/nabapal/my_crypto_algo_delta.git
cd my_crypto_algo_delta

# Install dependencies
pip install -r requirements.txt

# Run dashboard
python launch_dashboard.py

# Run paper trading bot
python paper_trading_bot.py
```

### Strategy Configuration
Edit `config.py` to switch between strategy versions:
```python
STRATEGY_VERSION = "v2"  # Options: "v1", "v2", "v3"
```

## 📁 Project Structure

```
my_crypto_algo_delta/
├── 📊 ui/                          # Streamlit dashboard
├── 🧠 strategies/                  # Trading strategies
├── 📈 backtests/                   # Backtesting scripts
├── 📚 doc/                         # Documentation
├── 🔧 config.py                    # Configuration
├── 🤖 paper_trading_bot.py         # Main trading bot
├── 🚀 launch_dashboard.py          # Dashboard launcher
└── 🐳 Dockerfile                   # Container configuration
```

## 🔧 Configuration

### Strategy Versions
- **v1**: Basic EMA crossover with ATR stops
- **v2**: Enhanced with EMA9-based trailing stops
- **v3**: Advanced with EMA20-based trailing stops for shorts

### Risk Management
- **Risk per Trade**: 2% of portfolio
- **Risk-Reward Ratio**: 1:10
- **Position Sizing**: Dynamic based on ATR

## 📊 Dashboard Features

- **Real-time Monitoring**: Live position tracking
- **Strategy Control**: Start/stop trading
- **Configuration**: Live parameter adjustment
- **Performance Metrics**: P&L, win rate, trade history
- **Technical Indicators**: EMA, ATR, swing levels

## 🔐 Security

- API keys stored as secrets
- Logs and reports excluded from git
- Production-ready configuration management

## 📈 Strategy Logic

### LONG Signals
- EMA9 > EMA20 (bullish trend)
- Price > EMA9 (momentum confirmation)
- Stop Loss: Swing Low - (ATR × 0.5)

### SHORT Signals  
- EMA9 < EMA20 (bearish trend)
- Price < EMA9 (momentum confirmation)
- Stop Loss: Swing High + (ATR × 0.5)

## 🚀 Live Deployment URL

Once deployed on Fly.io, your app will be available at:
`https://my-crypto-algo-delta.fly.dev`

## 📞 Support

For issues or questions:
- Check the logs: `flyctl logs`
- Monitor status: `flyctl status`
- Review documentation in `/doc`

---

**⚠️ Disclaimer**: This is for educational purposes. Always test thoroughly before live trading.
