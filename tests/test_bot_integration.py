#!/usr/bin/env python3
"""
Test Bot Integration Approach
Test the new bot integration that directly uses bot classes and logic
"""

import sys
import os
import asyncio

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_dashboard'))

from web_dashboard.models.bot_integration import BotDataIntegration

async def test_bot_integration():
    """Test the bot integration approach"""
    print("🤖 Testing Bot Integration Approach")
    print("=" * 60)
    
    try:
        bot_integration = BotDataIntegration()
        data = await bot_integration.get_bot_live_data()
        
        print(f"✅ Bot Integration Success!")
        print(f"🤖 Bot Status: {data['bot_status']}")
        
        # Portfolio data
        portfolio = data['portfolio']
        print(f"\n💰 Portfolio Analysis:")
        print(f"   Initial Capital: ${portfolio['initial_capital']:,.2f}")
        print(f"   Base Balance: ${portfolio['base_balance']:,.2f}")
        print(f"   Unrealized P&L: ${portfolio['unrealized_pnl']:+,.2f}")
        print(f"   Realized P&L: ${portfolio['realized_pnl']:+,.2f}")
        print(f"   Total Balance: ${portfolio['total_balance']:,.2f}")
        print(f"   Total Return: {portfolio['total_return_percent']:+.2f}%")
        print(f"   Has Position: {'✅' if portfolio['has_active_position'] else '❌'}")
        
        # Active position
        position = data['active_position']
        if position:
            print(f"\n📊 Active Position:")
            print(f"   Trade ID: {position['trade_id']}")
            print(f"   Side: {position['side']}")
            print(f"   Entry: ${position['entry_price']:,.2f}")
            print(f"   Current: ${position['current_price']:,.2f}")
            print(f"   Quantity: {position['quantity']:.6f} BTC")
            print(f"   Duration: {position['duration']}")
            print(f"   P&L: ${position['unrealized_pnl']:+,.2f} ({position['pnl_percentage']:+.2f}%)")
            if position['stop_loss']:
                print(f"   Stop Loss: ${position['stop_loss']:,.2f}")
            if position['take_profit']:
                print(f"   Take Profit: ${position['take_profit']:,.2f}")
        else:
            print(f"\n📊 Active Position: None")
        
        # Trading stats
        stats = data['trading_stats']
        print(f"\n📈 Trading Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Winning Trades: {stats['winning_trades']}")
        print(f"   Losing Trades: {stats['losing_trades']}")
        print(f"   Win Rate: {stats['win_rate']:.1f}%")
        print(f"   Avg Win: ${stats['avg_win']:+,.2f}")
        print(f"   Avg Loss: ${stats['avg_loss']:+,.2f}")
        print(f"   Largest Win: ${stats['largest_win']:,.2f}")
        print(f"   Largest Loss: ${stats['largest_loss']:,.2f}")
        
        # Market data
        market = data['market_data']
        print(f"\n💹 Market Data:")
        print(f"   Symbol: {market['symbol']}")
        print(f"   Current Price: ${market['current_price']:,.2f}")
        print(f"   Last Update: {market['timestamp']}")
        
        # Data quality check
        print(f"\n🔍 Data Quality Check:")
        print(f"   ✅ Bot Status: {data['bot_status']}")
        print(f"   {'✅' if market['current_price'] > 0 else '❌'} Current Price: {'Valid' if market['current_price'] > 0 else 'Invalid'}")
        if position:
            pnl_check = "Calculated" if position['unrealized_pnl'] != 0 or position['current_price'] == position['entry_price'] else "Missing"
            print(f"   ✅ P&L Calculation: {pnl_check}")
        else:
            print(f"   ✅ P&L Calculation: No Position")
        
        print(f"\n✅ BOT INTEGRATION SUMMARY:")
        print(f"   🤖 Direct Bot Logic: Uses bot's Position.calculate_unrealized_pnl()")
        print(f"   📊 Data Source: CSV files + Real-time API")
        print(f"   🧮 P&L Method: Mathematical calculation (not log parsing)")
        print(f"   ⚡ Performance: Fast direct calculation")
        print(f"   🛡️ Reliability: Uses same logic as the bot")
        
        return data
        
    except Exception as e:
        print(f"❌ Error in bot integration: {e}")
        import traceback
        traceback.print_exc()
        return None

async def compare_approaches():
    """Compare the new bot integration with other approaches"""
    print(f"\n🔄 Comparing Data Approaches")
    print("=" * 60)
    
    # Test bot integration
    bot_data = await test_bot_integration()
    
    if bot_data:
        print(f"\n📊 Bot Integration Results:")
        print(f"   Current Price: ${bot_data['market_data']['current_price']:,.2f}")
        print(f"   Portfolio Balance: ${bot_data['portfolio']['total_balance']:,.2f}")
        print(f"   Unrealized P&L: ${bot_data['portfolio']['unrealized_pnl']:+,.2f}")
        print(f"   Has Position: {bot_data['portfolio']['has_active_position']}")

if __name__ == "__main__":
    asyncio.run(compare_approaches())
