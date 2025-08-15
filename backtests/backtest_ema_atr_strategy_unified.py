DOC_FILE = "doc/EMA_ATR_Strategy_Unified_Documentation.md"

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from config import BACKTEST_DATA_FILE, STRATEGY_VERSION
from strategies.ema_atr_strategy_unified import calculate_indicators, backtest_strategy


def load_backtest_data():
    df = pd.read_csv(BACKTEST_DATA_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    print(f"\u2705 Data loaded: {len(df)} records from {df.index.min()} to {df.index.max()}")
    print(f"\U0001F4B0 Price range: ${df['Close'].min():,.2f} - ${df['Close'].max():,.2f}")
    return df

def print_performance_summary(trades_df, df):
    if len(trades_df) == 0:
        print("No trades executed.")
        return
    from config import PAPER_TRADING_CAPITAL
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    losing_trades = len(trades_df[trades_df['pnl'] < 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = trades_df['pnl'].sum()
    avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    final_capital = PAPER_TRADING_CAPITAL + total_pnl
    total_return = (final_capital / PAPER_TRADING_CAPITAL - 1) * 100 if PAPER_TRADING_CAPITAL != 0 else 0
    running_max = df['Portfolio_Value'].cummax()
    drawdowns = (running_max - df['Portfolio_Value']) / running_max
    max_drawdown = drawdowns.max() * 100 if not drawdowns.empty else 0
    avg_duration = trades_df['duration_hours'].mean()
    print(f"\n📊 STRATEGY PERFORMANCE ANALYSIS ({STRATEGY_VERSION})")
    print("=" * 60)
    print(f"💰 TRADING RESULTS:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Winning Trades: {winning_trades}")
    print(f"   Losing Trades: {losing_trades}")
    print(f"   Win Rate: {win_rate:.2f}%")
    print(f"\n💵 PROFIT & LOSS:")
    print(f"   Total P&L: ${total_pnl:,.2f}")
    print(f"   Average Win: ${avg_win:,.2f}")
    print(f"   Average Loss: ${avg_loss:,.2f}")
    print(f"   Profit Factor: {abs(avg_win / avg_loss):.2f}" if avg_loss != 0 else "N/A")
    print(f"\n📈 PORTFOLIO METRICS:")
    print(f"   Initial Capital: ${PAPER_TRADING_CAPITAL:,.2f}")
    print(f"   Final Capital: ${final_capital:,.2f}")
    print(f"   Total Return: {total_return:+.2f}%")
    print(f"   Max Drawdown: {max_drawdown:.2f}%")
    print(f"\n⏱️ TIME ANALYSIS:")
    print(f"   Average Trade Duration: {avg_duration:.1f} hours")
    print(f"   Backtest Period: {df.index.min()} to {df.index.max()}")
    exit_reasons = trades_df['exit_reason'].value_counts()
    print(f"\n🎯 EXIT ANALYSIS:")
    for reason, count in exit_reasons.items():
        print(f"   {reason}: {count} trades ({count/total_trades*100:.1f}%)")
    print(f"\n📄 Strategy Documentation: {DOC_FILE}")


def main():
    df = load_backtest_data()
    df = calculate_indicators(df)
    trades, df = backtest_strategy(df)
    trades_df = pd.DataFrame(trades)
    print_performance_summary(trades_df, df)
    # Save detailed results
    import os
    from datetime import datetime
    os.makedirs('data/ema_atr_strategy', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trades_csv = f"data/ema_atr_strategy/trades_1h_{timestamp}_{STRATEGY_VERSION}.csv"
    trades_df.to_csv(trades_csv, index=False)
    print(f"\n✅ Trades saved to {trades_csv}")

if __name__ == "__main__":
    main()
