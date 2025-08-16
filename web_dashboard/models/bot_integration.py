"""
Bot Integration Module
Direct integration with the Paper Trading Bot for real-time data access
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Add project root to path to import bot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_trading_bot import PaperTradingBot, Position
from data_feed import DataFeed
from config import *

logger = logging.getLogger(__name__)

class BotDataIntegration:
    """
    Direct integration with the running paper trading bot
    This is the PROPER way to get data - use the bot's own methods
    """
    
    def __init__(self):
        self.data_feed = DataFeed()
        # Fix paths - go up two levels from web_dashboard/models to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.reports_dir = os.path.join(project_root, "reports")
        self.logs_dir = os.path.join(project_root, "logs")
        
        logger.info(f"Bot Integration initialized - Reports: {self.reports_dir}, Logs: {self.logs_dir}")
        
    async def get_bot_live_data(self) -> Dict:
        """
        Get live bot data by reading the latest CSV and creating bot objects
        This mimics what the bot would return if we could access it directly
        """
        try:
            # Get latest trade file
            trade_files = [f for f in os.listdir(self.reports_dir) if f.startswith('trades_') and f.endswith('.csv')]
            if not trade_files:
                return self._get_empty_data()
                
            latest_file = max(trade_files, key=lambda f: os.path.getctime(os.path.join(self.reports_dir, f)))
            trades_df = pd.read_csv(os.path.join(self.reports_dir, latest_file))
            
            # Get current market data
            current_price = await self._get_current_market_price()
            
            # Calculate portfolio data using bot's logic
            portfolio_data = await self._calculate_portfolio_data(trades_df, current_price)
            
            # Get active position if exists
            active_position = await self._get_active_position_data(trades_df, current_price)
            
            # Get trading statistics
            trading_stats = await self._calculate_trading_stats(trades_df)
            
            return {
                "bot_status": "RUNNING",  # This would come from process monitoring
                "portfolio": portfolio_data,
                "active_position": active_position,
                "trading_stats": trading_stats,
                "market_data": {
                    "symbol": "BTCUSDT",
                    "current_price": current_price,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting bot live data: {e}")
            return self._get_empty_data()
    
    async def _get_current_market_price(self) -> float:
        """Get current market price using the same data feed as the bot"""
        try:
            # Use the bot's own data feed method
            df = self.data_feed.fetch_historical_candles(resolution="1h", count=1)
            if df is not None and not df.empty:
                return float(df.iloc[-1]['Close'])
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return 0.0
    
    async def _calculate_portfolio_data(self, trades_df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate portfolio data using the bot's exact logic"""
        try:
            initial_capital = PAPER_TRADING_CAPITAL
            
            # Get base portfolio balance (last Portfolio_Balance_After)
            if not trades_df.empty and 'Portfolio_Balance_After' in trades_df.columns:
                base_balance = float(trades_df.iloc[-1]['Portfolio_Balance_After'])
            else:
                base_balance = initial_capital
            
            # Calculate realized P&L from completed trades
            exit_trades = trades_df[trades_df['Action'] == 'EXIT']
            realized_pnl = float(exit_trades['Realized_PnL'].sum()) if not exit_trades.empty else 0.0
            
            # Calculate unrealized P&L for active position
            unrealized_pnl = 0.0
            has_active_position = False
            
            # Check for active position (last trade is ENTRY)
            if not trades_df.empty and trades_df.iloc[-1]['Action'] == 'ENTRY':
                has_active_position = True
                last_trade = trades_df.iloc[-1]
                
                # Use bot's Position class logic for P&L calculation
                entry_price = float(last_trade['Entry_Price'])
                quantity = float(last_trade['Quantity'])
                position_type = last_trade['Position_Type'].lower()
                
                if current_price > 0:
                    if position_type == 'long':
                        unrealized_pnl = (current_price - entry_price) * quantity
                    else:  # short
                        unrealized_pnl = (entry_price - current_price) * quantity
            
            # Calculate total portfolio value (bot's logic)
            total_balance = base_balance + unrealized_pnl
            total_return_percent = ((total_balance - initial_capital) / initial_capital) * 100
            
            return {
                "initial_capital": initial_capital,
                "base_balance": base_balance,
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": realized_pnl,
                "total_balance": total_balance,
                "total_return_percent": total_return_percent,
                "has_active_position": has_active_position
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio data: {e}")
            return {
                "initial_capital": PAPER_TRADING_CAPITAL,
                "base_balance": PAPER_TRADING_CAPITAL,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "total_balance": PAPER_TRADING_CAPITAL,
                "total_return_percent": 0.0,
                "has_active_position": False
            }
    
    async def _get_active_position_data(self, trades_df: pd.DataFrame, current_price: float) -> Optional[Dict]:
        """Get active position data using bot's Position class logic"""
        try:
            # Check for active position
            if trades_df.empty or trades_df.iloc[-1]['Action'] != 'ENTRY':
                return None
                
            last_trade = trades_df.iloc[-1]
            entry_price = float(last_trade['Entry_Price'])
            quantity = float(last_trade['Quantity'])
            position_type = last_trade['Position_Type']
            entry_time = last_trade['Timestamp_UTC']
            
            # Calculate position metrics using bot's logic
            if position_type.lower() == 'long':
                unrealized_pnl = (current_price - entry_price) * quantity
                pnl_percentage = ((current_price - entry_price) / entry_price) * 100
            else:  # short
                unrealized_pnl = (entry_price - current_price) * quantity
                pnl_percentage = ((entry_price - current_price) / entry_price) * 100
            
            # Calculate time in position
            entry_dt = pd.to_datetime(entry_time)
            current_dt = datetime.now()
            time_diff = current_dt - entry_dt.replace(tzinfo=None)
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            
            return {
                "trade_id": last_trade['Trade_ID'],
                "symbol": "BTCUSDT",
                "side": position_type.upper(),
                "entry_price": entry_price,
                "current_price": current_price,
                "quantity": quantity,
                "entry_time": entry_time,
                "duration": f"{hours}h {minutes}m",
                "unrealized_pnl": unrealized_pnl,
                "pnl_percentage": pnl_percentage,
                "stop_loss": float(last_trade['Stop_Loss']) if last_trade['Stop_Loss'] else None,
                "take_profit": float(last_trade['Take_Profit']) if last_trade['Take_Profit'] else None
            }
            
        except Exception as e:
            logger.error(f"Error getting active position data: {e}")
            return None
    
    async def _calculate_trading_stats(self, trades_df: pd.DataFrame) -> Dict:
        """Calculate trading statistics from completed trades"""
        try:
            # Get completed trades (EXIT actions)
            exit_trades = trades_df[trades_df['Action'] == 'EXIT']
            
            if exit_trades.empty:
                return {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "avg_win": 0.0,
                    "avg_loss": 0.0,
                    "largest_win": 0.0,
                    "largest_loss": 0.0
                }
            
            # Calculate statistics
            total_trades = len(exit_trades)
            winning_trades = exit_trades[exit_trades['Realized_PnL'] > 0]
            losing_trades = exit_trades[exit_trades['Realized_PnL'] < 0]
            
            win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0.0
            avg_win = float(winning_trades['Realized_PnL'].mean()) if not winning_trades.empty else 0.0
            avg_loss = float(losing_trades['Realized_PnL'].mean()) if not losing_trades.empty else 0.0
            largest_win = float(winning_trades['Realized_PnL'].max()) if not winning_trades.empty else 0.0
            largest_loss = abs(float(losing_trades['Realized_PnL'].min())) if not losing_trades.empty else 0.0
            
            return {
                "total_trades": total_trades,
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "win_rate": win_rate,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "largest_win": largest_win,
                "largest_loss": largest_loss
            }
            
        except Exception as e:
            logger.error(f"Error calculating trading stats: {e}")
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0
            }
    
    def _get_empty_data(self) -> Dict:
        """Return empty data structure when no data is available"""
        return {
            "bot_status": "STOPPED",
            "portfolio": {
                "initial_capital": PAPER_TRADING_CAPITAL,
                "base_balance": PAPER_TRADING_CAPITAL,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "total_balance": PAPER_TRADING_CAPITAL,
                "total_return_percent": 0.0,
                "has_active_position": False
            },
            "active_position": None,
            "trading_stats": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0
            },
            "market_data": {
                "symbol": "BTCUSDT",
                "current_price": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        }
