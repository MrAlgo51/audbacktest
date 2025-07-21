import pandas as pd
import numpy as np
import os

def run_backtest_15min(data_dir, ram_threshold=-1.75, jpy_block_threshold=1.0):
    # Load data
    df_usd = pd.read_csv(os.path.join(data_dir, "AUDUSD_15.csv"))
    df_jpy = pd.read_csv(os.path.join(data_dir, "AUDJPY_15.csv"))

    # Parse timestamps
    df_usd['timestamp'] = pd.to_datetime(df_usd['timestamp'])
    df_jpy['timestamp'] = pd.to_datetime(df_jpy['timestamp'])

    # --- Calculate True ATR ---
    for df in [df_usd, df_jpy]:
        df['hl'] = df['high'] - df['low']
        df['hc'] = (df['high'] - df['close'].shift()).abs()
        df['lc'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['hl', 'hc', 'lc']].max(axis=1)
        df['atr'] = df['tr'].rolling(14).mean()

    # --- RAM Calculation ---
    df_usd['ram'] = (df_usd['close'] - df_usd['close'].rolling(21).mean()) / df_usd['atr']
    df_jpy['ram'] = (df_jpy['close'] - df_jpy['close'].rolling(21).mean()) / df_jpy['atr']

    # --- RAM Z-score ---
    df_usd['ram_z'] = (df_usd['ram'] - df_usd['ram'].rolling(100).mean()) / df_usd['ram'].rolling(100).std()
    df_jpy['ram_z'] = (df_jpy['ram'] - df_jpy['ram'].rolling(100).mean()) / df_jpy['ram'].rolling(100).std()

    # --- RAM Quantile (0–1) ---
    df_usd['ram_q'] = df_usd['ram'].rolling(100).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    df_jpy['ram_q'] = df_jpy['ram'].rolling(100).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)

    # Drop NaNs
    df_usd = df_usd.dropna().reset_index(drop=True)
    df_jpy = df_jpy.dropna().reset_index(drop=True)

    # Merge
    merged = pd.merge(df_usd, df_jpy, on='timestamp', suffixes=('_usd', '_jpy'))

    # --- Backtest Loop ---
    balance = 10000
    lot_size = 10000
    atr_mult_tp = 2.0
    atr_mult_sl = 1.5
    martingale_multiplier = 2
    max_martingale_steps = 5

    position = 0
    entry_price = 0
    tp = sl = 0
    step = 0
    wins = 0
    losses = 0
    equity_curve = []
    drawdowns = []
    levels_used = []
    pnl_by_level = {}
    peak = balance

    for i in range(len(merged)):
        row = merged.iloc[i]
        atr = row['atr_usd']
        price = row['close_usd']
        ram_z = row['ram_z_usd']
        ram_z_jpy = row['ram_z_jpy']
        high = row['high_usd']
        low = row['low_usd']

        if np.isnan(atr) or np.isnan(ram_z) or np.isnan(ram_z_jpy):
            continue

        # ENTRY LOGIC: Fade long if RAM is very low and JPY isn't trending down hard
        if position == 0 and ram_z <= ram_threshold and ram_z_jpy < jpy_block_threshold:
            position = lot_size * (martingale_multiplier ** step)
            entry_price = price
            tp = entry_price + atr * atr_mult_tp
            sl = entry_price - atr * atr_mult_sl

        elif position > 0:
            # Take profit
            if high >= tp:
                profit = (tp - entry_price) * position / tp
                balance += profit
                wins += 1
                pnl_by_level[step] = pnl_by_level.get(step, 0) + profit
                levels_used.append(step)
                step = 0
                position = 0
            # Stop loss
            elif low <= sl:
                loss = (entry_price - sl) * position / sl
                balance -= loss
                pnl_by_level[step] = pnl_by_level.get(step, 0) - loss
                step += 1
                position = 0
                if step > max_martingale_steps:
                    losses += 1
                    levels_used.append(step)
                    step = 0

        equity_curve.append(balance)
        peak = max(peak, balance)
        drawdowns.append((peak - balance) / peak)

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

    return stats


# ---- Grid Test Runner ----
if __name__ == "__main__":
    data_dir = "data"  # Adjust if needed
    ram_range = [-2.0, -1.75, -1.5, -1.25, -1.0]
    jpy_range = [0.25, 0.5, 0.75, 1.0, 1.25]

    for ram in ram_range:
        for jpy in jpy_range:
            result = run_backtest_15min(data_dir, ram_threshold=ram, jpy_block_threshold=jpy)
            print(f"RAM: {ram}, JPY: {jpy} → Final Balance: {result['final_balance']}, "
                  f"Win Rate: {result['win_rate']}%, Trades: {result['total_trades']}, "
                  f"Drawdown: {result['max_drawdown_pct']}%")
