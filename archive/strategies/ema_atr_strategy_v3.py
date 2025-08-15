import pandas as pd
from config import ATR_PERIOD, EMA_SHORT, EMA_LONG, ATR_MULTIPLIER, RISK_REWARD_RATIO, TRAILING_SL, PAPER_TRADING_CAPITAL

def calculate_indicators_v3(df):
    df['EMA9'] = df['Close'].ewm(span=EMA_SHORT).mean()
    df['EMA20'] = df['Close'].ewm(span=EMA_LONG).mean()
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = abs(df['High'] - df['Close'].shift(1))
    df['TR3'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df['ATR'] = df['TR'].rolling(ATR_PERIOD).mean()
    df.drop(['TR1', 'TR2', 'TR3', 'TR'], axis=1, inplace=True)
    return df

def find_swing_points_v3(df, window=2):
    df['SwingHigh'] = df['High'].rolling(window=window*2+1, center=True).max()
    df['SwingLow'] = df['Low'].rolling(window=window*2+1, center=True).min()
    df['IsSwingHigh'] = (df['High'] == df['SwingHigh'])
    df['IsSwingLow'] = (df['Low'] == df['SwingLow'])
    return df

def get_recent_swing_low_v3(df, current_idx, lookback=10):
    start_idx = max(0, current_idx - lookback)
    recent_data = df.iloc[start_idx:current_idx+1]
    return recent_data['Low'].min()

def get_recent_swing_high_v3(df, current_idx, lookback=10):
    start_idx = max(0, current_idx - lookback)
    recent_data = df.iloc[start_idx:current_idx+1]
    return recent_data['High'].max()

def backtest_strategy_v3(df):
    trades = []
    position = None
    capital = PAPER_TRADING_CAPITAL
    df['Portfolio_Value'] = float(PAPER_TRADING_CAPITAL)
    for i in range(max(ATR_PERIOD, EMA_LONG) + 5, len(df)):
        current_price = df['Close'].iloc[i]
        current_time = df.index[i]
        if position is None:
            if (df['EMA9'].iloc[i] > df['EMA20'].iloc[i] and df['Close'].iloc[i] > df['EMA9'].iloc[i] and not pd.isna(df['ATR'].iloc[i])):
                swing_low = get_recent_swing_low_v3(df, i)
                sl = swing_low - ATR_MULTIPLIER * df['ATR'].iloc[i]
                risk = current_price - sl
                tp = current_price + (risk * RISK_REWARD_RATIO)
                risk_amount = capital * 0.02
                position_size = risk_amount / risk if risk > 0 else 0
                if position_size > 0:
                    position = {
                        'type': 'long',
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'entry_index': i,
                        'sl': sl,
                        'tp': tp,
                        'size': position_size,
                        'initial_sl': sl
                    }
            elif (df['EMA9'].iloc[i] < df['EMA20'].iloc[i] and df['Close'].iloc[i] < df['EMA9'].iloc[i] and not pd.isna(df['ATR'].iloc[i])):
                swing_high = get_recent_swing_high_v3(df, i)
                sl = swing_high + ATR_MULTIPLIER * df['ATR'].iloc[i]
                risk = sl - current_price
                tp = current_price - (risk * RISK_REWARD_RATIO)
                risk_amount = capital * 0.02
                position_size = risk_amount / risk if risk > 0 else 0
                if position_size > 0:
                    position = {
                        'type': 'short',
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'entry_index': i,
                        'sl': sl,
                        'tp': tp,
                        'size': position_size,
                        'initial_sl': sl
                    }
        else:
            if TRAILING_SL:
                if position['type'] == 'long':
                    new_sl = max(position['sl'], df['EMA9'].iloc[i])
                    position['sl'] = new_sl
                else:
                    new_sl = min(position['sl'], df['EMA20'].iloc[i])
                    position['sl'] = new_sl
            exit_reason = None
            exit_price = current_price
            if position['type'] == 'long':
                if current_price <= position['sl']:
                    exit_reason = 'Stop Loss'
                    exit_price = position['sl']
                elif current_price >= position['tp']:
                    exit_reason = 'Take Profit'
                    exit_price = position['tp']
            else:
                if current_price >= position['sl']:
                    exit_reason = 'Stop Loss'
                    exit_price = position['sl']
                elif current_price <= position['tp']:
                    exit_reason = 'Take Profit'
                    exit_price = position['tp']
            if exit_reason:
                if position['type'] == 'long':
                    pnl = (exit_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - exit_price) * position['size']
                capital += pnl
                trade_record = {
                    'entry_time': position['entry_time'],
                    'exit_time': current_time,
                    'type': position['type'],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'size': position['size'],
                    'pnl': pnl,
                    'exit_reason': exit_reason,
                    'duration_hours': (current_time - position['entry_time']).total_seconds() / 3600
                }
                trades.append(trade_record)
                position = None
        if position:
            if position['type'] == 'long':
                unrealized_pnl = (current_price - position['entry_price']) * position['size']
            else:
                unrealized_pnl = (position['entry_price'] - current_price) * position['size']
            df.loc[df.index[i], 'Portfolio_Value'] = capital + unrealized_pnl
        else:
            df.loc[df.index[i], 'Portfolio_Value'] = capital
    return trades, df

def analyze_results_v3(trades, df):
    if not trades:
        return pd.DataFrame()
    trades_df = pd.DataFrame(trades)
    trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
    return trades_df
