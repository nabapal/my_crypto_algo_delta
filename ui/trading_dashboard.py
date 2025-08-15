"""
Crypto Trading Bot Dashboard - Cryptomaty Style Interface
A comprehensive web UI for managing trading strategies, monitoring performance, and configuring settings
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
import sys
from datetime import datetime, timedelta
import time
import subprocess
import threading
import queue
from streamlit_autorefresh import st_autorefresh

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data_feed import DataFeed
from paper_trading_bot import PaperTradingBot

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
    .strategy-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-live {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .profit-positive {
        color: #28a745;
        font-weight: bold;
    }
    .profit-negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self):
        self.data_feed = DataFeed()
        self.bot_process = None
        self.bot_queue = queue.Queue()
        
    def load_strategy_performance(self):
        """Load latest performance data"""
        try:
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                return None
            
            # Get latest performance file
            files = [f for f in os.listdir(reports_dir) if f.startswith('performance_detail_')]
            if not files:
                return None
            
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
            
            with open(os.path.join(reports_dir, latest_file), 'r') as f:
                return json.load(f)
        except:
            return None
    
    def load_trades_data(self):
        """Load latest trades CSV"""
        try:
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                return pd.DataFrame()
            
            # Get latest trades file
            files = [f for f in os.listdir(reports_dir) if f.startswith('trades_') and f.endswith('.csv')]
            if not files:
                return pd.DataFrame()
            
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
            
            return pd.read_csv(os.path.join(reports_dir, latest_file))
        except:
            return pd.DataFrame()
    
    def get_bot_status(self):
        """Check if trading bot is running"""
        try:
            # Check if there are recent log entries
            log_file = "logs/trading_activity_20250815.log"
            if os.path.exists(log_file):
                mod_time = os.path.getmtime(log_file)
                last_modified = datetime.fromtimestamp(mod_time)
                if datetime.now() - last_modified < timedelta(minutes=5):
                    return "Live", "🟢"
            return "Stopped", "🔴"
        except:
            return "Unknown", "⚪"
    
    def render_header(self):
        """Render main header"""
        st.markdown('<h1 class="main-header">🚀 Crypto Trading Bot Dashboard</h1>', unsafe_allow_html=True)
        
        # Status bar
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            status, icon = self.get_bot_status()
            st.metric("Bot Status", f"{icon} {status}")
        
        with col2:
            try:
                # Get current price
                live_price = self.data_feed.fetch_live_price()
                st.metric("BTC Price", f"${live_price:,.2f}")
            except:
                st.metric("BTC Price", "Loading...")
        
        with col3:
            perf = self.load_strategy_performance()
            if perf:
                st.metric("Portfolio", f"${perf.get('portfolio_balance', 0):.2f}")
            else:
                st.metric("Portfolio", f"${config.PAPER_TRADING_CAPITAL}")
        
        with col4:
            if perf:
                total_pnl = perf.get('total_pnl', 0)
                pnl_class = "profit-positive" if total_pnl >= 0 else "profit-negative"
                st.markdown(f'<div class="{pnl_class}">Total P&L: ${total_pnl:.2f}</div>', unsafe_allow_html=True)
            else:
                st.metric("Total P&L", "$0.00")
        
        with col5:
            if perf:
                win_rate = perf.get('win_rate_percent', 0)
                st.metric("Win Rate", f"{win_rate:.1f}%")
            else:
                st.metric("Win Rate", "0.0%")

    def render_strategy_management(self):
        """Render strategy management section"""
        st.header("📊 Strategy Management")
        
        # Strategy cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="strategy-card">
                <h3>🎯 EMA + ATR Strategy</h3>
                <p><strong>Version:</strong> v3</p>
                <p><strong>Status:</strong> <span class="status-live">●</span> Active</p>
                <p><strong>Parameters:</strong> EMA(9,20) + ATR(14)</p>
                <p><strong>Risk/Reward:</strong> 1:10</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔧 Configure Strategy", key="config_strategy"):
                st.session_state.show_config = True
        
        with col2:
            perf = self.load_strategy_performance()
            if perf:
                pnl = perf.get('total_pnl', 0)
                trades = perf.get('total_trades', 0)
                win_rate = perf.get('win_rate_percent', 0)
                pnl_color = "#28a745" if pnl >= 0 else "#dc3545"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Performance</h3>
                    <p><strong>Total P&L:</strong> <span style="color: {pnl_color}">${pnl:.2f}</span></p>
                    <p><strong>Total Trades:</strong> {trades}</p>
                    <p><strong>Win Rate:</strong> {win_rate:.1f}%</p>
                    <p><strong>Last Updated:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)

    def render_live_trading(self):
        """Render live trading section"""
        st.header("⚡ Live Trading")
        
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Start Trading", key="start_trading"):
                self.start_trading_bot()
        
        with col2:
            if st.button("⏹️ Stop Trading", key="stop_trading"):
                self.stop_trading_bot()
        
        with col3:
            if st.button("📊 View Logs", key="view_logs"):
                st.session_state.show_logs = True
        
        with col4:
            if st.button("📄 Download Reports", key="download_reports"):
                st.session_state.show_reports = True
        
        # Current position
        perf = self.load_strategy_performance()
        if perf and perf.get('current_position'):
            pos = perf['current_position']
            st.subheader("🎯 Current Position")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Type", pos.get('signal_data', {}).get('position_type', 'N/A').upper())
            with col2:
                st.metric("Entry Price", f"${pos.get('entry_price', 0):.2f}")
            with col3:
                st.metric("Stop Loss", f"${pos.get('stop_loss', 0):.2f}")
            with col4:
                st.metric("Take Profit", f"${pos.get('take_profit', 0):.2f}")

    def render_configuration(self):
        """Render configuration panel"""
        if not st.session_state.get('show_config', False):
            return
        
        st.header("⚙️ Strategy Configuration")
        
        # Load current config
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Strategy Parameters")
            ema_short = st.number_input("EMA Short Period", value=config.EMA_SHORT, min_value=1, max_value=100)
            ema_long = st.number_input("EMA Long Period", value=config.EMA_LONG, min_value=1, max_value=200)
            atr_period = st.number_input("ATR Period", value=config.ATR_PERIOD, min_value=1, max_value=50)
            atr_multiplier = st.number_input("ATR Multiplier", value=config.ATR_MULTIPLIER, min_value=0.1, max_value=5.0, step=0.1)
            risk_reward = st.number_input("Risk/Reward Ratio", value=config.RISK_REWARD_RATIO, min_value=1, max_value=20)
        
        with col2:
            st.subheader("💰 Risk Management")
            paper_capital = st.number_input("Paper Trading Capital", value=config.PAPER_TRADING_CAPITAL, min_value=100, max_value=10000)
            live_capital = st.number_input("Live Trading Capital", value=config.LIVE_TRADING_CAPITAL, min_value=50, max_value=5000)
            max_risk = st.number_input("Max Risk Per Trade (%)", value=config.MAX_RISK_PER_TRADE*100, min_value=0.5, max_value=10.0, step=0.5)
            
            trading_symbol = st.selectbox("Trading Symbol", ["BTCUSD", "ETHUSD", "ADAUSD"], index=0)
            strategy_version = st.selectbox("Strategy Version", ["v1", "v2", "v3"], index=2)
        
        if st.button("💾 Save Configuration", key="save_config"):
            self.save_configuration({
                'EMA_SHORT': ema_short,
                'EMA_LONG': ema_long,
                'ATR_PERIOD': atr_period,
                'ATR_MULTIPLIER': atr_multiplier,
                'RISK_REWARD_RATIO': risk_reward,
                'PAPER_TRADING_CAPITAL': paper_capital,
                'LIVE_TRADING_CAPITAL': live_capital,
                'MAX_RISK_PER_TRADE': max_risk / 100,
                'SYMBOL': trading_symbol,
                'STRATEGY_VERSION': strategy_version
            })
            st.success("✅ Configuration saved successfully!")
            time.sleep(2)
            st.rerun()

    def render_charts(self):
        """Render trading charts"""
        st.header("📊 Trading Charts")
        
        try:
            # Get market data
            df = self.data_feed.fetch_historical_candles(limit=100)
            if df is not None and not df.empty:
                
                # Calculate indicators for chart
                from strategies.ema_atr_strategy_unified import calculate_indicators
                df_with_indicators = calculate_indicators(df.copy())
                
                # Create candlestick chart
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    subplot_titles=('Price & EMAs', 'ATR'),
                    row_width=[0.7, 0.3]
                )
                
                # Candlestick
                fig.add_trace(
                    go.Candlestick(
                        x=df['Timestamp'],
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name="Price"
                    ),
                    row=1, col=1
                )
                
                # EMAs
                if 'EMA9' in df_with_indicators.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_with_indicators['Timestamp'],
                            y=df_with_indicators['EMA9'],
                            mode='lines',
                            name='EMA 9',
                            line=dict(color='orange', width=2)
                        ),
                        row=1, col=1
                    )
                
                if 'EMA20' in df_with_indicators.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_with_indicators['Timestamp'],
                            y=df_with_indicators['EMA20'],
                            mode='lines',
                            name='EMA 20',
                            line=dict(color='blue', width=2)
                        ),
                        row=1, col=1
                    )
                
                # ATR
                if 'ATR' in df_with_indicators.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_with_indicators['Timestamp'],
                            y=df_with_indicators['ATR'],
                            mode='lines',
                            name='ATR',
                            line=dict(color='purple', width=2)
                        ),
                        row=2, col=1
                    )
                
                fig.update_layout(
                    title="BTC/USD Trading Chart",
                    xaxis_rangeslider_visible=False,
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading chart data: {str(e)}")

    def render_trades_table(self):
        """Render trades table"""
        st.header("📋 Trade History")
        
        df_trades = self.load_trades_data()
        if not df_trades.empty:
            # Format the dataframe for display
            display_df = df_trades.copy()
            
            # Format datetime
            if 'Timestamp' in display_df.columns:
                display_df['Timestamp'] = pd.to_datetime(display_df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Format numeric columns
            numeric_cols = ['Entry_Price', 'Stop_Loss', 'Take_Profit', 'Risk_Amount', 'Expected_Reward', 'PnL']
            for col in numeric_cols:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
            
            # Color code P&L
            def highlight_pnl(val):
                if pd.isna(val) or val == "":
                    return ""
                pnl_val = float(val.replace('$', ''))
                color = 'color: green' if pnl_val >= 0 else 'color: red'
                return color
            
            if 'PnL' in display_df.columns:
                styled_df = display_df.style.applymap(highlight_pnl, subset=['PnL'])
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No trades data available yet. Start trading to see results!")

    def start_trading_bot(self):
        """Start the trading bot"""
        try:
            # Kill any existing process
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, shell=True)
            
            # Start new process
            self.bot_process = subprocess.Popen(
                ['python', 'paper_trading_bot.py'],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            st.success("✅ Trading bot started successfully!")
        except Exception as e:
            st.error(f"❌ Error starting bot: {str(e)}")

    def stop_trading_bot(self):
        """Stop the trading bot"""
        try:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, shell=True)
            st.success("✅ Trading bot stopped successfully!")
        except Exception as e:
            st.error(f"❌ Error stopping bot: {str(e)}")

    def save_configuration(self, new_config):
        """Save new configuration to config.py"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')
            
            # Read current config
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Update configuration values
            with open(config_path, 'w') as f:
                for line in lines:
                    line_written = False
                    for key, value in new_config.items():
                        if line.startswith(f"{key} ="):
                            if isinstance(value, str):
                                f.write(f'{key} = "{value}"\n')
                            else:
                                f.write(f'{key} = {value}\n')
                            line_written = True
                            break
                    if not line_written:
                        f.write(line)
                        
            # Reload config module
            import importlib
            importlib.reload(config)
            
        except Exception as e:
            st.error(f"Error saving configuration: {str(e)}")

def main():
    """Main dashboard application"""
    dashboard = TradingDashboard()
    
    # Auto-refresh every 30 seconds
    st_autorefresh(interval=30000, key="dashboard_refresh")
    
    # Initialize session state
    if 'show_config' not in st.session_state:
        st.session_state.show_config = False
    
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Trading", "Configuration", "Charts", "Trade History"]
    )
    
    # Render header on all pages
    dashboard.render_header()
    
    # Route to appropriate page
    if page == "Dashboard":
        dashboard.render_strategy_management()
        dashboard.render_live_trading()
    elif page == "Trading":
        dashboard.render_live_trading()
    elif page == "Configuration":
        dashboard.render_configuration()
    elif page == "Charts":
        dashboard.render_charts()
    elif page == "Trade History":
        dashboard.render_trades_table()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🤖 Crypto Trading Bot v1.0**")
    st.sidebar.markdown("Built with ❤️ using Streamlit")

if __name__ == "__main__":
    main()
