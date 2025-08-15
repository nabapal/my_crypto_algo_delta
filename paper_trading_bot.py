"""
Paper Trading Bot for EMA+ATR Strategy
Real-time trading simulation with comprehensive logging and reporting
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
import time
import csv
from datetime import datetime, timedelta, timezone
import json
from typing import Dict, List, Optional
import pytz
import uuid
import hashlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_feed import DataFeed
from strategies.ema_atr_strategy_unified import calculate_indicators, get_recent_swing_low, get_recent_swing_high
from config import *

# Timezone settings
UTC = pytz.UTC
LOCAL_TZ = pytz.timezone('Asia/Kolkata')  # Adjust to your timezone

class SessionManager:
    """Manages unique session IDs for bot runs"""
    def __init__(self):
        self.session_id = self.generate_session_id()
        self.start_time = datetime.now(UTC)
        
    def generate_session_id(self):
        """Generate unique session ID based on timestamp and strategy"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        strategy_hash = hashlib.md5(f"{EMA_SHORT}_{EMA_LONG}_{ATR_PERIOD}_{ATR_MULTIPLIER}".encode()).hexdigest()[:6]
        return f"SID_{timestamp}_{strategy_hash}"
    
    def get_log_suffix(self):
        """Get log file suffix with session ID"""
        date_str = self.start_time.strftime("%Y%m%d")
        return f"{date_str}_{self.session_id}"

class Position:
    """Represents a trading position with comprehensive tracking"""
    def __init__(self, entry_price, quantity, stop_loss, take_profit, entry_time, strategy_version, signal_data, trade_id=None):
        self.trade_id = trade_id or self.generate_trade_id()
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = entry_time
        self.strategy_version = strategy_version
        self.signal_data = signal_data
        self.trailing_sl = stop_loss
        self.position_type = signal_data.get('position_type', 'long')  # 'long' or 'short'
        self.highest_price = entry_price  # For long trailing stop
        self.lowest_price = entry_price   # For short trailing stop
        
        # Store swing levels for display
        self.swing_low = signal_data.get('swing_low')
        self.swing_high = signal_data.get('swing_high')
        
        # Trade lifecycle tracking
        self.is_closed = False
        self.exit_price = None
        self.exit_time = None
        self.exit_reason = None
        self.realized_pnl = 0.0
        
    def generate_trade_id(self):
        """Generate unique trade ID"""
        timestamp = datetime.now(UTC).strftime("%H%M%S")
        random_part = uuid.uuid4().hex[:4]
        return f"T_{timestamp}_{random_part}"
    
    def get_entry_log_data(self):
        """Get comprehensive entry log data"""
        return {
            'trade_id': self.trade_id,
            'action': 'ENTRY',
            'timestamp_utc': self.entry_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'signal_type': self.signal_data['signal_type'],
            'position_type': self.position_type.upper(),
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_amount': self.signal_data.get('risk_amount', 0),
            'expected_reward': self.signal_data.get('expected_reward', 0),
            'ema9': self.signal_data.get('ema9', 0),
            'ema20': self.signal_data.get('ema20', 0),
            'atr': self.signal_data.get('atr', 0),
            'swing_low': self.signal_data.get('swing_low', 0),
            'swing_high': self.signal_data.get('swing_high', 0),
            'strategy_version': self.strategy_version,
            'atr_multiplier': ATR_MULTIPLIER,
            'risk_reward_ratio': RISK_REWARD_RATIO
        }
    
    def close_position(self, exit_price, exit_reason):
        """Close the position and calculate final P&L"""
        self.exit_price = exit_price
        self.exit_time = datetime.now(UTC)
        self.exit_reason = exit_reason
        self.is_closed = True
        
        # Calculate realized P&L
        if self.position_type == 'long':
            self.realized_pnl = (exit_price - self.entry_price) * self.quantity
        else:  # short position
            self.realized_pnl = (self.entry_price - exit_price) * self.quantity
    
    def get_exit_log_data(self):
        """Get comprehensive exit log data"""
        if not self.is_closed or not self.exit_time:
            return None
            
        time_in_position = self.exit_time - self.entry_time
        return {
            'trade_id': self.trade_id,
            'action': 'EXIT',
            'timestamp_utc': self.exit_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'exit_price': self.exit_price,
            'exit_reason': self.exit_reason,
            'realized_pnl': self.realized_pnl,
            'pnl_percentage': (self.realized_pnl / (self.entry_price * self.quantity)) * 100,
            'time_in_position_minutes': int(time_in_position.total_seconds() / 60),
            'trailing_sl_final': self.trailing_sl
        }
        
    def calculate_unrealized_pnl(self, current_price):
        """Calculate unrealized P&L based on current price"""
        if self.position_type == 'long':
            unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:  # short position
            unrealized_pnl = (self.entry_price - current_price) * self.quantity
        return unrealized_pnl
    
    def calculate_pnl_percentage(self, current_price):
        """Calculate P&L percentage based on entry price"""
        if self.position_type == 'long':
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:  # short position
            return ((self.entry_price - current_price) / self.entry_price) * 100
    
    def calculate_sl_percentage(self, current_price):
        """Calculate distance to stop loss as percentage"""
        if self.position_type == 'long':
            return ((current_price - self.trailing_sl) / current_price) * 100
        else:  # short position
            return ((self.trailing_sl - current_price) / current_price) * 100
    
    def get_position_status(self, current_price, ema9, ema20, atr):
        """Get comprehensive position status"""
        unrealized_pnl = self.calculate_unrealized_pnl(current_price)
        pnl_percentage = self.calculate_pnl_percentage(current_price)
        sl_percentage = self.calculate_sl_percentage(current_price)
        
        return {
            'entry_price': self.entry_price,
            'current_price': current_price,
            'quantity': self.quantity,
            'position_type': self.position_type.upper(),
            'unrealized_pnl': unrealized_pnl,
            'pnl_percentage': pnl_percentage,
            'stop_loss': self.stop_loss,
            'trailing_sl': self.trailing_sl,
            'sl_percentage': sl_percentage,
            'take_profit': self.take_profit,
            'entry_time': self.entry_time,
            'ema9': ema9,
            'ema20': ema20,
            'atr': atr
        }

    def update_trailing_stop(self, current_price, atr_value, ema9, ema20):
        """Update trailing stop loss based on strategy version and EMA values"""
        if TRAILING_SL:
            if self.position_type == 'long':
                # For long positions, trail stop up with price
                if current_price > self.highest_price:
                    self.highest_price = current_price
                
                # Strategy v3: Use EMA9 for LONG trailing
                if STRATEGY_VERSION == "v1" or STRATEGY_VERSION == "v2":
                    new_trailing_sl = max(self.trailing_sl, ema20)
                elif STRATEGY_VERSION == "v3":
                    new_trailing_sl = max(self.trailing_sl, ema9)
                else:
                    new_trailing_sl = self.trailing_sl
                
                if new_trailing_sl > self.trailing_sl:
                    old_sl = self.trailing_sl
                    self.trailing_sl = new_trailing_sl
                    print(f"🔄 TRAILING SL UPDATED (LONG): ${old_sl:.2f} → ${new_trailing_sl:.2f} (EMA{9 if STRATEGY_VERSION == 'v3' else 20})")
                else:
                    print(f"🔒 TRAILING SL UNCHANGED (LONG): ${self.trailing_sl:.2f} (EMA{9 if STRATEGY_VERSION == 'v3' else 20}: ${ema9 if STRATEGY_VERSION == 'v3' else ema20:.2f})")
                        
            elif self.position_type == 'short':
                # For short positions, trail stop down with price
                if current_price < self.lowest_price:
                    self.lowest_price = current_price
                
                # Strategy v3: Use EMA20 for SHORT trailing
                if STRATEGY_VERSION == "v1" or STRATEGY_VERSION == "v3":
                    new_trailing_sl = min(self.trailing_sl, ema20)
                elif STRATEGY_VERSION == "v2":
                    new_trailing_sl = min(self.trailing_sl, ema9)
                else:
                    new_trailing_sl = self.trailing_sl
                
                if new_trailing_sl < self.trailing_sl:
                    old_sl = self.trailing_sl
                    self.trailing_sl = new_trailing_sl
                    print(f"🔄 TRAILING SL UPDATED (SHORT): ${old_sl:.2f} → ${new_trailing_sl:.2f} (EMA{20 if STRATEGY_VERSION == 'v3' else 9})")
                else:
                    print(f"🔒 TRAILING SL UNCHANGED (SHORT): ${self.trailing_sl:.2f} (EMA{20 if STRATEGY_VERSION == 'v3' else 9}: ${ema20 if STRATEGY_VERSION == 'v3' else ema9:.2f})")
    
    def to_dict(self):
        """Convert position to dictionary for logging"""
        return {
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'trailing_sl': self.trailing_sl,
            'entry_time': self.entry_time.isoformat(),
            'strategy_version': self.strategy_version,
            'signal_data': self.signal_data
        }

