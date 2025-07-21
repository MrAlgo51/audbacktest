import pandas as pd
import numpy as np
import os

def run_backtest_audusd(data_dir, risk_per_trade=100, max_steps=3):
    # Load data
    df_usd = pd.read_csv(os.path.join(data_dir, "AUDUSD_15.csv"), parse_dates=['timestamp'])
    df_jpy = pd.read_csv(os.path.join(data_dir, "AUDJPY_15.csv"), parse_dates=['timestamp'])

    # Keep only needed columns
    df_usd = df_usd[['timestamp', 'open', 'high', 'low', 'close']].copy()
    df_jpy = df_jpy[['timestamp', 'close']].rename(columns={'close': 'jpy_close'}).copy()

    # Merge on timestamp
    df = df_usd.merge(df_jpy, on='timestamp', how='inner')

    # --- True ATR (Wilder-style) ---
    df['hl'] = df['high'] - df['low']
    df['hc'] = (df['high'] - df['close'].shift()).abs()
    df['lc'] = (df['low'] - df['close'].shift()).abs()
    df['tr'] = df[['hl', 'hc', 'lc']].max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()

    # --- AUDUSD RAM + z-score ---
    df['ram'] = (df['close'] - df['close'].rolling(21).mean()) / df['atr']
    df['ram_z'] = (df['ram'] - df['ram'].rolling(100).mean()) / df['ram'].rolling(100).std()

    # --- AUDJPY RAM ---
    df['jpy_mean'] = df['jpy_close'].rolling(21).mean()
    df['jpy_atr'] = df['jpy_close'].rolling(14).apply(lambda x: x.max() - x.min(), raw=True)
    df['jpy_ram'] = (df['jpy_close'] - df['jpy_mean']) / df['jpy_atr']
    df['jpy_ram_z'] = (df['jpy_ram'] - df['jpy_ram'].rolling(100).mean()) / df['jpy_ram'].rolling(100).std()

    # Clean
    df = df.dropna().reset_index(drop=True)

    # --- Strategy Parameters ---
    ram_z_threshold = -1.5
    jpy_block_threshold = 1.0
    balance = 10000
    trades = []
    i = 0

    while i < len(df):
        row = df.iloc[i]
        if row['ram_z'] <= ram_z_threshold and row['jpy_ram_z'] < jpy_block_threshold:
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
                    high = df.iloc[j]['high']
                    low = df.iloc[j]['low']
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

    # --- Stats ---
    df_trades = pd.DataFrame(trades)
    if not df_trades.empty:
        win_rate = df_trades[df_trades['result'] == 'win'].shape[0] / len(df_trades)
        max_dd = 1 - df_trades['balance'].min() / 10000
    else:
        win_rate, max_dd = 0.0, 0.0

    print(f"Final Balance: {balance:.2f}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Max Drawdown: {max_dd:.2%}")
    return balance, win_rate, max_dd, df_trades
