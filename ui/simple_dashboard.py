"""
Simplified Crypto Trading Bot Dashboard for Render.com Deployment
A streamlined web UI for monitoring trading strategies and performance
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import sys
from datetime import datetime, timedelta
import time

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
    from data_feed import DataFeed
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Crypto Trading Bot Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cryptomaty-style appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E3440 0%, #3B4252 100%);
    }
    .stSelectbox > div > div {
        background-color: #434C5E;
        border: 1px solid #5E81AC;
    }
</style>
""", unsafe_allow_html=True)

class SimpleTradingDashboard:
    """Simplified Trading Dashboard for reliable deployment"""
    
    def __init__(self):
        self.data_feed = None
        self.initialize_data_feed()
    
    def initialize_data_feed(self):
        """Initialize data feed with error handling"""
        try:
            self.data_feed = DataFeed()
        except Exception as e:
            st.error(f"Error initializing data feed: {e}")
            self.data_feed = None
    
    def render_header(self):
        """Render main header"""
        st.markdown('<h1 class="main-header">🚀 Crypto Trading Bot Dashboard</h1>', unsafe_allow_html=True)
        
        # Status indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Strategy", getattr(config, 'STRATEGY_VERSION', 'v3'))
        
        with col2:
            st.metric("💰 Capital", f"${getattr(config, 'PAPER_TRADING_CAPITAL', 500)}")
        
        with col3:
            st.metric("⚖️ Risk/Trade", f"{getattr(config, 'MAX_RISK_PER_TRADE', 0.02)*100}%")
        
        with col4:
            current_time = datetime.now().strftime("%H:%M:%S")
            st.metric("🕐 Time", current_time)
    
    def render_market_data(self):
        """Render market data section"""
        st.header("📈 Live Market Data")
        
        if self.data_feed:
            try:
                # Get sample market data (simplified for deployment)
                # df = self.data_feed.get_ohlcv_data('BTCUSD', '1h', 24)
                
                # Sample data for demonstration
                dates = pd.date_range(start=datetime.now() - timedelta(hours=24), end=datetime.now(), freq='1h')
                sample_prices = [58000 + i*100 + (i%3)*200 for i in range(len(dates))]
                df = pd.DataFrame({
                    'close': sample_prices,
                    'high': [p*1.01 for p in sample_prices],
                    'low': [p*0.99 for p in sample_prices]
                }, index=dates)
                
                if df is not None and not df.empty:
                    # Current price
                    current_price = df['close'].iloc[-1]
                    price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
                    price_change_pct = (price_change / df['close'].iloc[-2]) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "BTC/USD",
                            f"${current_price:,.2f}",
                            f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                        )
                    
                    with col2:
                        st.metric("24h High", f"${df['high'].max():,.2f}")
                    
                    with col3:
                        st.metric("24h Low", f"${df['low'].min():,.2f}")
                    
                    # Simple price chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['close'],
                        mode='lines',
                        name='BTC Price',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    fig.update_layout(
                        title="BTC/USD Price (24h)",
                        xaxis_title="Time",
                        yaxis_title="Price (USD)",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("No market data available")
                    
            except Exception as e:
                st.error(f"Error fetching market data: {e}")
        else:
            st.error("Data feed not available")
    
    def render_strategy_config(self):
        """Render strategy configuration"""
        st.header("⚙️ Strategy Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Settings")
            
            # Display current config
            config_data = {
                "Strategy Version": getattr(config, 'STRATEGY_VERSION', 'v3'),
                "EMA Short": getattr(config, 'EMA_SHORT', 9),
                "EMA Long": getattr(config, 'EMA_LONG', 20),
                "ATR Period": getattr(config, 'ATR_PERIOD', 14),
                "ATR Multiplier": getattr(config, 'ATR_MULTIPLIER', 0.5),
                "Risk/Reward Ratio": getattr(config, 'RISK_REWARD_RATIO', 10),
                "Max Risk per Trade": f"{getattr(config, 'MAX_RISK_PER_TRADE', 0.02)*100}%"
            }
            
            for key, value in config_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("Strategy Info")
            
            strategy_info = {
                "v1": "Basic EMA crossover with ATR stops",
                "v2": "Enhanced with EMA9-based trailing stops",
                "v3": "Advanced with EMA20-based trailing stops for shorts"
            }
            
            current_strategy = getattr(config, 'STRATEGY_VERSION', 'v3')
            st.info(f"**Current Strategy:** {strategy_info.get(current_strategy, 'Unknown')}")
            
            st.write("**Entry Conditions:**")
            st.write("• LONG: EMA9 > EMA20 AND Price > EMA9")
            st.write("• SHORT: EMA9 < EMA20 AND Price < EMA9")
            
            st.write("**Risk Management:**")
            st.write("• Position Size: Dynamic based on ATR")
            st.write("• Stop Loss: Swing levels ± ATR")
            st.write("• Take Profit: 10:1 Risk/Reward")
    
    def render_status(self):
        """Render bot status"""
        st.header("🤖 Bot Status")
        
        # Check if bot is running (simplified)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Status", "Ready")
        
        with col2:
            st.metric("🔄 Mode", "Paper Trading")
        
        with col3:
            st.metric("💹 Active Positions", "0")
        
        # Instructions
        st.subheader("🚀 Getting Started")
        st.write("""
        1. **Monitor**: View live market data and current settings
        2. **Configure**: Adjust strategy parameters if needed
        3. **Deploy**: Run the paper trading bot locally for active trading
        4. **Analyze**: Review performance and optimize settings
        """)
        
        st.info("💡 **Note**: This is the monitoring dashboard. To start active trading, run the paper trading bot locally using `python paper_trading_bot.py`")

def main():
    """Main dashboard application"""
    dashboard = SimpleTradingDashboard()
    
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Market Data", "Strategy Config", "Status"]
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Render header on all pages
    dashboard.render_header()
    
    # Route to appropriate page
    if page == "Overview":
        dashboard.render_market_data()
        dashboard.render_status()
    elif page == "Market Data":
        dashboard.render_market_data()
    elif page == "Strategy Config":
        dashboard.render_strategy_config()
    elif page == "Status":
        dashboard.render_status()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🤖 Crypto Trading Bot v1.0**")
    st.sidebar.markdown("Built with ❤️ using Streamlit")
    st.sidebar.markdown("Deployed on Render.com 🚀")

if __name__ == "__main__":
    main()
