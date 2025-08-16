"""
Data Models for Trading Dashboard
Defines the structure of data returned to the UI
"""

from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json

@dataclass
class BotStatus:
    """Bot operational status"""
    status: str  # RUNNING, STOPPED, ERROR
    mode: str    # PAPER_TRADING, LIVE_TRADING
    last_update: str
    uptime: Optional[str] = None
    session_id: Optional[str] = None
    has_active_position: bool = False

@dataclass 
class MarketData:
    """Current market information"""
    symbol: str
    current_price: float
    last_update: str
    price_change_24h: Optional[float] = None
    price_change_percent: Optional[float] = None

@dataclass
class Portfolio:
    """Portfolio financial summary"""
    initial_capital: float
    base_balance: float      # Balance from completed trades
    unrealized_pnl: float    # CALCULATED from active position
    realized_pnl: float      # Sum from completed trades
    total_balance: float     # CALCULATED: base_balance + unrealized_pnl
    total_return_percent: float  # CALCULATED: ((total_balance - initial_capital) / initial_capital) * 100

@dataclass
class ActivePosition:
    """Active trading position details"""
    has_position: bool
    symbol: Optional[str] = None
    side: Optional[str] = None           # LONG, SHORT
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    quantity: Optional[float] = None
    entry_time: Optional[str] = None
    duration: Optional[str] = None       # CALCULATED
    unrealized_pnl: Optional[float] = None  # CALCULATED
    pnl_percent: Optional[float] = None     # CALCULATED
    stop_loss: Optional[float] = None    # From logs (optional)
    take_profit: Optional[float] = None  # From logs (optional)

@dataclass
class TradingStats:
    """Trading performance statistics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float          # CALCULATED: (winning_trades / total_trades) * 100
    avg_win: float           # CALCULATED: Average positive Realized_PnL
    avg_loss: float          # CALCULATED: Average negative Realized_PnL
    largest_win: float       # Max positive Realized_PnL
    largest_loss: float      # Max negative Realized_PnL (absolute value)

@dataclass
class TechnicalIndicators:
    """Technical analysis data (optional)"""
    ema9: Optional[float] = None
    ema20: Optional[float] = None
    atr: Optional[float] = None
    trend: Optional[str] = None          # BULLISH, BEARISH
    price_vs_ema9: Optional[str] = None  # ABOVE, BELOW

@dataclass
class DashboardData:
    """Complete dashboard data structure"""
    timestamp: str
    bot_status: BotStatus
    market_data: MarketData
    portfolio: Portfolio
    active_position: ActivePosition
    trading_stats: TradingStats
    technical_indicators: Optional[TechnicalIndicators] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "bot_status": asdict(self.bot_status),
            "market_data": asdict(self.market_data),
            "portfolio": asdict(self.portfolio),
            "active_position": asdict(self.active_position),
            "trading_stats": asdict(self.trading_stats),
            "technical_indicators": asdict(self.technical_indicators) if self.technical_indicators else None
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

# Example usage and validation
def create_example_dashboard_data() -> DashboardData:
    """Create example data structure for testing"""
    return DashboardData(
        timestamp=datetime.now().isoformat(),
        bot_status=BotStatus(
            status="RUNNING",
            mode="PAPER_TRADING", 
            last_update=datetime.now().isoformat(),
            uptime="1h 16m",
            session_id="SID_20250815_201814_be6c22",
            has_active_position=True
        ),
        market_data=MarketData(
            symbol="BTCUSDT",
            current_price=117177.00,
            last_update=datetime.now().isoformat()
        ),
        portfolio=Portfolio(
            initial_capital=500.00,
            base_balance=490.00,
            unrealized_pnl=-0.48,
            realized_pnl=0.00,
            total_balance=489.52,
            total_return_percent=-2.10
        ),
        active_position=ActivePosition(
            has_position=True,
            symbol="BTCUSDT",
            side="SHORT",
            entry_price=117108.50,
            current_price=117177.00,
            quantity=0.004413,
            entry_time="2025-08-15T20:19:09Z",
            duration="1h 16m",
            unrealized_pnl=-0.48,
            pnl_percent=-0.06,
            stop_loss=117457.00,
            take_profit=94450.46
        ),
        trading_stats=TradingStats(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            avg_win=0.00,
            avg_loss=0.00,
            largest_win=0.00,
            largest_loss=0.00
        ),
        technical_indicators=TechnicalIndicators(
            ema9=117436.70,
            ema20=117935.64,
            atr=596.93,
            trend="BEARISH",
            price_vs_ema9="BELOW"
        )
    )

if __name__ == "__main__":
    # Test the data structure
    example_data = create_example_dashboard_data()
    print("=== DASHBOARD DATA MODEL ===")
    print(example_data.to_json())