class LogManager:
    """Handles all logging operations with session tracking"""
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.log_dir = "logs"
        self.report_dir = "reports"
        
        # Create directories if they don't exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Set up loggers
        self.setup_loggers()
        
        # Log session start
        self.log_session_start()
    
    def log_session_start(self):
        """Log session start information"""
        session_info = {
            'session_id': self.session_manager.session_id,
            'start_time_utc': self.session_manager.start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'strategy_config': {
                'ema_short': EMA_SHORT,
                'ema_long': EMA_LONG,
                'atr_period': ATR_PERIOD,
                'atr_multiplier': ATR_MULTIPLIER,
                'risk_reward_ratio': RISK_REWARD_RATIO,
                'strategy_version': STRATEGY_VERSION,
                'paper_capital': PAPER_TRADING_CAPITAL,
                'max_risk_per_trade': MAX_RISK_PER_TRADE
            }
        }
        
        self.trading_logger.info(f"SESSION_START - {json.dumps(session_info, indent=2)}")
        
        # Save session info to file
        session_file = f"{self.report_dir}/session_{self.session_manager.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, default=str)
    
    def setup_loggers(self):
        """Set up different loggers for different purposes with UTC timestamps"""
        log_suffix = self.session_manager.get_log_suffix()
        
        # Custom formatter with UTC timestamp
        formatter = logging.Formatter('%(asctime)s UTC - %(levelname)s - %(message)s')
        formatter.converter = time.gmtime  # Use UTC time
        
        # API Communication Logger
        self.api_logger = logging.getLogger('API')
        api_handler = logging.FileHandler(f"{self.log_dir}/api_communication_{log_suffix}.log", encoding='utf-8')
        api_handler.setFormatter(formatter)
        self.api_logger.addHandler(api_handler)
        self.api_logger.setLevel(logging.INFO)
        
        # Trading Activity Logger
        self.trading_logger = logging.getLogger('Trading')
        trading_handler = logging.FileHandler(f"{self.log_dir}/trading_activity_{log_suffix}.log", encoding='utf-8')
        trading_handler.setFormatter(formatter)
        self.trading_logger.addHandler(trading_handler)
        self.trading_logger.setLevel(logging.INFO)
        
        # Market Data Logger
        self.market_logger = logging.getLogger('Market')
        market_handler = logging.FileHandler(f"{self.log_dir}/market_data_{log_suffix}.log", encoding='utf-8')
        market_handler.setFormatter(formatter)
        self.market_logger.addHandler(market_handler)
        self.market_logger.setLevel(logging.INFO)
        
        # Error Logger
        self.error_logger = logging.getLogger('Error')
        error_handler = logging.FileHandler(f"{self.log_dir}/errors_{log_suffix}.log", encoding='utf-8')
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)
        
        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s UTC - %(name)s - %(levelname)s - %(message)s')
        console_formatter.converter = time.gmtime  # Use UTC time
        console_handler.setFormatter(console_formatter)
        
        # Add console handler to all loggers
        for logger in [self.api_logger, self.trading_logger, self.market_logger, self.error_logger]:
            logger.addHandler(console_handler)

