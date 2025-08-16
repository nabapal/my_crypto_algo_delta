"""
Trading Data Manager
Handles all trading data operations, file monitoring, and real-time updates
"""

import os
import sys
import glob
import pandas as pd
import json
import asyncio
import psutil
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import config
except ImportError:
    config = None

logger = logging.getLogger(__name__)

class TradingFileWatcher(FileSystemEventHandler):
    """Monitor trading files for changes"""
    
    def __init__(self, trading_manager):
        self.trading_manager = trading_manager
        self.last_trade_count = 0
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Check for trade CSV files
        if file_path.endswith('.csv') and 'trades_' in os.path.basename(file_path):
            # Schedule coroutine in a thread-safe way
            if hasattr(self.trading_manager, '_loop') and self.trading_manager._loop:
                self.trading_manager._loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.trading_manager.handle_trade_file_change(file_path))
                )
        
        # Check for log files  
        elif file_path.endswith('.log'):
            log_type = self.get_log_type(file_path)
            if log_type and hasattr(self.trading_manager, '_loop') and self.trading_manager._loop:
                self.trading_manager._loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.trading_manager.handle_log_file_change(file_path, log_type))
                )
    
    def get_log_type(self, file_path: str) -> Optional[str]:
        """Determine log type from file path"""
        filename = os.path.basename(file_path)
        
        if 'console_output' in filename:
            return 'console'
        elif 'market_data' in filename:
            return 'market'
        elif 'trading_activity' in filename:
            return 'trading'
        elif 'api_communication' in filename:
            return 'api'
        elif 'errors' in filename:
            return 'errors'
        
        return None

