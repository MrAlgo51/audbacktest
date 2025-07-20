import pandas as pd
import numpy as np

def run_backtest_audusd(data_dir, risk_per_trade=100, max_steps=3):
    # Load data with datetime parsing
    df = pd.read_csv(f"{data_dir}/AUDUSD_15.csv", parse_dates=['timestamp'])
    df_jpy = pd.read_csv(f"{data_dir}/AUDJPY_15.csv", parse_dates=['timestamp'])

    # Align dataframes on timestamp
    df = df[['timestamp', 'open', 'high', 'low', 'close']].copy()
    df_jpy = df_jpy[['timestamp', 'close']].copy()
    df_jpy.rename(columns={'close': 'jpy_close'}, inplace=True)
    df = df.merge(df_jpy, on='timestamp', how='inner')

    # Calculate RAM (Relative ATR Mean) for AUDUSD
    df['atr'] = df['high'].rolling(14).max() - df['low'].rolling(14).min()
    df['mean'] = df['close'].rolling(14).mean()
    df['ram'] = (df['close'] - df['mean']) / df['atr']

    # RAM for JPY (based on its close)
    df['jpy_mean'] = df['jpy_close'].rolling(14).mean()
    df['jpy_atr'] = df['jpy_close'].rolling(14).max() - df['jpy_close'].rolling(14).min()
    df['jpy_ram'] = (df['jpy_close'] - df['jpy_mean']) / df['jpy_atr']

    df = df.dropna()

    # Parameters
    ram_threshold = 0.5
    jpy_block_threshold = 0.5
    balance = 10000
    trades = []

    i = 0
    while i < len(df):
        row = df.iloc[i]
        if row['ram'] < ram_threshold and row['jpy_ram'] < jpy_block_threshold:
            step = 0
            entry_price = row['close']
            atr = row['atr']
            sl = entry_price - atr * 1.0
            tp = entry_price + atr * 1.5

            while step < max_steps and i < len(df) - 1:
                risk_amount = risk_per_trade * (step + 1)
                size = risk_amount / (entry_price - sl)
                j = i + 1
                trade_result = None

                while j < len(df):
                    low = df.iloc[j]['low']
                    high = df.iloc[j]['high']
                    if low <= sl:
                        balance -= risk_amount
                        trade_result = 'loss'
                        break
                    elif high >= tp:
                        gain = (tp - entry_price) * size
                        balance += gain
                        trade_result = 'win'
                        break
                    j += 1

                trades.append({
                    'entry_time': df.iloc[i]['timestamp'],
                    'exit_time': df.iloc[j]['timestamp'] if j < len(df) else None,
                    'step': step,
                    'result': trade_result,
                    'balance': balance
                })

                if trade_result == 'win':
                    i = j
                    break
                else:
                    step += 1
                    i = j
                    if i >= len(df):
                        break
                    entry_price = df.iloc[i]['close']
                    atr = df.iloc[i]['atr']
                    sl = entry_price - atr * 1.0
                    tp = entry_price + atr * 1.5
        else:
            i += 1

    # Final analysis
    df_trades = pd.DataFrame(trades)
    if not df_trades.empty:
        win_rate = df_trades[df_trades['result'] == 'win'].shape[0] / len(df_trades)
        max_dd = 1 - df_trades['balance'].min() / 10000
    else:
        win_rate, max_dd = 0, 0

    print(f"Final Balance: {balance:.2f}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Max Drawdown: {max_dd:.2%}")
    return balance, win_rate, max_dd, df_trades
