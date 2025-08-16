"""
Test the corrected risk/reward calculation with actual position sizing
"""
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from data_feed import DataFeed
from strategies.ema_atr_strategy_unified import calculate_indicators, get_recent_swing_low, get_recent_swing_high
from config import MAX_RISK_PER_TRADE, RISK_REWARD_RATIO, ATR_MULTIPLIER

def test_corrected_calculation():
    """Test the corrected risk/reward calculation"""
    print("🔍 TESTING CORRECTED RISK/REWARD CALCULATION")
    print("="*70)
    
    # Get market data
    df_client = DataFeed()
    df = df_client.fetch_historical_candles(resolution="1h", count=100)
    
    if df is not None:
        # Calculate indicators
        df_with_indicators = calculate_indicators(df.copy())
        
        # Get latest data
        current_idx = len(df_with_indicators) - 1
        current_data = df_with_indicators.iloc[current_idx]
        
        print(f"📊 Current Market Data:")
        print(f"  BTC Price: ${current_data['Close']:,.2f}")
        print(f"  EMA9: ${current_data['EMA9']:,.2f}")
        print(f"  EMA20: ${current_data['EMA20']:,.2f}")
        print(f"  ATR: ${current_data['ATR']:,.2f}")
        
        # Portfolio settings
        portfolio_balance = 500.0  # $500 starting capital
        portfolio_risk_percent = MAX_RISK_PER_TRADE  # 2%
        portfolio_risk_amount = portfolio_balance * portfolio_risk_percent  # $10
        
        print(f"\n💰 Portfolio Settings:")
        print(f"  Total Capital: ${portfolio_balance:,.2f}")
        print(f"  Risk per Trade: {portfolio_risk_percent*100:.1f}% = ${portfolio_risk_amount:.2f}")
        
        # Check for SHORT signal (current market condition)
        short_signal = (current_data['EMA9'] < current_data['EMA20'] and
                       current_data['Close'] < current_data['EMA9'])
        
        if short_signal:
            print(f"\n🔴 SHORT SIGNAL CALCULATION:")
            
            # Calculate SHORT signal parameters
            swing_high = get_recent_swing_high(df_with_indicators, current_idx, lookback=10)
            entry_price = current_data['Close']
            stop_loss = swing_high + (current_data['ATR'] * ATR_MULTIPLIER)
            
            # Price risk per BTC
            price_risk_per_btc = stop_loss - entry_price
            
            # Position size calculation
            position_size_btc = portfolio_risk_amount / price_risk_per_btc
            
            # Take profit calculation
            take_profit = entry_price - (price_risk_per_btc * RISK_REWARD_RATIO)
            
            # Actual dollar amounts
            actual_dollar_risk = position_size_btc * price_risk_per_btc
            profit_per_btc = entry_price - take_profit
            actual_dollar_reward = position_size_btc * profit_per_btc
            
            print(f"  Entry Price: ${entry_price:,.2f}")
            print(f"  Stop Loss: ${stop_loss:,.2f}")
            print(f"  Take Profit: ${take_profit:,.2f}")
            print(f"")
            print(f"  Price Risk per BTC: ${price_risk_per_btc:,.2f}")
            print(f"  Position Size: {position_size_btc:.6f} BTC")
            print(f"")
            print(f"  ✅ ACTUAL DOLLAR RISK: ${actual_dollar_risk:.2f}")
            print(f"  ✅ ACTUAL DOLLAR REWARD: ${actual_dollar_reward:.2f}")
            print(f"  ✅ Risk/Reward Ratio: 1:{RISK_REWARD_RATIO}")
            print(f"")
            print(f"📈 Trade Summary:")
            print(f"  • Risking ${actual_dollar_risk:.2f} to make ${actual_dollar_reward:.2f}")
            print(f"  • Position value: ${position_size_btc * entry_price:.2f}")
            print(f"  • This represents {(actual_dollar_risk/portfolio_balance)*100:.1f}% of portfolio")
            
        else:
            print(f"\n⏳ No SHORT signal currently active")
        
        print(f"\n" + "="*70)
        
    else:
        print("❌ Failed to fetch market data")

if __name__ == "__main__":
    test_corrected_calculation()
