import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Load Data ===
df = pd.read_csv('data/clean/AUDUSD_1H_202502.csv')
df_jpy = pd.read_csv('data/clean/AUDJPY_1H_202502.csv')

# === Indicators ===
def calculate_atr(data, period=14):
    data['H-L'] = data['high'] - data['low']
    data['H-PC'] = np.abs(data['high'] - data['close'].shift(1))
    data['L-PC'] = np.abs(data['low'] - data['close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    return data.drop(columns=['H-L', 'H-PC', 'L-PC', 'TR'])

df = calculate_atr(df)
df_jpy = calculate_atr(df_jpy)

df['mean'] = df['close'].rolling(window=20).mean()
df['ram'] = (df['close'] - df['mean']) / df['ATR']

df_jpy['mean'] = df_jpy['close'].rolling(window=20).mean()
df_jpy['ram'] = (df_jpy['close'] - df_jpy['mean']) / df_jpy['ATR']

# === Backtest Parameters ===
initial_balance = 10000
balance = initial_balance
position = 0
entry_price = 0
lot_size = 10000
atr_mult_tp = 2.0
atr_mult_sl = 1.5
martingale_multiplier = 2
max_martingale_steps = 5
ram_threshold = -1.5  # Entry trigger on AUD/USD RAM
jpy_block_threshold = 1.0  # Block entries if AUD/JPY RAM exceeds this
step = 0
last_balance = balance

# === Diagnostics ===
equity_curve = []
trade_sequences = 0
wins = 0
losses = 0
levels_used = []
pnl_by_level = {}
peak = balance
drawdowns = []

# === Backtest Loop ===
for i in range(20, min(len(df), len(df_jpy))):
    atr = df['ATR'].iloc[i]
    price = df['close'].iloc[i]
    ram = df['ram'].iloc[i]
    ram_jpy = df_jpy['ram'].iloc[i]
    if np.isnan(atr) or np.isnan(ram) or np.isnan(ram_jpy):
        continue

    # === Entry Logic with Filter ===
    if position == 0 and ram < ram_threshold and abs(ram_jpy) < jpy_block_threshold:
        trade_sequences += 1
        position = lot_size * (martingale_multiplier ** step)
        entry_price = price
        tp = entry_price + atr * atr_mult_tp
        sl = entry_price - atr * atr_mult_sl
        print(f"BUY @ {entry_price:.5f} | TP: {tp:.5f}, SL: {sl:.5f}, Step: {step}, Size: {position}")
        continue

    # === Exit Logic ===
    if position > 0:
        if price >= tp:
            profit = (tp - entry_price) * position / price
            balance += profit
            wins += 1
            levels_used.append(step)
            pnl_by_level[step] = pnl_by_level.get(step, 0) + profit
            print(f"TP Hit. +{profit:.2f}, Bal: {balance:.2f}")
            position = 0
            step = 0
        elif price <= sl:
            loss = (entry_price - sl) * position / price
            balance -= loss
            pnl_by_level[step] = pnl_by_level.get(step, 0) - loss
            print(f"SL Hit. -{loss:.2f}, Bal: {balance:.2f}")
            position = 0
            step += 1
            if step > max_martingale_steps:
                losses += 1
                print("Max martingale steps hit — reset.")
                levels_used.append(step)
                step = 0

    equity_curve.append(balance)
    peak = max(peak, balance)
    drawdown = (peak - balance) / peak
    drawdowns.append(drawdown)

# === Final Stats ===
total_trades = wins + losses
avg_levels = np.mean(levels_used) if levels_used else 0
max_dd = max(drawdowns) * 100 if drawdowns else 0

print("\n--- Performance Stats ---")
print(f"Final Balance: ${balance:.2f}")
print(f"Total Trades: {total_trades}")
print(f"Win Rate: {100 * wins / total_trades:.2f}%")
print(f"Avg Martingale Levels Used: {avg_levels:.2f}")
print(f"Max Drawdown: {max_dd:.2f}%")
print(f"P&L by Martingale Step:")
for lvl, val in pnl_by_level.items():
    print(f"  Level {lvl}: {val:.2f}")

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(equity_curve)
plt.title('Equity Curve (RAM + AUD/JPY Filter)')
plt.xlabel('Trades')
plt.ylabel('Balance')
plt.grid()
plt.tight_layout()
plt.show()
