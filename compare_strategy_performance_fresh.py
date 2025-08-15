import pandas as pd
import matplotlib.pyplot as plt
import os

def load_trades(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"File not found: {file_path}")
        return None

def analyze_trades(trades):
    if trades is None or trades.empty:
        return {'total': 0, 'win_rate': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0, 'total_pnl': 0.0, 'pf': 0.0, 'max_dd': 0.0, 'sharpe': 0.0, 'equity': pd.Series(dtype=float)}
    wins = trades[trades['pnl'] > 0]
    losses = trades[trades['pnl'] < 0]
    total = len(trades)
    win_rate = (len(wins) / total) * 100 if total > 0 else 0
    avg_win = wins['pnl'].mean() if not wins.empty else 0
    avg_loss = losses['pnl'].mean() if not losses.empty else 0
    total_pnl = trades['pnl'].sum()
    pf = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    equity = trades['pnl'].cumsum()
    running_max = equity.cummax()
    drawdown = (running_max - equity)
    max_dd = drawdown.max() if not drawdown.empty else 0
    sharpe = (trades['pnl'].mean() / trades['pnl'].std()) * (252 ** 0.5) if trades['pnl'].std() != 0 else 0
    return {
        'total': total,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'total_pnl': total_pnl,
        'pf': pf,
        'max_dd': max_dd,
        'sharpe': sharpe,
        'equity': equity
    }

def print_stats(label, stats):
    print(f"\n--- {label} ---")
    print(f"Total Trades: {stats['total']}")
    print(f"Win Rate: {stats['win_rate']:.2f}%")
    print(f"Average Win: {stats['avg_win']:.2f}")
    print(f"Average Loss: {stats['avg_loss']:.2f}")
    print(f"Total P&L: {stats['total_pnl']:.2f}")
    print(f"Profit Factor: {stats['pf']:.2f}")
    print(f"Max Drawdown: {stats['max_dd']:.2f}")
    print(f"Sharpe Ratio: {stats['sharpe']:.2f}")

def main():
    files = {
        'v1': 'data/ema_atr_strategy/trades_1h_20250815_174908_v1.csv',
        'v2': 'data/ema_atr_strategy/trades_1h_20250815_174919_v2.csv',
        'v3': 'data/ema_atr_strategy/trades_1h_20250815_174933_v3.csv',
    }
    results = {}
    for label, path in files.items():
        trades = load_trades(path)
        stats = analyze_trades(trades)
        print_stats(f"Strategy {label}", stats)
        results[label] = stats
    # Plot equity curves
    plt.figure(figsize=(12, 6))
    for label, stats in results.items():
        if not stats['equity'].empty:
            plt.plot(stats['equity'].reset_index(drop=True), label=label)
    plt.title('Equity Curve Comparison')
    plt.xlabel('Trade Number')
    plt.ylabel('Cumulative P&L')
    plt.legend()
    plt.tight_layout()
    plt.show()
    # Print best strategy
    best = max(results, key=lambda k: results[k]['total_pnl'])
    print(f"\nBest strategy by total P&L: {best.upper()} (${results[best]['total_pnl']:.2f})")

if __name__ == "__main__":
    main()
