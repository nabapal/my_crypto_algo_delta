"""
Quick test to show current market conditions and potential signals
"""
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from data_feed import DataFeed
from strategies.ema_atr_strategy_unified import calculate_indicators, get_recent_swing_low, get_recent_swing_high
import pandas as pd

def test_current_signals():
    """Test what signals would be generated with current market data"""
    print("🔍 ANALYZING CURRENT MARKET CONDITIONS")
    print("="*60)
    
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
        
        # Check conditions
        ema9_above_ema20 = current_data['EMA9'] > current_data['EMA20']
        price_above_ema9 = current_data['Close'] > current_data['EMA9']
        price_below_ema9 = current_data['Close'] < current_data['EMA9']
        
        print(f"\n🎯 Signal Analysis:")
        print(f"  EMA9 > EMA20: {ema9_above_ema20} ({'✅' if ema9_above_ema20 else '❌'})")
        print(f"  Price > EMA9: {price_above_ema9} ({'✅' if price_above_ema9 else '❌'})")
        print(f"  Price < EMA9: {price_below_ema9} ({'✅' if price_below_ema9 else '❌'})")
        
        # Check for LONG signal
        long_signal = (current_data['EMA9'] > current_data['EMA20'] and 
                      current_data['Close'] > current_data['EMA9'])
        
        # Check for SHORT signal  
        short_signal = (current_data['EMA9'] < current_data['EMA20'] and
                       current_data['Close'] < current_data['EMA9'])
        
        print(f"\n🚀 TRADING SIGNALS:")
        if long_signal:
            swing_low = get_recent_swing_low(df_with_indicators, current_idx, lookback=10)
            entry_price = current_data['Close']
            stop_loss = swing_low - (current_data['ATR'] * 0.5)  # ATR_MULTIPLIER = 0.5
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 10)  # RISK_REWARD_RATIO = 10
            
            print(f"  🟢 LONG SIGNAL ACTIVE!")
            print(f"     Entry: ${entry_price:,.2f}")
            print(f"     Stop Loss: ${stop_loss:,.2f}")
            print(f"     Take Profit: ${take_profit:,.2f}")
            print(f"     Risk: ${risk:,.2f}")
            print(f"     Reward: ${risk * 10:,.2f}")
            
        elif short_signal:
            swing_high = get_recent_swing_high(df_with_indicators, current_idx, lookback=10)
            entry_price = current_data['Close']
            stop_loss = swing_high + (current_data['ATR'] * 0.5)  # ATR_MULTIPLIER = 0.5
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * 10)  # RISK_REWARD_RATIO = 10
            
            print(f"  🔴 SHORT SIGNAL ACTIVE!")
            print(f"     Entry: ${entry_price:,.2f}")
            print(f"     Stop Loss: ${stop_loss:,.2f}")
            print(f"     Take Profit: ${take_profit:,.2f}")
            print(f"     Risk: ${risk:,.2f}")
            print(f"     Reward: ${risk * 10:,.2f}")
            
        else:
            print(f"  ⏳ NO SIGNAL - Waiting for conditions...")
            if not ema9_above_ema20:
                print(f"     • Need EMA9 > EMA20 for LONG signals")
                print(f"     • Current: EMA9 (${current_data['EMA9']:,.2f}) < EMA20 (${current_data['EMA20']:,.2f})")
                print(f"     • Could generate SHORT signal if price < EMA9")
            else:
                print(f"     • EMA9 > EMA20 ✅")
                print(f"     • Need price movement relative to EMA9")
        
        print(f"\n" + "="*60)
        
    else:
        print("❌ Failed to fetch market data")

if __name__ == "__main__":
    test_current_signals()