class RiskManager:
    """Handles risk management and position sizing"""
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_risk_per_trade = MAX_RISK_PER_TRADE
        self.daily_loss_limit = getattr(globals(), 'DAILY_LOSS_LIMIT', 0.10)
        self.emergency_stop_loss = getattr(globals(), 'EMERGENCY_STOP_LOSS', 0.05)
        self.max_positions = getattr(globals(), 'MAX_CONCURRENT_POSITIONS', 1)
        
    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calculate position size based on risk management rules"""
        try:
            risk_amount = self.current_capital * self.max_risk_per_trade
            price_risk = abs(entry_price - stop_loss_price)
            
            if price_risk <= 0:
                return 0
            
            position_size = risk_amount / price_risk
            return position_size
            
        except Exception as e:
            logging.getLogger('Error').error(f"Error calculating position size: {str(e)}")
            return 0
    
    def validate_trade(self, position_size, entry_price):
        """Validate if trade meets risk management criteria"""
        # For paper trading, we only need to check if we have enough risk capital
        # Not the full position value (since this simulates leveraged trading)
        risk_amount = self.current_capital * self.max_risk_per_trade
        
        # Check if we have enough capital for the risk amount
        if risk_amount > self.current_capital:
            return False, "Insufficient capital for risk amount"
        
        # Check portfolio-level risk
        portfolio_risk = (self.initial_capital - self.current_capital) / self.initial_capital
        if portfolio_risk >= self.emergency_stop_loss:
            return False, "Emergency stop-loss triggered"
        
        return True, "Trade validated"

class PaperTradingBot:
    """Main paper trading bot class with comprehensive tracking"""
    def __init__(self):
        self.session_manager = SessionManager()
        self.data_feed = DataFeed()
        self.log_manager = LogManager(self.session_manager)
        self.risk_manager = RiskManager(PAPER_TRADING_CAPITAL)
        
        # Trading state
        self.current_position = None
        self.portfolio_balance = PAPER_TRADING_CAPITAL
        self.trades_executed = []
        self.last_candle_time = None
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        # Set up CSV files for trade reporting
        self.setup_trade_reporting()
        
        print(f"\n{'='*80}")
        print(f"🚀 PAPER TRADING BOT - SESSION: {self.session_manager.session_id}")
        print(f"{'='*80}")
        print(f"💰 Capital: ${PAPER_TRADING_CAPITAL}")
        print(f"📊 Strategy: EMA({EMA_SHORT},{EMA_LONG}) + ATR({ATR_PERIOD}) - Version {STRATEGY_VERSION}")
        print(f"⚖️ Risk per trade: {MAX_RISK_PER_TRADE*100}% | Risk-Reward: {RISK_REWARD_RATIO}:1")
        print(f"🕐 Started: {self.session_manager.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"{'='*80}\n")
    
    def setup_trade_reporting(self):
        """Set up CSV files for trade reporting with session ID"""
        session_id = self.session_manager.session_id
        self.trades_file = f"{self.log_manager.report_dir}/trades_{session_id}.csv"
        self.performance_file = f"{self.log_manager.report_dir}/performance_{session_id}.csv"
        
        # Create enhanced trades CSV with headers
        with open(self.trades_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Trade_ID', 'Session_ID', 'Action', 'Timestamp_UTC', 'Signal_Type', 'Position_Type',
                'Entry_Price', 'Exit_Price', 'Quantity', 'Stop_Loss', 'Take_Profit', 'Trailing_SL_Final',
                'Risk_Amount', 'Expected_Reward', 'Realized_PnL', 'PnL_Percentage',
                'Time_in_Position_Minutes', 'Exit_Reason', 'Strategy_Version',
                'EMA9', 'EMA20', 'ATR', 'ATR_Multiplier', 'Swing_Low', 'Swing_High',
                'Risk_Reward_Ratio', 'Portfolio_Balance_Before', 'Portfolio_Balance_After'
            ])
    
    def log_trade_entry(self, position):
        """Log comprehensive trade entry to CSV"""
        entry_data = position.get_entry_log_data()
        
        with open(self.trades_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry_data['trade_id'],
                self.session_manager.session_id,
                entry_data['action'],
                entry_data['timestamp_utc'],
                entry_data['signal_type'],
                entry_data['position_type'],
                entry_data['entry_price'],
                '',  # Exit_Price - empty for entry
                entry_data['quantity'],
                entry_data['stop_loss'],
                entry_data['take_profit'],
                '',  # Trailing_SL_Final - empty for entry
                entry_data['risk_amount'],
                entry_data['expected_reward'],
                '',  # Realized_PnL - empty for entry
                '',  # PnL_Percentage - empty for entry
                '',  # Time_in_Position_Minutes - empty for entry
                '',  # Exit_Reason - empty for entry
                entry_data['strategy_version'],
                entry_data['ema9'],
                entry_data['ema20'],
                entry_data['atr'],
                entry_data['atr_multiplier'],
                entry_data['swing_low'],
                entry_data['swing_high'],
                entry_data['risk_reward_ratio'],
                self.portfolio_balance + entry_data['risk_amount'],  # Balance before trade
                self.portfolio_balance  # Balance after trade
            ])
    
    def log_trade_exit(self, position):
        """Log comprehensive trade exit to CSV"""
        exit_data = position.get_exit_log_data()
        if not exit_data:
            return
        
        with open(self.trades_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                exit_data['trade_id'],
                self.session_manager.session_id,
                exit_data['action'],
                exit_data['timestamp_utc'],
                '',  # Signal_Type - empty for exit
                position.position_type.upper(),
                position.entry_price,
                exit_data['exit_price'],
                position.quantity,
                position.stop_loss,
                position.take_profit,
                exit_data['trailing_sl_final'],
                '',  # Risk_Amount - empty for exit
                '',  # Expected_Reward - empty for exit
                exit_data['realized_pnl'],
                exit_data['pnl_percentage'],
                exit_data['time_in_position_minutes'],
                exit_data['exit_reason'],
                position.strategy_version,
                '',  # EMA9 - empty for exit (could add current values)
                '',  # EMA20 - empty for exit
                '',  # ATR - empty for exit
                ATR_MULTIPLIER,
                '',  # Swing_Low - empty for exit
                '',  # Swing_High - empty for exit
                RISK_REWARD_RATIO,
                self.portfolio_balance - exit_data['realized_pnl'],  # Balance before exit
                self.portfolio_balance  # Balance after exit
            ])
    
    def check_for_new_candle(self, df):
        """Check if there's a new 1H candle"""
        if df is None or df.empty:
            return False
        
        latest_candle_time = df.iloc[-1]['Timestamp']
        
        if self.last_candle_time is None:
            self.last_candle_time = latest_candle_time
            return True
        
        if latest_candle_time > self.last_candle_time:
            self.last_candle_time = latest_candle_time
            self.log_manager.market_logger.info(f"New candle detected: {latest_candle_time}")
            return True
        
        return False
    
    def analyze_market_data(self, df):
        """Analyze market data for strategy signals"""
        try:
            # Calculate indicators
            df_with_indicators = calculate_indicators(df.copy())
            
            if len(df_with_indicators) < max(ATR_PERIOD, EMA_LONG) + 10:
                self.log_manager.market_logger.warning("Insufficient data for analysis")
                return None, None
            
            # Get latest values
            current_idx = len(df_with_indicators) - 1
            current_data = df_with_indicators.iloc[current_idx]
            prev_data = df_with_indicators.iloc[current_idx - 1]
            
            # Log market data
            self.log_manager.market_logger.info(
                f"Market Data - Price: {current_data['Close']:.2f}, "
                f"EMA9: {current_data['EMA9']:.2f}, EMA20: {current_data['EMA20']:.2f}, "
                f"ATR: {current_data['ATR']:.2f}"
            )
            
            # Check for LONG signal (EMA9 > EMA20 AND Close > EMA9)
            long_signal = (
                current_data['EMA9'] > current_data['EMA20'] and 
                current_data['Close'] > current_data['EMA9'] and
                not pd.isna(current_data['ATR'])
            )
            
            # Check for SHORT signal (EMA9 < EMA20 AND Close < EMA9)  
            short_signal = (
                current_data['EMA9'] < current_data['EMA20'] and
                current_data['Close'] < current_data['EMA9'] and
                not pd.isna(current_data['ATR'])
            )
            
            # Print detailed signal analysis
            print(f"\n🔍 SIGNAL ANALYSIS (Strategy v{STRATEGY_VERSION}):")
            print(f"  📍 Current Price: ${current_data['Close']:,.2f}")
            print(f"  🔵 EMA9: ${current_data['EMA9']:,.2f}")
            print(f"  🔴 EMA20: ${current_data['EMA20']:,.2f}")
            print(f"  📊 ATR: ${current_data['ATR']:,.2f}")
            print(f"  📈 EMA9 > EMA20: {current_data['EMA9'] > current_data['EMA20']} ({current_data['EMA9']:,.2f} vs {current_data['EMA20']:,.2f})")
            print(f"  📍 Price vs EMA9: {'ABOVE' if current_data['Close'] > current_data['EMA9'] else 'BELOW'} ({current_data['Close']:,.2f} vs {current_data['EMA9']:,.2f})")
            print(f"  🎯 LONG Signal: {long_signal}")
            print(f"  🎯 SHORT Signal: {short_signal}")
            
            if long_signal:
                print(f"\n✅ LONG SIGNAL DETECTED!")
                print(f"  📋 Logic: EMA9 > EMA20 AND Price > EMA9")
                print(f"  🔵 EMA9 ({current_data['EMA9']:,.2f}) > EMA20 ({current_data['EMA20']:,.2f}) ✓")
                print(f"  📍 Price ({current_data['Close']:,.2f}) > EMA9 ({current_data['EMA9']:,.2f}) ✓")
                
                # LONG (BUY) signal logic
                swing_low = get_recent_swing_low(df_with_indicators, current_idx, lookback=10)
                
                print(f"\n📊 LONG POSITION CALCULATION:")
                print(f"  📉 Swing Low (10 periods): ${swing_low:,.2f}")
                print(f"  📊 ATR Value: ${current_data['ATR']:,.2f}")
                print(f"  ⚖️ ATR Multiplier: {ATR_MULTIPLIER}")
                
                # Calculate stop loss and take profit for LONG
                entry_price = current_data['Close']
                atr_stop = swing_low - (current_data['ATR'] * ATR_MULTIPLIER)
                stop_loss = atr_stop  # Use ATR-based stop from swing low
                
                print(f"  🛡️ Initial SL Calculation: ${swing_low:,.2f} - (${current_data['ATR']:,.2f} × {ATR_MULTIPLIER}) = ${stop_loss:,.2f}")
                
                # Calculate take profit based on risk-reward ratio
                price_risk = entry_price - stop_loss
                if price_risk > 0:  # Valid risk amount
                    take_profit = entry_price + (price_risk * RISK_REWARD_RATIO)
                    
                    # Calculate actual position size and dollar risk/reward
                    portfolio_risk_amount = self.portfolio_balance * MAX_RISK_PER_TRADE  # 2% of portfolio
                    position_size = portfolio_risk_amount / price_risk  # Position size in BTC
                    actual_dollar_risk = position_size * price_risk
                    actual_dollar_reward = position_size * (price_risk * RISK_REWARD_RATIO)
                    
                    signal_data = {
                        'signal_type': 'BUY',
                        'position_type': 'long',
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'ema9': current_data['EMA9'],
                        'ema20': current_data['EMA20'],
                        'atr': current_data['ATR'],
                        'swing_low': swing_low,
                        'swing_high': get_recent_swing_high(df_with_indicators, current_idx, lookback=10),
                        'price_risk': price_risk,
                        'position_size': position_size,
                        'risk_amount': actual_dollar_risk,
                        'expected_reward': actual_dollar_reward,
                        'timestamp': current_data['Timestamp']
                    }
                    
                    return 'BUY', signal_data
            
            elif short_signal:
                print(f"\n✅ SHORT SIGNAL DETECTED!")
                print(f"  📋 Logic: EMA9 < EMA20 AND Price < EMA9")
                print(f"  🔵 EMA9 ({current_data['EMA9']:,.2f}) < EMA20 ({current_data['EMA20']:,.2f}) ✓")
                print(f"  📍 Price ({current_data['Close']:,.2f}) < EMA9 ({current_data['EMA9']:,.2f}) ✓")
                
                # SHORT (SELL) signal logic
                swing_high = get_recent_swing_high(df_with_indicators, current_idx, lookback=10)
                
                print(f"\n📊 SHORT POSITION CALCULATION:")
                print(f"  📈 Swing High (10 periods): ${swing_high:,.2f}")
                print(f"  📊 ATR Value: ${current_data['ATR']:,.2f}")
                print(f"  ⚖️ ATR Multiplier: {ATR_MULTIPLIER}")
                
                # Calculate stop loss and take profit for SHORT
                entry_price = current_data['Close']
                atr_stop = swing_high + (current_data['ATR'] * ATR_MULTIPLIER)
                stop_loss = atr_stop  # Use ATR-based stop from swing high
                
                print(f"  🛡️ Initial SL Calculation: ${swing_high:,.2f} + (${current_data['ATR']:,.2f} × {ATR_MULTIPLIER}) = ${stop_loss:,.2f}")
                
                # Calculate take profit based on risk-reward ratio
                price_risk = stop_loss - entry_price
                if price_risk > 0:  # Valid risk amount
                    take_profit = entry_price - (price_risk * RISK_REWARD_RATIO)
                    
                    # Calculate actual position size and dollar risk/reward
                    portfolio_risk_amount = self.portfolio_balance * MAX_RISK_PER_TRADE  # 2% of portfolio
                    position_size = portfolio_risk_amount / price_risk  # Position size in BTC
                    actual_dollar_risk = position_size * price_risk
                    actual_dollar_reward = position_size * (price_risk * RISK_REWARD_RATIO)
                    
                    signal_data = {
                        'signal_type': 'SELL',
                        'position_type': 'short',
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'ema9': current_data['EMA9'],
                        'ema20': current_data['EMA20'],
                        'atr': current_data['ATR'],
                        'swing_low': get_recent_swing_low(df_with_indicators, current_idx, lookback=10),
                        'swing_high': swing_high,
                        'price_risk': price_risk,
                        'position_size': position_size,
                        'risk_amount': actual_dollar_risk,
                        'expected_reward': actual_dollar_reward,
                        'timestamp': current_data['Timestamp']
                    }
                    
                    return 'SELL', signal_data
            
            return None, None
            
        except Exception as e:
            self.log_manager.error_logger.error(f"Error analyzing market data: {str(e)}")
            return None, None
    
    def execute_entry(self, signal_type, signal_data):
        """Execute entry order (simulated)"""
        try:
            # Check if we already have a position
            if self.current_position is not None:
                self.log_manager.trading_logger.info("Position already open, skipping entry signal")
                return False
            
            entry_price = signal_data['entry_price']
            stop_loss = signal_data['stop_loss']
            take_profit = signal_data['take_profit']
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss)
            
            if position_size <= 0:
                self.log_manager.trading_logger.warning("Position size calculation resulted in 0 or negative size")
                return False
            
            # Validate trade
            is_valid, validation_msg = self.risk_manager.validate_trade(position_size, entry_price)
            if not is_valid:
                self.log_manager.trading_logger.warning(f"Trade validation failed: {validation_msg}")
                return False
            
            # Create position
            self.current_position = Position(
                entry_price=entry_price,
                quantity=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=datetime.now(UTC),
                strategy_version=STRATEGY_VERSION,
                signal_data=signal_data
            )
            
            # Update portfolio - only deduct the risk amount for paper trading
            risk_amount = self.risk_manager.current_capital * self.risk_manager.max_risk_per_trade
            self.portfolio_balance -= risk_amount  # Reserve risk amount
            
            # Log comprehensive trade entry
            self.log_manager.trading_logger.info(
                f"TRADE_ENTRY - {self.current_position.trade_id} | "
                f"{signal_type} {signal_data['position_type'].upper()} | "
                f"Price: ${entry_price:.2f} | Qty: {position_size:.6f} BTC | "
                f"SL: ${stop_loss:.2f} | TP: ${take_profit:.2f} | "
                f"Risk: ${signal_data['risk_amount']:.2f}"
            )
            
            # Log to CSV
            self.log_trade_entry(self.current_position)
            
            print(f"\n✅ TRADE OPENED - ID: {self.current_position.trade_id}")
            print(f"📊 {signal_type} {signal_data['position_type'].upper()} position at ${entry_price:,.2f}")
            print(f"🛡️ Stop Loss: ${stop_loss:,.2f} | 🎯 Take Profit: ${take_profit:,.2f}")
            
            return True
            
        except Exception as e:
            self.log_manager.error_logger.error(f"Error executing entry: {str(e)}")
            return False
    
    def check_exit_conditions(self, current_price, current_atr, ema9, ema20):
        """Check if position should be closed"""
        if self.current_position is None:
            return False, None, None
        
        # Update trailing stop with EMA values
        self.current_position.update_trailing_stop(current_price, current_atr, ema9, ema20)
        
        # Print exit condition analysis
        print(f"\n🔍 EXIT ANALYSIS (Strategy v{STRATEGY_VERSION}):")
        print(f"  📍 Current Price: ${current_price:,.2f}")
        print(f"  🛡️ Trailing SL: ${self.current_position.trailing_sl:,.2f}")
        print(f"  🎯 Take Profit: ${self.current_position.take_profit:,.2f}")
        print(f"  📊 Position Type: {self.current_position.position_type.upper()}")
        
        if self.current_position.position_type == 'long':
            print(f"  🔍 SL Check: Price (${current_price:,.2f}) <= SL (${self.current_position.trailing_sl:,.2f}) = {current_price <= self.current_position.trailing_sl}")
            print(f"  🔍 TP Check: Price (${current_price:,.2f}) >= TP (${self.current_position.take_profit:,.2f}) = {current_price >= self.current_position.take_profit}")
            
            # Long position exit conditions
            # Check stop loss (including trailing stop)
            if current_price <= self.current_position.trailing_sl:
                print(f"  ❌ STOP LOSS TRIGGERED: Price hit or below trailing SL")
                return True, current_price, "STOP_LOSS"
            
            # Check take profit
            if current_price >= self.current_position.take_profit:
                print(f"  ✅ TAKE PROFIT TRIGGERED: Price hit or above TP target")
                return True, current_price, "TAKE_PROFIT"
                
        elif self.current_position.position_type == 'short':
            print(f"  🔍 SL Check: Price (${current_price:,.2f}) >= SL (${self.current_position.trailing_sl:,.2f}) = {current_price >= self.current_position.trailing_sl}")
            print(f"  🔍 TP Check: Price (${current_price:,.2f}) <= TP (${self.current_position.take_profit:,.2f}) = {current_price <= self.current_position.take_profit}")
            
            # Short position exit conditions
            # Check stop loss (including trailing stop)
            if current_price >= self.current_position.trailing_sl:
                print(f"  ❌ STOP LOSS TRIGGERED: Price hit or above trailing SL")
                return True, current_price, "STOP_LOSS"
            
            # Check take profit  
            if current_price <= self.current_position.take_profit:
                print(f"  ✅ TAKE PROFIT TRIGGERED: Price hit or below TP target")
                return True, current_price, "TAKE_PROFIT"
        
        print(f"  ✅ No exit conditions met - position continues")
        return False, None, None

    def check_exit_conditions_without_trailing_update(self, current_price, current_atr, ema9, ema20):
        """Check if position should be closed without updating trailing SL"""
        if self.current_position is None:
            return False, None, None
        
        # Print exit condition analysis (without trailing SL update)
        print(f"\n🔍 EXIT ANALYSIS (Strategy v{STRATEGY_VERSION}) - Real-time Check:")
        print(f"  📍 Current Price: ${current_price:,.2f}")
        print(f"  🛡️ Trailing SL: ${self.current_position.trailing_sl:,.2f}")
        print(f"  🎯 Take Profit: ${self.current_position.take_profit:,.2f}")
        print(f"  📊 Position Type: {self.current_position.position_type.upper()}")
        
        if self.current_position.position_type == 'long':
            print(f"  🔍 SL Check: Price (${current_price:,.2f}) <= SL (${self.current_position.trailing_sl:,.2f}) = {current_price <= self.current_position.trailing_sl}")
            print(f"  🔍 TP Check: Price (${current_price:,.2f}) >= TP (${self.current_position.take_profit:,.2f}) = {current_price >= self.current_position.take_profit}")
            
            # Long position exit conditions
            if current_price <= self.current_position.trailing_sl:
                print(f"  ❌ STOP LOSS TRIGGERED: Price hit or below trailing SL")
                return True, current_price, "STOP_LOSS"
            
            if current_price >= self.current_position.take_profit:
                print(f"  ✅ TAKE PROFIT TRIGGERED: Price hit or above TP target")
                return True, current_price, "TAKE_PROFIT"
                
        elif self.current_position.position_type == 'short':
            print(f"  🔍 SL Check: Price (${current_price:,.2f}) >= SL (${self.current_position.trailing_sl:,.2f}) = {current_price >= self.current_position.trailing_sl}")
            print(f"  🔍 TP Check: Price (${current_price:,.2f}) <= TP (${self.current_position.take_profit:,.2f}) = {current_price <= self.current_position.take_profit}")
            
            # Short position exit conditions
            if current_price >= self.current_position.trailing_sl:
                print(f"  ❌ STOP LOSS TRIGGERED: Price hit or above trailing SL")
                return True, current_price, "STOP_LOSS"
            
            if current_price <= self.current_position.take_profit:
                print(f"  ✅ TAKE PROFIT TRIGGERED: Price hit or below TP target")
                return True, current_price, "TAKE_PROFIT"
        
        print(f"  ✅ No exit conditions met - position continues")
        
        return False, None, None
    
    def execute_exit(self, exit_price, exit_reason):
        """Execute exit order (simulated)"""
        try:
            if self.current_position is None:
                return False
            
            # Calculate P&L based on position type
            if self.current_position.position_type == 'long':
                # Long position: profit when exit price > entry price
                pnl = (exit_price - self.current_position.entry_price) * self.current_position.quantity
            else:  # short position
                # Short position: profit when exit price < entry price
                pnl = (self.current_position.entry_price - exit_price) * self.current_position.quantity
            
            # For risk-based trading, return the initial risk amount plus/minus PnL
            initial_risk = PAPER_TRADING_CAPITAL * MAX_RISK_PER_TRADE
            self.portfolio_balance += initial_risk + pnl  # Return risk capital + profit/loss
            
            # Update statistics
            self.total_trades += 1
            self.total_pnl += pnl
            if pnl > 0:
                self.winning_trades += 1
            
            # Close the position (this calculates realized P&L)
            self.current_position.close_position(exit_price, exit_reason)
            
            # Log comprehensive trade exit
            self.log_manager.trading_logger.info(
                f"TRADE_EXIT - {self.current_position.trade_id} | "
                f"Price: ${exit_price:.2f} | PnL: ${pnl:+.2f} | "
                f"Reason: {exit_reason} | Portfolio: ${self.portfolio_balance:.2f}"
            )
            
            # Log to CSV
            self.log_trade_exit(self.current_position)
            
            print(f"\n🚨 TRADE CLOSED - ID: {self.current_position.trade_id}")
            print(f"💰 Exit Price: ${exit_price:,.2f} | Reason: {exit_reason}")
            print(f"📊 P&L: ${pnl:+,.2f} | Portfolio: ${self.portfolio_balance:.2f}")
            
            # Clear position
            closed_position = self.current_position
            self.current_position = None
            
            return True
            
        except Exception as e:
            self.log_manager.error_logger.error(f"Error executing exit: {str(e)}")
            return False
    
    def display_position_status(self, current_price, ema9, ema20, atr):
        """Display comprehensive position status in terminal"""
        if not self.current_position:
            return
        
        status = self.current_position.get_position_status(current_price, ema9, ema20, atr)
        utc_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        local_time = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
        
        # Calculate time in position
        time_in_position = datetime.now(UTC) - self.current_position.entry_time
        hours = int(time_in_position.total_seconds() // 3600)
        minutes = int((time_in_position.total_seconds() % 3600) // 60)
        
        print(f"\n{'='*80}")
        print(f"📊 POSITION STATUS - {utc_time}")
        print(f"🌍 Local Time: {local_time}")
        print(f"{'='*80}")
        
        # Position Overview
        pnl_symbol = "📈" if status['unrealized_pnl'] >= 0 else "📉"
        pnl_color = "+" if status['unrealized_pnl'] >= 0 else ""
        
        # Calculate true portfolio value
        portfolio_info = self.get_current_portfolio_value(current_price)
        
        print(f"🎯 Position Type: {status['position_type']}")
        print(f"💰 Entry Price: ${status['entry_price']:,.2f}")
        print(f"📍 Current Price: ${status['current_price']:,.2f}")
        print(f"📊 Quantity: {status['quantity']:.6f} BTC")
        print(f"⏰ Time in Position: {hours}h {minutes}m")
        
        # P&L Information with Portfolio Update
        print(f"\n💵 P&L ANALYSIS:")
        print(f"  {pnl_symbol} Unrealized P&L: {pnl_color}${status['unrealized_pnl']:,.2f}")
        print(f"  📊 P&L Percentage: {pnl_color}{status['pnl_percentage']:+.2f}%")
        print(f"  💼 Base Portfolio: ${portfolio_info['base_balance']:,.2f}")
        print(f"  💎 Total Portfolio Value: ${portfolio_info['total_value']:,.2f} (including unrealized)")
        
        # Stop Loss Information
        sl_symbol = "🔴" if status['position_type'] == 'LONG' else "🟢"
        print(f"\n🛡️ STOP LOSS ANALYSIS:")
        print(f"  🎯 Original SL: ${status['stop_loss']:,.2f}")
        print(f"  {sl_symbol} Trailing SL: ${status['trailing_sl']:,.2f}")
        print(f"  📏 SL Distance: {status['sl_percentage']:+.2f}%")
        
        # Take Profit
        print(f"\n🎯 TAKE PROFIT:")
        print(f"  💎 Target Price: ${status['take_profit']:,.2f}")
        
        # Technical Indicators
        print(f"\n📈 TECHNICAL INDICATORS:")
        print(f"  🔵 EMA9: ${status['ema9']:,.2f}")
        print(f"  🔴 EMA20: ${status['ema20']:,.2f}")
        print(f"  📊 ATR: ${status['atr']:,.2f}")
        
        # Show swing levels from position data if available
        if hasattr(self.current_position, 'swing_low') and self.current_position.swing_low:
            print(f"  📉 Swing Low: ${self.current_position.swing_low:,.2f}")
        if hasattr(self.current_position, 'swing_high') and self.current_position.swing_high:
            print(f"  📈 Swing High: ${self.current_position.swing_high:,.2f}")
        
        # EMA Analysis
        ema_trend = "BULLISH" if status['ema9'] > status['ema20'] else "BEARISH"
        price_vs_ema9 = "ABOVE" if status['current_price'] > status['ema9'] else "BELOW"
        print(f"  📈 EMA Trend: {ema_trend}")
        print(f"  📍 Price vs EMA9: {price_vs_ema9}")
        
        print(f"{'='*80}\n")
        
        # Log to market data log
        self.log_manager.market_logger.info(
            f"POSITION_STATUS - {status['position_type']} | "
            f"Entry: ${status['entry_price']:,.2f} | "
            f"Current: ${status['current_price']:,.2f} | "
            f"Unrealized P&L: ${status['unrealized_pnl']:+.2f} ({status['pnl_percentage']:+.2f}%) | "
            f"Trailing SL: ${status['trailing_sl']:,.2f} ({status['sl_percentage']:+.2f}%) | "
            f"EMA9: ${status['ema9']:,.2f} | EMA20: ${status['ema20']:,.2f} | ATR: ${status['atr']:,.2f}"
        )

    def display_market_status(self, current_price, ema9, ema20, atr):
        """Display current market status when no position is open"""
        utc_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        local_time = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
        
        print(f"\n{'='*80}")
        print(f"📊 MARKET STATUS - {utc_time}")
        print(f"🌍 Local Time: {local_time}")
        print(f"{'='*80}")
        
        # Current market price
        print(f"💰 Current Price: ${current_price:,.2f}")
        portfolio_info = self.get_current_portfolio_value()
        print(f"💵 Portfolio Balance: ${portfolio_info['total_value']:,.2f}")
        
        # Technical indicators
        print(f"\n📈 TECHNICAL INDICATORS:")
        print(f"  🔵 EMA9: ${ema9:,.2f}")
        print(f"  🔴 EMA20: ${ema20:,.2f}")
        print(f"  📊 ATR: ${atr:,.2f}")
        
        # EMA Analysis
        ema_trend = "BULLISH" if ema9 > ema20 else "BEARISH"
        price_vs_ema9 = "ABOVE" if current_price > ema9 else "BELOW"
        ema_distance = abs(ema9 - ema20) / ema20 * 100
        
        print(f"  📈 EMA Trend: {ema_trend}")
        print(f"  📍 Price vs EMA9: {price_vs_ema9}")
        print(f"  📏 EMA Distance: {ema_distance:.2f}%")
        
        # Market condition assessment
        print(f"\n🔍 MARKET ANALYSIS:")
        if ema9 > ema20 and current_price > ema9:
            print(f"  🟢 Bullish setup - Price above EMAs, ready for LONG signals")
        elif ema9 < ema20 and current_price < ema9:
            print(f"  🔴 Bearish setup - Price below EMAs, ready for SHORT signals")
        else:
            print(f"  🟡 Neutral/Transitional market - No clear trend alignment")
        
        print(f"{'='*80}\n")
        
        # Log to market data log
        self.log_manager.market_logger.info(
            f"MARKET_STATUS - NO_POSITION | "
            f"Price: ${current_price:,.2f} | "
            f"Portfolio: ${self.portfolio_balance:,.2f} | "
            f"EMA9: ${ema9:,.2f} | EMA20: ${ema20:,.2f} | ATR: ${atr:,.2f} | "
            f"Trend: {ema_trend} | Price_vs_EMA9: {price_vs_ema9}"
        )

    def generate_performance_report(self):
        """Generate performance summary report"""
        try:
            win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
            avg_pnl = self.total_pnl / self.total_trades if self.total_trades > 0 else 0
            
            # Get current portfolio value including unrealized P&L
            live_data = self.data_feed.fetch_live_price()
            if live_data and self.current_position:
                portfolio_info = self.get_current_portfolio_value(live_data['last_price'])
                current_portfolio_value = portfolio_info['total_value']
            else:
                portfolio_info = self.get_current_portfolio_value()
                current_portfolio_value = portfolio_info['total_value']
            
            portfolio_return = ((current_portfolio_value - PAPER_TRADING_CAPITAL) / PAPER_TRADING_CAPITAL) * 100
            
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'win_rate_percent': win_rate,
                'total_pnl': self.total_pnl,
                'average_pnl_per_trade': avg_pnl,
                'base_portfolio_balance': self.portfolio_balance,
                'current_portfolio_value': current_portfolio_value,
                'unrealized_pnl': portfolio_info.get('unrealized_pnl', 0.0),
                'initial_capital': PAPER_TRADING_CAPITAL,
                'portfolio_return_percent': portfolio_return,
                'current_position': self.current_position.to_dict() if self.current_position else None
            }
            
            # Save to JSON for detailed analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"{self.log_manager.report_dir}/performance_detail_{timestamp}.json", 'w') as f:
                json.dump(performance_data, f, indent=2, default=str)
            
            print(f"\n{'='*60}")
            print(f"PERFORMANCE SUMMARY")
            print(f"{'='*60}")
            print(f"Total Trades: {self.total_trades}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Total P&L: ${self.total_pnl:.2f}")
            print(f"Base Portfolio: ${self.portfolio_balance:.2f}")
            print(f"Current Portfolio Value: ${current_portfolio_value:.2f}")
            if portfolio_info.get('unrealized_pnl', 0) != 0:
                print(f"Unrealized P&L: ${portfolio_info['unrealized_pnl']:+.2f}")
            print(f"Return: {portfolio_return:.2f}%")
            if self.current_position:
                print(f"Current Position: OPEN (Entry: ${self.current_position.entry_price:.2f})")
            else:
                print(f"Current Position: NONE")
            print(f"{'='*60}\n")
            
        except Exception as e:
            self.log_manager.error_logger.error(f"Error generating performance report: {str(e)}")
    
    def get_current_portfolio_value(self, current_price=None):
        """Calculate current portfolio value including unrealized P&L"""
        base_portfolio = self.portfolio_balance
        
        if self.current_position and current_price:
            # Add unrealized P&L to get true portfolio value
            unrealized_pnl = self.current_position.calculate_unrealized_pnl(current_price)
            total_portfolio_value = base_portfolio + unrealized_pnl
            
            return {
                'base_balance': base_portfolio,
                'unrealized_pnl': unrealized_pnl,
                'total_value': total_portfolio_value,
                'has_position': True
            }
        else:
            return {
                'base_balance': base_portfolio,
                'unrealized_pnl': 0.0,
                'total_value': base_portfolio,
                'has_position': False
            }
    
    def run(self):
        """Main bot execution loop"""
        print("Starting Paper Trading Bot...")
        print("Press Ctrl+C to stop the bot")
        
        try:
            while True:
                try:
                    # Fetch historical data for strategy analysis
                    print("Fetching market data...")
                    df = self.data_feed.fetch_historical_candles(resolution="1h", count=100)
                    
                    if df is None or not self.data_feed.validate_data(df):
                        print("Invalid market data, retrying in 60 seconds...")
                        time.sleep(60)
                        continue
                    
                    # Check for new candle (strategy signals and trailing SL updates)
                    if self.check_for_new_candle(df):
                        print("New candle detected, analyzing for signals...")
                        signal_type, signal_data = self.analyze_market_data(df)
                        
                        if signal_type in ['BUY', 'SELL'] and signal_data:
                            position_type = signal_data['position_type']
                            print(f"{signal_type} signal detected! {position_type.upper()} position")
                            print(f"  Entry Price: ${signal_data['entry_price']:,.2f}")
                            print(f"  Stop Loss: ${signal_data['stop_loss']:,.2f}")
                            print(f"  Take Profit: ${signal_data['take_profit']:,.2f}")
                            print(f"  Position Size: {signal_data['position_size']:.6f} BTC")
                            print(f"  Dollar Risk: ${signal_data['risk_amount']:.2f}")
                            print(f"  Expected Reward: ${signal_data['expected_reward']:.2f}")
                            print(f"  Risk/Reward Ratio: 1:{RISK_REWARD_RATIO}")
                            self.execute_entry(signal_type, signal_data)
                        
                        # Update trailing SL only when new candle completes (EMA values change)
                        if self.current_position:
                            live_data = self.data_feed.fetch_live_price()
                            if live_data:
                                current_price = live_data['last_price']
                                df_with_indicators = calculate_indicators(df.copy())
                                current_atr = df_with_indicators.iloc[-1]['ATR']
                                current_ema9 = df_with_indicators.iloc[-1]['EMA9']
                                current_ema20 = df_with_indicators.iloc[-1]['EMA20']
                                
                                print(f"\n📊 NEW CANDLE - UPDATING TRAILING SL")
                                print(f"  🕐 Candle Time: {df.index[-1]}")
                                print(f"  🔵 Updated EMA9: ${current_ema9:,.2f}")
                                print(f"  🔴 Updated EMA20: ${current_ema20:,.2f}")
                                
                                # Update trailing stop with new EMA values
                                self.current_position.update_trailing_stop(current_price, current_atr, current_ema9, current_ema20)
                    
                    # Display market status and technical indicators (every 60 seconds)
                    live_data = self.data_feed.fetch_live_price()
                    if live_data:
                        current_price = live_data['last_price']
                        # Get current technical indicators from latest data
                        df_with_indicators = calculate_indicators(df.copy())
                        current_atr = df_with_indicators.iloc[-1]['ATR']
                        current_ema9 = df_with_indicators.iloc[-1]['EMA9']
                        current_ema20 = df_with_indicators.iloc[-1]['EMA20']
                        
                        # Display position status if we have one, otherwise show market status
                        if self.current_position:
                            self.display_position_status(current_price, current_ema9, current_ema20, current_atr)
                            
                            # Check exit conditions (every 60 seconds for real-time monitoring)
                            should_exit, exit_price, exit_reason = self.check_exit_conditions_without_trailing_update(current_price, current_atr, current_ema9, current_ema20)
                            if should_exit:
                                print(f"Exit condition met: {exit_reason} at ${exit_price:.2f}")
                                self.execute_exit(exit_price, exit_reason)
                        else:
                            self.display_market_status(current_price, current_ema9, current_ema20, current_atr)
                    
                    # Generate performance report every hour
                    current_time = datetime.now()
                    if current_time.minute == 0:  # Top of the hour
                        self.generate_performance_report()
                    
                    # Wait before next iteration with updated portfolio value
                    live_data = self.data_feed.fetch_live_price()
                    if live_data:
                        current_price = live_data['last_price']
                        portfolio_info = self.get_current_portfolio_value(current_price)
                        print(f"Waiting... Next check in 60 seconds (Portfolio: ${portfolio_info['total_value']:.2f})")
                    else:
                        portfolio_info = self.get_current_portfolio_value()
                        print(f"Waiting... Next check in 60 seconds (Portfolio: ${portfolio_info['total_value']:.2f})")
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    print("\nBot stopped by user")
                    break
                except Exception as e:
                    self.log_manager.error_logger.error(f"Error in main loop: {str(e)}")
                    print(f"Error occurred: {str(e)}. Retrying in 60 seconds...")
                    time.sleep(60)
                    
        finally:
            print("Generating final performance report...")
            self.generate_performance_report()
            print("Paper Trading Bot stopped")

if __name__ == "__main__":
    bot = PaperTradingBot()
    bot.run()
