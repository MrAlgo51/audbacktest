import pandas as pd

def run_martingale_backtest(df, starting_balance=1000.0, base_lot=0.1, tp_pips=10, sl_pips=10, max_levels=5):
    pip_value = 0.0001  # For AUD/USD
    balance = starting_balance
    position = None
    entry_price = 0
    lot = base_lot
    trades = 0
    levels = 0

    for i in range(len(df)):
        row = df.iloc[i]
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']

        # === RAM CALC ===
        candle_range = high_price - low_price + 1e-6
        ram = (close_price - open_price) / candle_range

        # === ENTRY CONDITION ===
        if position is None:
            if ram < -0.7:
                position = 'long'
                entry_price = close_price
                lot = base_lot
                levels = 1
                trades += 1
            elif ram > 0.7:
                position = 'short'
                entry_price = close_price
                lot = base_lot
                levels = 1
                trades += 1

        # === EXIT / MARTINGALE LOGIC ===
        elif position == 'long':
            if close_price > entry_price:
                balance += lot * (close_price - entry_price) / pip_value
                position = None
            elif levels < max_levels:
                lot *= 2
                entry_price = close_price
                levels += 1
                trades += 1

        elif position == 'short':
            if close_price < entry_price:
                balance += lot * (entry_price - close_price) / pip_value
                position = None
            elif levels < max_levels:
                lot *= 2
                entry_price = close_price
                levels += 1
                trades += 1

    return {
        "Final Balance": round(balance, 2),
        "Total Trades": trades,
        "Max Levels": max_levels
    }

# Load your data
df = pd.read_csv('data/clean/AUDUSD_1H_202502.csv')

# Debug: Confirm column names
print("Original columns:", df.columns)

# Run backtest
results = run_martingale_backtest(df, tp_pips=10, sl_pips=10)

# Print results
print("Martingale Backtest Results:")
for k, v in results.items():
    print(f"{k}: {v}")