class TradingDataManager:
    """Main class for managing all trading data operations"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.reports_dir = os.path.join(self.base_dir, "reports")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        
        self.websocket_manager = None
        self.file_observer = None
        self.last_trade_data = None
        self.current_bot_status = {"running": False, "pid": None}
        self._loop = None  # Store event loop reference
        
        # Cache for performance
        self.cache = {
            "trades": None,
            "performance": None,
            "logs": {},
            "last_update": None
        }
    
    async def start_monitoring(self, websocket_manager):
        """Start monitoring files and bot status"""
        self.websocket_manager = websocket_manager
        self._loop = asyncio.get_running_loop()  # Store current event loop
        
        # Start file watcher
        self.start_file_watcher()
        
        # Start periodic status checks
        asyncio.create_task(self.periodic_status_check())
        asyncio.create_task(self.periodic_log_monitoring())
        
        logger.info("✅ Trading data monitoring started")
    
    def start_file_watcher(self):
        """Start file system watcher"""
        try:
            event_handler = TradingFileWatcher(self)
            self.file_observer = Observer()
            
            # Watch reports directory
            if os.path.exists(self.reports_dir):
                self.file_observer.schedule(event_handler, self.reports_dir, recursive=False)
            
            # Watch logs directory  
            if os.path.exists(self.logs_dir):
                self.file_observer.schedule(event_handler, self.logs_dir, recursive=False)
            
            self.file_observer.start()
            logger.info("📁 File watcher started")
            
        except Exception as e:
            logger.error(f"❌ Error starting file watcher: {e}")
    
    async def handle_trade_file_change(self, file_path: str):
        """Handle changes to trade CSV files"""
        try:
            # Load and check for new trades
            trades_df = pd.read_csv(file_path)
            
            if trades_df.empty:
                return
            
            latest_trade = trades_df.iloc[-1].to_dict()
            
            # Check if this is a new trade
            if self.last_trade_data is None or latest_trade['Trade_ID'] != self.last_trade_data.get('Trade_ID'):
                self.last_trade_data = latest_trade
                
                # Determine event type
                if latest_trade['Action'] == 'ENTRY':
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_trade_event("trade_opened", {
                            "trade_id": latest_trade['Trade_ID'],
                            "position_type": latest_trade['Position_Type'],
                            "entry_price": latest_trade['Entry_Price'],
                            "quantity": latest_trade['Quantity'],
                            "timestamp": latest_trade['Timestamp_UTC']
                        })
                    
                elif latest_trade['Action'] == 'EXIT':
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_trade_event("trade_closed", {
                            "trade_id": latest_trade['Trade_ID'],
                            "exit_price": latest_trade.get('Exit_Price', 0),
                            "pnl": latest_trade['P&L'],
                            "portfolio_balance": latest_trade['Portfolio_Balance_After'],
                            "timestamp": latest_trade['Timestamp_UTC']
                        })
            
            # Clear trades cache
            self.cache["trades"] = None
            
        except Exception as e:
            logger.error(f"❌ Error handling trade file change: {e}")
    
    async def handle_log_file_change(self, file_path: str, log_type: str):
        """Handle changes to log files"""
        try:
            # Read last few lines of log
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if not lines:
                return
            
            # Check last line for specific events
            last_line = lines[-1].strip()
            
            # Check for P&L updates in console logs
            if log_type == 'console' and 'Unrealized P&L:' in last_line:
                pnl_data = self.parse_unrealized_pnl(last_line)
                if pnl_data and self.websocket_manager:
                    await self.websocket_manager.broadcast_pnl_update(pnl_data)
            
            # Clear log cache for this type
            self.cache["logs"][log_type] = None
            
        except Exception as e:
            logger.error(f"❌ Error handling log file change: {e}")
    
    def parse_unrealized_pnl(self, log_line: str) -> Optional[Dict]:
        """Parse unrealized P&L from console log line"""
        try:
            import re
            
            # Extract unrealized P&L value
            match = re.search(r'Unrealized P&L:\s*\$([+-]?\d+\.\d+)', log_line)
            if not match:
                # Try alternative format
                match = re.search(r'Unrealized P&L:\s*([+-])\$(\d+\.\d+)', log_line)
                if match:
                    sign = match.group(1)
                    value = float(match.group(2))
                    pnl = value if sign == '+' else -value
                else:
                    return None
            else:
                pnl = float(match.group(1))
            
            return {
                "unrealized_pnl": pnl,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing P&L from log line: {e}")
            return None
    
    async def periodic_status_check(self):
        """Periodically check bot status"""
        while True:
            try:
                current_status = await self.get_bot_status()
                
                # Check if status changed
                if (current_status["running"] != self.current_bot_status["running"] or 
                    current_status["pid"] != self.current_bot_status["pid"]):
                    
                    self.current_bot_status = current_status
                    if self.websocket_manager:
                        await self.websocket_manager.broadcast_status_update(current_status)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in periodic status check: {e}")
                await asyncio.sleep(30)
    
    async def periodic_log_monitoring(self):
        """Periodically monitor logs for updates"""
        while True:
            try:
                # Check console logs for latest updates
                console_log = self.get_latest_log_file('console_output_*.log')
                if console_log:
                    await self.handle_log_file_change(console_log, 'console')
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in periodic log monitoring: {e}")
                await asyncio.sleep(10)
    
    async def get_bot_status(self) -> Dict:
        """Get current bot status"""
        try:
            bot_running = False
            bot_pid = None
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline'] if proc.info['cmdline'] else []
                        cmdline_str = ' '.join(cmdline).lower()
                        
                        # Check for paper_trading_bot in command line (with or without .py)
                        if 'paper_trading_bot' in cmdline_str:
                            bot_running = True
                            bot_pid = proc.info['pid']
                            logger.info(f"✅ Found trading bot process: PID {bot_pid}, Command: {' '.join(cmdline)}")
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not bot_running:
                logger.info("ℹ️ No trading bot process found")
            
            return {
                "running": bot_running,
                "pid": bot_pid,
                "timestamp": datetime.now().isoformat(),
                "status": "RUNNING" if bot_running else "STOPPED"
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {
                "running": False,
                "pid": None,
                "timestamp": datetime.now().isoformat(),
                "status": "ERROR",
                "error": str(e)
            }

    async def get_comprehensive_status(self) -> Dict:
        """Get comprehensive bot and financial status"""
        try:
            # Get bot status
            bot_status = await self.get_bot_status()
            
            # Get trading data and calculate financial metrics
            financial_data = await self.calculate_financial_metrics()
            
            return {
                "bot": bot_status,
                "portfolio": financial_data["portfolio"],
                "trading": financial_data["trading"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {
                "bot": {"running": False, "status": "ERROR", "error": str(e)},
                "portfolio": {"initial_capital": 500, "balance": 500, "unrealized_pnl": 0, "realized_pnl": 0},
                "trading": {"total_trades": 0, "win_rate": 0, "active_position": False},
                "error": str(e)
            }
    
    async def calculate_financial_metrics(self) -> Dict:
        """Calculate comprehensive financial metrics"""
        try:
            # Load configuration for initial capital
            initial_capital = 500  # Default paper trading capital
            
            # Get trade data
            trade_files = glob.glob(os.path.join(self.reports_dir, "trades_*.csv"))
            
            if not trade_files:
                return {
                    "portfolio": {
                        "initial_capital": initial_capital,
                        "balance": initial_capital,
                        "unrealized_pnl": 0.0,
                        "realized_pnl": 0.0
                    },
                    "trading": {
                        "total_trades": 0,
                        "win_rate": 0.0,
                        "active_position": False,
                        "avg_win": 0.0,
                        "avg_loss": 0.0
                    }
                }
            
            latest_file = max(trade_files, key=os.path.getctime)
            trades_df = pd.read_csv(latest_file)
            
            if trades_df.empty:
                return {
                    "portfolio": {
                        "initial_capital": initial_capital,
                        "balance": initial_capital,
                        "unrealized_pnl": 0.0,
                        "realized_pnl": 0.0
                    },
                    "trading": {
                        "total_trades": 0,
                        "win_rate": 0.0,
                        "active_position": False,
                        "avg_win": 0.0,
                        "avg_loss": 0.0
                    }
                }
            
            # Fill NaN values
            trades_df = trades_df.fillna(0)
            
            # Calculate realized P&L from completed trades
            completed_trades = trades_df[trades_df['Action'] == 'EXIT']
            realized_pnl = completed_trades['Realized_PnL'].sum() if not completed_trades.empty else 0.0
            
            # Get current portfolio balance from latest trade (Portfolio_Balance_After for last trade)
            if not trades_df.empty:
                last_trade = trades_df.iloc[-1]
                if 'Portfolio_Balance_After' in trades_df.columns:
                    current_base_balance = last_trade['Portfolio_Balance_After']
                else:
                    current_base_balance = initial_capital
            else:
                current_base_balance = initial_capital
            
            # Calculate unrealized P&L from active position
            unrealized_pnl = 0.0
            active_position = False
            
            # Check if there's an active position (last trade is ENTRY)
            if not trades_df.empty and trades_df.iloc[-1]['Action'] == 'ENTRY':
                active_position = True
                
                # Get position details
                last_trade = trades_df.iloc[-1]
                entry_price = last_trade['Price']
                quantity = last_trade['Quantity']
                side = last_trade['Side']
                
                # Get current market price from logs
                current_price = await self.get_current_price_from_logs()
                
                if current_price > 0:
                    # Calculate unrealized P&L
                    unrealized_pnl = await self.calculate_unrealized_pnl(
                        entry_price, current_price, quantity, side
                    )
                else:
                    logger.warning("Could not get current price from logs, using 0 for unrealized P&L")
                    unrealized_pnl = 0.0
            
            # Calculate current balance
            current_balance = current_base_balance + unrealized_pnl
            
            # Calculate trading statistics
            total_trades = len(completed_trades)
            winning_trades = completed_trades[completed_trades['Realized_PnL'] > 0]
            losing_trades = completed_trades[completed_trades['Realized_PnL'] < 0]
            
            win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0.0
            avg_win = winning_trades['Realized_PnL'].mean() if not winning_trades.empty else 0.0
            avg_loss = losing_trades['Realized_PnL'].mean() if not losing_trades.empty else 0.0
            
            return {
                "portfolio": {
                    "initial_capital": initial_capital,
                    "balance": current_balance,
                    "unrealized_pnl": unrealized_pnl,
                    "realized_pnl": realized_pnl
                },
                "trading": {
                    "total_trades": total_trades,
                    "win_rate": win_rate,
                    "active_position": active_position,
                    "avg_win": avg_win,
                    "avg_loss": avg_loss
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {e}")
            return {
                "portfolio": {
                    "initial_capital": 500,
                    "balance": 500,
                    "unrealized_pnl": 0.0,
                    "realized_pnl": 0.0
                },
                "trading": {
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "active_position": False,
                    "avg_win": 0.0,
                    "avg_loss": 0.0
                }
            }
    
    async def calculate_unrealized_pnl(self, entry_price: float, current_price: float, 
                                       quantity: float, side: str) -> float:
        """Calculate unrealized P&L from position data"""
        try:
            if side.upper() == 'LONG':
                # LONG: Profit when price goes up
                pnl = (current_price - entry_price) * quantity
            elif side.upper() == 'SHORT':
                # SHORT: Profit when price goes down
                pnl = (entry_price - current_price) * quantity
            else:
                logger.error(f"Unknown position side: {side}")
                return 0.0
            
            logger.debug(f"Calculated P&L: {side} position, entry=${entry_price:.2f}, current=${current_price:.2f}, qty={quantity:.6f}, pnl=${pnl:.2f}")
            return round(pnl, 2)
            
        except Exception as e:
            logger.error(f"Error calculating unrealized P&L: {e}")
            return 0.0

    async def get_current_price_from_logs(self) -> float:
        """Extract current BTC price from console logs"""
        try:
            console_logs = await self.get_log_data('console')
            
            if not console_logs or 'logs' not in console_logs:
                logger.debug("No console logs available for price extraction")
                return 0.0
            
            content = console_logs['logs']
            
            # Look for current price patterns
            price_patterns = [
                r'📍 Current Price:\s*\$?([\d,]+\.?\d*)',
                r'Current Price:\s*\$?([\d,]+\.?\d*)',
                r'Price:\s*\$?([\d,]+\.?\d*)'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    try:
                        # Remove commas and convert to float
                        price_str = matches[-1].replace(',', '')
                        current_price = float(price_str)
                        logger.debug(f"Current price extracted from logs: ${current_price:.2f}")
                        return current_price
                    except ValueError:
                        continue
            
            logger.debug("No current price found in console logs")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extracting current price from logs: {e}")
            return 0.0

    async def get_comprehensive_dashboard_data(self) -> Dict:
        """Get all data needed for the dashboard in one comprehensive structure"""
        try:
            # Get all component data
            status_data = await self.get_comprehensive_status()
            financial_data = await self.calculate_financial_metrics()
            
            # Get active position details if available
            active_position_data = None
            trade_files = glob.glob(os.path.join(self.reports_dir, "trades_*.csv"))
            
            if trade_files:
                latest_file = max(trade_files, key=os.path.getctime)
                trades_df = pd.read_csv(latest_file).fillna(0)
                
                if not trades_df.empty and trades_df.iloc[-1]['Action'] == 'ENTRY':
                    last_trade = trades_df.iloc[-1]
                    current_price = await self.get_current_price_from_logs()
                    
                    active_position_data = {
                        "symbol": "BTCUSDT",
                        "side": last_trade['Side'],
                        "entry_price": float(last_trade['Price']),
                        "current_price": current_price,
                        "quantity": float(last_trade['Quantity']),
                        "entry_time": last_trade['Timestamp'],
                        "unrealized_pnl": financial_data['portfolio']['unrealized_pnl'],
                        "pnl_percent": (financial_data['portfolio']['unrealized_pnl'] / (float(last_trade['Price']) * float(last_trade['Quantity']))) * 100 if last_trade['Price'] and last_trade['Quantity'] else 0
                    }
            
            # Combine all data
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "bot_status": {
                    "status": status_data.get('status', 'UNKNOWN'),
                    "mode": "PAPER_TRADING",
                    "last_update": datetime.now().isoformat(),
                    "has_active_position": financial_data['trading']['active_position']
                },
                "portfolio": financial_data['portfolio'],
                "trading_stats": financial_data['trading'],
                "active_position": active_position_data,
                "market_data": {
                    "symbol": "BTCUSDT",
                    "current_price": await self.get_current_price_from_logs(),
                    "last_update": datetime.now().isoformat()
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard data: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "bot_status": {"status": "ERROR", "mode": "UNKNOWN"},
                "portfolio": {"initial_capital": 500, "balance": 500, "unrealized_pnl": 0, "realized_pnl": 0},
                "trading_stats": {"total_trades": 0, "win_rate": 0, "active_position": False},
                "active_position": None,
                "market_data": {"symbol": "BTCUSDT", "current_price": 0}
            }
        """Get current bot status"""
        try:
            bot_running = False
            bot_pid = None
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline'] if proc.info['cmdline'] else []
                        cmdline_str = ' '.join(cmdline).lower()
                        
                        # Check for paper_trading_bot in command line (with or without .py)
                        if 'paper_trading_bot' in cmdline_str:
                            bot_running = True
                            bot_pid = proc.info['pid']
                            logger.info(f"✅ Found trading bot process: PID {bot_pid}, Command: {' '.join(cmdline)}")
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not bot_running:
                logger.info("ℹ️ No trading bot process found")
            
            return {
                "running": bot_running,
                "pid": bot_pid,
                "timestamp": datetime.now().isoformat(),
                "status": "RUNNING" if bot_running else "STOPPED"
            }
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {
                "running": False,
                "pid": None,
                "timestamp": datetime.now().isoformat(),
                "status": "ERROR",
                "error": str(e)
            }
    
    async def get_trades_data(self) -> Dict:
        """Get trading data"""
        try:
            if self.cache["trades"] is not None:
                return self.cache["trades"]
            
            trade_files = glob.glob(os.path.join(self.reports_dir, "trades_*.csv"))
            
            if not trade_files:
                return {"trades": [], "summary": {"total_trades": 0}}
            
            latest_file = max(trade_files, key=os.path.getctime)
            trades_df = pd.read_csv(latest_file)
            
            if trades_df.empty:
                return {"trades": [], "summary": {"total_trades": 0}}
            
            # Convert to dict for JSON serialization and handle NaN values
            trades_df = trades_df.fillna(0)  # Replace NaN with 0
            trades_list = trades_df.to_dict('records')
            
            # Calculate summary
            completed_trades = trades_df[trades_df['Action'] == 'EXIT']
            summary = {
                "total_trades": len(completed_trades),
                "active_position": trades_df.iloc[-1]['Action'] == 'ENTRY' if not trades_df.empty else False,
                "total_pnl": completed_trades['P&L'].sum() if not completed_trades.empty else 0.0,
                "win_rate": len(completed_trades[completed_trades['P&L'] > 0]) / len(completed_trades) * 100 if len(completed_trades) > 0 else 0.0
            }
            
            result = {
                "trades": trades_list,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache["trades"] = result
            return result
            
        except Exception as e:
            logger.error(f"Error getting trades data: {e}")
            return {"trades": [], "summary": {"total_trades": 0}, "error": str(e)}
    
    async def get_performance_data(self) -> Dict:
        """Get performance metrics"""
        try:
            if self.cache["performance"] is not None:
                return self.cache["performance"]
            
            performance_files = glob.glob(os.path.join(self.reports_dir, "performance_detail_*.json"))
            
            if not performance_files:
                return {"performance": {}, "timestamp": datetime.now().isoformat()}
            
            latest_file = max(performance_files, key=os.path.getctime)
            
            with open(latest_file, 'r') as f:
                performance_data = json.load(f)
            
            result = {
                "performance": performance_data,
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache["performance"] = result
            return result
            
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return {"performance": {}, "error": str(e)}
    
    async def get_log_data(self, log_type: str) -> Dict:
        """Get specific log data"""
        try:
            if log_type in self.cache["logs"] and self.cache["logs"][log_type] is not None:
                return self.cache["logs"][log_type]
            
            # Map log types to file patterns
            pattern_map = {
                'console': '*console_output*.log',
                'market': '*market_data*.log', 
                'trading': '*trading_activity*.log',
                'api': '*api_communication*.log',
                'errors': '*errors*.log'
            }
            
            pattern = pattern_map.get(log_type, f"*{log_type}*.log")
            log_file = self.get_latest_log_file(pattern)
            
            if not log_file or not os.path.exists(log_file):
                logger.info(f"🔍 Log file not found for {log_type} with pattern {pattern}")
                return {"logs": "", "error": "Log file not found"}
            
            logger.info(f"✅ Found log file for {log_type}: {log_file}")
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Return last 100 lines
            lines = content.split('\n')
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            result = {
                "logs": '\n'.join(recent_lines),
                "content": '\n'.join(recent_lines),  # Add both for compatibility
                "file_path": log_file,
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache["logs"][log_type] = result
            return result
            
        except Exception as e:
            logger.error(f"Error getting log data for {log_type}: {e}")
            return {"logs": "", "error": str(e)}
    
    def get_latest_log_file(self, pattern: str) -> Optional[str]:
        """Get the latest log file matching pattern"""
        try:
            files = glob.glob(os.path.join(self.logs_dir, pattern))
            if not files:
                return None
            return max(files, key=os.path.getctime)
        except Exception:
            return None
    
    async def get_current_status(self) -> Dict:
        """Get comprehensive current status"""
        try:
            bot_status = await self.get_bot_status()
            trades_data = await self.get_trades_data()
            
            # Get current portfolio info
            portfolio_balance = 500.0  # Default
            unrealized_pnl = 0.0
            
            if trades_data["trades"]:
                latest_trade = trades_data["trades"][-1]
                portfolio_balance = latest_trade.get('Portfolio_Balance_After', 500.0)
                
                # Try to get unrealized P&L from console logs
                console_data = await self.get_log_data('console')
                if console_data["logs"]:
                    lines = console_data["logs"].split('\n')
                    for line in reversed(lines):
                        if 'Unrealized P&L:' in line:
                            pnl_data = self.parse_unrealized_pnl(line)
                            if pnl_data:
                                unrealized_pnl = pnl_data["unrealized_pnl"]
                                break
            
            return {
                "bot": bot_status,
                "portfolio": {
                    "balance": portfolio_balance,
                    "unrealized_pnl": unrealized_pnl,
                    "initial_capital": getattr(config, 'PAPER_TRADING_CAPITAL', 500) if config else 500
                },
                "trading": trades_data["summary"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
