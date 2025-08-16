"""
Clean Trading Data Manager using proper data models and calculations
"""

import os
import psutil
from datetime import datetime
from typing import Dict, Optional
import logging

from .dashboard_models import (
    DashboardData, BotStatus, MarketData, Portfolio, 
    ActivePosition, TradingStats, TechnicalIndicators
)
from .data_calculator import TradingDataCalculator

logger = logging.getLogger(__name__)

class CleanTradingDataManager:
    """Clean implementation of trading data management"""
    
    def __init__(self):
        # Set up paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.reports_dir = os.path.join(base_dir, "reports")
        self.logs_dir = os.path.join(base_dir, "logs")
        
        # Initialize calculator
        self.calculator = TradingDataCalculator(self.reports_dir, self.logs_dir)
        
        logger.info(f"Initialized CleanTradingDataManager")
        logger.info(f"Reports dir: {self.reports_dir}")
        logger.info(f"Logs dir: {self.logs_dir}")
    
    def detect_bot_status(self) -> str:
        """Detect if the trading bot is running"""
        try:
            # Look for paper_trading_bot.py process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and isinstance(cmdline, list):
                        cmdline_str = ' '.join(cmdline)
                        if 'paper_trading_bot.py' in cmdline_str:
                            return "RUNNING"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return "STOPPED"
            
        except Exception as e:
            logger.error(f"Error detecting bot status: {e}")
            return "UNKNOWN"
    
    async def get_dashboard_data(self) -> DashboardData:
        """Get complete dashboard data structure"""
        try:
            # Get bot status
            bot_status_str = self.detect_bot_status()
            
            # Get current price
            current_price = self.calculator.extract_current_price()
            
            # Get portfolio data
            base_balance, realized_pnl = self.calculator.get_portfolio_balance()
            
            # Get active position data
            position_data = self.calculator.get_active_position_data()
            has_active_position = position_data is not None
            
            # Calculate unrealized P&L if there's an active position
            unrealized_pnl = 0.0
            if has_active_position and current_price > 0:
                unrealized_pnl = self.calculator.calculate_unrealized_pnl(
                    position_data['entry_price'],
                    current_price,
                    position_data['quantity'],
                    position_data['side']
                )
            
            # Calculate portfolio totals
            total_balance = base_balance + unrealized_pnl
            initial_capital = 500.0  # From config
            total_return_percent = ((total_balance - initial_capital) / initial_capital) * 100
            
            # Get trading statistics
            trading_stats = self.calculator.get_trading_statistics()
            
            # Get technical indicators (optional)
            tech_indicators = self.calculator.extract_technical_indicators()
            
            # Build data structures
            bot_status = BotStatus(
                status=bot_status_str,
                mode="PAPER_TRADING",
                last_update=datetime.now().isoformat(),
                has_active_position=has_active_position
            )
            
            market_data = MarketData(
                symbol="BTCUSDT",
                current_price=current_price,
                last_update=datetime.now().isoformat()
            )
            
            portfolio = Portfolio(
                initial_capital=initial_capital,
                base_balance=base_balance,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_balance=total_balance,
                total_return_percent=round(total_return_percent, 2)
            )
            
            # Build active position
            if has_active_position:
                duration = self.calculator.calculate_position_duration(position_data['entry_time'])
                position_value = position_data['entry_price'] * position_data['quantity']
                pnl_percent = (unrealized_pnl / position_value * 100) if position_value > 0 else 0.0
                
                active_position = ActivePosition(
                    has_position=True,
                    symbol=position_data['symbol'],
                    side=position_data['side'],
                    entry_price=position_data['entry_price'],
                    current_price=current_price,
                    quantity=position_data['quantity'],
                    entry_time=position_data['entry_time'],
                    duration=duration,
                    unrealized_pnl=unrealized_pnl,
                    pnl_percent=round(pnl_percent, 2)
                )
            else:
                active_position = ActivePosition(has_position=False)
            
            # Build trading stats
            trading_statistics = TradingStats(
                total_trades=trading_stats['total_trades'],
                winning_trades=trading_stats['winning_trades'],
                losing_trades=trading_stats['losing_trades'],
                win_rate=trading_stats['win_rate'],
                avg_win=trading_stats['avg_win'],
                avg_loss=trading_stats['avg_loss'],
                largest_win=trading_stats['largest_win'],
                largest_loss=trading_stats['largest_loss']
            )
            
            # Build technical indicators (optional)
            technical_indicators = None
            if tech_indicators:
                technical_indicators = TechnicalIndicators(
                    ema9=tech_indicators.get('ema9'),
                    ema20=tech_indicators.get('ema20'),
                    atr=tech_indicators.get('atr'),
                    trend=tech_indicators.get('trend'),
                    price_vs_ema9=tech_indicators.get('price_vs_ema9')
                )
            
            # Build complete dashboard data
            dashboard_data = DashboardData(
                timestamp=datetime.now().isoformat(),
                bot_status=bot_status,
                market_data=market_data,
                portfolio=portfolio,
                active_position=active_position,
                trading_stats=trading_statistics,
                technical_indicators=technical_indicators
            )
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            # Return safe default data
            return DashboardData(
                timestamp=datetime.now().isoformat(),
                bot_status=BotStatus(status="ERROR", mode="UNKNOWN", last_update=datetime.now().isoformat()),
                market_data=MarketData(symbol="BTCUSDT", current_price=0.0, last_update=datetime.now().isoformat()),
                portfolio=Portfolio(initial_capital=500.0, base_balance=500.0, unrealized_pnl=0.0, realized_pnl=0.0, total_balance=500.0, total_return_percent=0.0),
                active_position=ActivePosition(has_position=False),
                trading_stats=TradingStats(total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0, avg_win=0.0, avg_loss=0.0, largest_win=0.0, largest_loss=0.0)
            )
