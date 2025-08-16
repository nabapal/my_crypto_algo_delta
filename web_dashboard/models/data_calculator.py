"""
Data Calculator for Trading Dashboard
Handles all calculations and data extraction logic
"""

import os
import glob
import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TradingDataCalculator:
    """Handles all trading data calculations"""
    
    def __init__(self, reports_dir: str, logs_dir: str):
        self.reports_dir = reports_dir
        self.logs_dir = logs_dir
    
    def get_latest_csv_file(self) -> Optional[str]:
        """Get the most recent trades CSV file"""
        try:
            trade_files = glob.glob(os.path.join(self.reports_dir, "trades_*.csv"))
            if not trade_files:
                return None
            return max(trade_files, key=os.path.getctime)
        except Exception as e:
            logger.error(f"Error finding latest CSV file: {e}")
            return None
    
    def get_latest_console_log(self) -> Optional[str]:
        """Get the most recent console log file"""
        try:
            console_files = glob.glob(os.path.join(self.logs_dir, "*console_output*.log"))
            if not console_files:
                return None
            return max(console_files, key=os.path.getctime)
        except Exception as e:
            logger.error(f"Error finding latest console log: {e}")
            return None
    
    def extract_current_price(self) -> float:
        """Extract current BTC price from console logs"""
        try:
            log_file = self.get_latest_console_log()
            if not log_file:
                logger.warning("No console log file found")
                return 0.0
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for current price patterns in reverse order (most recent first)
            price_patterns = [
                r'📍 Current Price:\s*\$?([\d,]+\.?\d*)',
                r'Current Price:\s*\$?([\d,]+\.?\d*)',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    try:
                        # Get the last (most recent) match and remove commas
                        price_str = matches[-1].replace(',', '')
                        current_price = float(price_str)
                        logger.debug(f"Extracted current price: ${current_price:.2f}")
                        return current_price
                    except ValueError as e:
                        logger.error(f"Error parsing price '{matches[-1]}': {e}")
                        continue
            
            logger.warning("No current price pattern found in console logs")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extracting current price: {e}")
            return 0.0
    
    def calculate_unrealized_pnl(self, entry_price: float, current_price: float, 
                                quantity: float, side: str) -> float:
        """Calculate unrealized P&L mathematically"""
        try:
            if current_price <= 0:
                return 0.0
                
            if side.upper() == 'LONG':
                # LONG: Profit when price goes up
                pnl = (current_price - entry_price) * quantity
            elif side.upper() == 'SHORT':
                # SHORT: Profit when price goes down  
                pnl = (entry_price - current_price) * quantity
            else:
                logger.error(f"Unknown position side: {side}")
                return 0.0
            
            return round(pnl, 2)
            
        except Exception as e:
            logger.error(f"Error calculating unrealized P&L: {e}")
            return 0.0
    
    def get_active_position_data(self) -> Optional[Dict]:
        """Get active position details from CSV"""
        try:
            csv_file = self.get_latest_csv_file()
            if not csv_file:
                logger.warning("No CSV file found")
                return None
            
            df = pd.read_csv(csv_file).fillna(0)
            if df.empty:
                logger.warning("CSV file is empty")
                return None
            
            # Check if last trade is an ENTRY (active position)
            last_trade = df.iloc[-1]
            if last_trade['Action'] != 'ENTRY':
                logger.info("Last trade is not ENTRY - no active position")
                return None
            
            logger.info(f"Found active position: {last_trade['Position_Type']} at ${last_trade['Entry_Price']}")
            
            return {
                'entry_price': float(last_trade['Entry_Price']),
                'quantity': float(last_trade['Quantity']),
                'side': str(last_trade['Position_Type']),  # SHORT/LONG
                'entry_time': str(last_trade['Timestamp_UTC']),
                'symbol': 'BTCUSDT'
            }
            
        except Exception as e:
            logger.error(f"Error getting active position data: {e}")
            return None
    
    def get_portfolio_balance(self) -> Tuple[float, float]:
        """Get base balance and realized P&L from CSV"""
        try:
            csv_file = self.get_latest_csv_file()
            if not csv_file:
                return 500.0, 0.0  # Default initial capital
            
            df = pd.read_csv(csv_file).fillna(0)
            if df.empty:
                return 500.0, 0.0
            
            # Get base balance from last trade
            if 'Portfolio_Balance_After' in df.columns and not df.empty:
                base_balance = float(df.iloc[-1]['Portfolio_Balance_After'])
            else:
                base_balance = 500.0  # Default
            
            # Calculate realized P&L from completed trades (EXIT actions)
            completed_trades = df[df['Action'] == 'EXIT']
            if not completed_trades.empty and 'Realized_PnL' in df.columns:
                realized_pnl = completed_trades['Realized_PnL'].sum()
            else:
                realized_pnl = 0.0
            
            logger.debug(f"Portfolio balance: base=${base_balance:.2f}, realized_pnl=${realized_pnl:.2f}")
            return float(base_balance), float(realized_pnl)
            
        except Exception as e:
            logger.error(f"Error getting portfolio balance: {e}")
            return 500.0, 0.0
            completed_trades = df[df['Action'] == 'EXIT']
            realized_pnl = completed_trades['Realized_PnL'].sum() if not completed_trades.empty else 0.0
            
            return base_balance, float(realized_pnl)
            
        except Exception as e:
            logger.error(f"Error getting portfolio balance: {e}")
            return 500.0, 0.0
    
    def get_trading_statistics(self) -> Dict:
        """Calculate trading performance statistics"""
        try:
            csv_file = self.get_latest_csv_file()
            if not csv_file:
                return {
                    'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                    'win_rate': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0,
                    'largest_win': 0.0, 'largest_loss': 0.0
                }
            
            df = pd.read_csv(csv_file).fillna(0)
            completed_trades = df[df['Action'] == 'EXIT']
            
            if completed_trades.empty:
                return {
                    'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                    'win_rate': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0,
                    'largest_win': 0.0, 'largest_loss': 0.0
                }
            
            # Calculate statistics
            total_trades = len(completed_trades)
            winning_trades = completed_trades[completed_trades['Realized_PnL'] > 0]
            losing_trades = completed_trades[completed_trades['Realized_PnL'] < 0]
            
            win_count = len(winning_trades)
            loss_count = len(losing_trades)
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
            
            avg_win = winning_trades['Realized_PnL'].mean() if not winning_trades.empty else 0.0
            avg_loss = losing_trades['Realized_PnL'].mean() if not losing_trades.empty else 0.0
            
            largest_win = winning_trades['Realized_PnL'].max() if not winning_trades.empty else 0.0
            largest_loss = abs(losing_trades['Realized_PnL'].min()) if not losing_trades.empty else 0.0
            
            return {
                'total_trades': total_trades,
                'winning_trades': win_count,
                'losing_trades': loss_count,
                'win_rate': round(win_rate, 2),
                'avg_win': round(float(avg_win), 2),
                'avg_loss': round(float(avg_loss), 2),
                'largest_win': round(float(largest_win), 2),
                'largest_loss': round(float(largest_loss), 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trading statistics: {e}")
            return {
                'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                'win_rate': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0,
                'largest_win': 0.0, 'largest_loss': 0.0
            }
    
    def calculate_position_duration(self, entry_time_str: str) -> str:
        """Calculate how long position has been open"""
        try:
            entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
            current_time = datetime.now(entry_time.tzinfo)
            duration = current_time - entry_time
            
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception as e:
            logger.error(f"Error calculating position duration: {e}")
            return "0m"
    
    def extract_technical_indicators(self) -> Dict:
        """Extract technical indicators from logs (optional)"""
        try:
            log_file = self.get_latest_console_log()
            if not log_file:
                return {}
            
            with open(log_file, 'r') as f:
                content = f.read()
            
            indicators = {}
            
            # Extract EMA values
            ema9_match = re.search(r'EMA9:\s*\$?([\d,]+\.?\d*)', content)
            if ema9_match:
                indicators['ema9'] = float(ema9_match.group(1).replace(',', ''))
            
            ema20_match = re.search(r'EMA20:\s*\$?([\d,]+\.?\d*)', content)
            if ema20_match:
                indicators['ema20'] = float(ema20_match.group(1).replace(',', ''))
            
            # Extract ATR
            atr_match = re.search(r'ATR:\s*\$?([\d,]+\.?\d*)', content)
            if atr_match:
                indicators['atr'] = float(atr_match.group(1).replace(',', ''))
            
            # Extract trend
            trend_match = re.search(r'EMA Trend:\s*(\w+)', content)
            if trend_match:
                indicators['trend'] = trend_match.group(1)
            
            # Extract price vs EMA9
            price_ema_match = re.search(r'Price vs EMA9:\s*(\w+)', content)
            if price_ema_match:
                indicators['price_vs_ema9'] = price_ema_match.group(1)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error extracting technical indicators: {e}")
            return {}
