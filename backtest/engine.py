import pandas as pd
import matplotlib.pyplot as plt

# Load CSVs
audusd = pd.read_csv("data/AUDUSD_15.csv")
audjpy = pd.read_csv("data/AUDJPY_15.csv")

# Ensure timestamp is comparable
audusd['timestamp'] = pd.to_datetime(audusd['timestamp'])
audjpy['timestamp'] = pd.to_datetime(audjpy['timestamp'])

# Sort just in case
audusd = audusd.sort_values('timestamp')
audjpy = audjpy.sort_values('timestamp')

# ---------- Signal Generator ----------
def generate_signals(df):
    df = df.copy()
    df['momentum'] = df['close'] - df['close'].shift(10)
    df['signal'] = 0
    df.loc[df['momentum'] > 0, 'signal'] = 1   # Long AUDJPY
    df.loc[df['momentum'] < 0, 'signal'] = -1  # Short AUDJPY
    df['signal'] = df['signal'].shift(1)       # Act next bar
    return df[['timestamp', 'signal']]

# ---------- Backtest Function ----------
def backtest(signals, trade_prices):
    merged = pd.merge(signals, trade_prices[['timestamp', 'open', 'close']], on='timestamp')

    # Simulate trade
    merged['entry'] = merged['open'].shift(-1)
    merged['exit'] = merged['close'].shift(-1)

    # Return calc
    merged['pct_return'] = (merged['exit'] - merged['entry']) / merged['entry']
    merged['strategy_return'] = merged['signal'] * merged['pct_return']
    merged = merged.dropna()

    # Equity curve
    merged['equity'] = (1 + merged['strategy_return']).cumprod()

    # Summary
    print(f"\n📊 Final Return: {merged['equity'].iloc[-1] - 1:.2%}")
    print(f"✅ Win Rate: {(merged['strategy_return'] > 0).mean():.2%}")
    print(f"📈 Trades Taken: {merged['signal'].ne(0).sum()}")

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(merged['timestamp'], merged['equity'], label='Equity Curve')
    plt.title("AUDUSD → AUDJPY Strategy")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Save trade log
    merged.to_csv("trade_log.csv", index=False)
    print("💾 Trade log saved to trade_log.csv")

# ---------- Run the Engine ----------
signals = generate_signals(audusd)
backtest(signals, audjpy)
