import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def calculate_atr(data, period=14):
    data['H-L'] = data['high'] - data['low']
    data['H-PC'] = np.abs(data['high'] - data['close'].shift(1))
    data['L-PC'] = np.abs(data['low'] - data['close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    return data.drop(columns=['H-L', 'H-PC', 'L-PC', 'TR'])

def run_backtest(ram_threshold=-1.75, jpy_block_threshold=1.0, show_plot=False):
    df = pd.read_csv('data/clean/AUDUSD_1H_202502.csv')
    df_jpy = pd.read_csv('data/clean/AUDJPY_1H_202502.csv')

    df = calculate_atr(df)
    df_jpy = calculate_atr(df_jpy)

    df['mean'] = df['close'].rolling(window=20).mean()
    df['ram'] = (df['close'] - df['mean']) / df['ATR']

    df_jpy['mean'] = df_jpy['close'].rolling(window=20).mean()
    df_jpy['ram'] = (df_jpy['close'] - df_jpy['mean']) / df_jpy['ATR']

    initial_balance = 10000
    balance = initial_balance
    position = 0
    entry_price = 0
    lot_size = 10000
    atr_mult_tp = 2.0
    atr_mult_sl = 1.5
    martingale_multiplier = 2
    max_martingale_steps = 5
    step = 0

    equity_curve = []
    trade_sequences = 0
    wins = 0
    losses = 0
    levels_used = []
    pnl_by_level = {}
    peak = balance
    drawdowns = []
    entry_logs = []

    for i in range(20, min(len(df), len(df_jpy))):
        atr = df['ATR'].iloc[i]
        price = df['close'].iloc[i]
        ram = df['ram'].iloc[i]
        ram_jpy = df_jpy['ram'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        timestamp = df['timestamp'].iloc[i] if 'timestamp' in df.columns else f"index_{i}"

        if np.isnan(atr) or np.isnan(ram) or np.isnan(ram_jpy):
            continue

        if position == 0 and ram < ram_threshold and abs(ram_jpy) < jpy_block_threshold:
            trade_sequences += 1
            position = lot_size * (martingale_multiplier ** step)
            entry_price = price
            tp = entry_price + atr * atr_mult_tp
            sl = entry_price - atr * atr_mult_sl

            entry_logs.append({
                'timestamp': timestamp,
                'price': price,
                'ram': ram,
                'ram_jpy': ram_jpy,
                'level': step,
                'balance_before': balance
            })
        elif position > 0:
            if high >= tp:
                profit = (tp - entry_price) * position / tp
                balance += profit
                wins += 1
                levels_used.append(step)
                pnl_by_level[step] = pnl_by_level.get(step, 0) + profit
                position = 0
                step = 0
            elif low <= sl:
                loss = (entry_price - sl) * position / sl
                balance -= loss
                pnl_by_level[step] = pnl_by_level.get(step, 0) - loss
                position = 0
                step += 1

                if step > max_martingale_steps:
                    losses += 1
                    levels_used.append(step)
                    step = 0

        equity_curve.append(balance)
        peak = max(peak, balance)
        drawdown = (peak - balance) / peak
        drawdowns.append(drawdown)

    total_trades = wins + losses
    avg_levels = np.mean(levels_used) if levels_used else 0
    max_dd = max(drawdowns) * 100 if drawdowns else 0

    stats = {
        'ram_threshold': ram_threshold,
        'jpy_block_threshold': jpy_block_threshold,
        'final_balance': round(balance, 2),
        'total_trades': total_trades,
        'win_rate': round(100 * wins / total_trades, 2) if total_trades else 0,
        'avg_martingale_level': round(avg_levels, 2),
        'max_drawdown_pct': round(max_dd, 2),
        'pnl_by_level': pnl_by_level
    }

    if show_plot:
        plt.figure(figsize=(10, 5))
        plt.plot(equity_curve)
        plt.title('Equity Curve')
        plt.xlabel('Bars')
        plt.ylabel('Balance')
        plt.grid()
        plt.tight_layout()
        plt.show()

    return stats, entry_logs

if __name__ == "__main__":
    ram_range = [-2.0, -1.75, -1.5, -1.25, -1.0]
    jpy_range = [0.25, 0.5, 0.75, 1.0, 1.25]

    for ram in ram_range:
        for jpy in jpy_range:
            result, logs = run_backtest(ram_threshold=ram, jpy_block_threshold=jpy, show_plot=False)

            print(f"RAM: {ram}, JPY: {jpy} → Final Balance: {result['final_balance']}, "
                  f"Win Rate: {result['win_rate']}%, Trades: {result['total_trades']}, "
                  f"Drawdown: {result['max_drawdown_pct']}%")
