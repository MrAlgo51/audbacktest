import pandas as pd

def run_backtest(filename, symbol, sl_pips, tp_pips, rsi_buy, rsi_sell):
    print(f"Loading data from {filename} for symbol {symbol}...")

    try:
        df = pd.read_csv(filename, parse_dates=["timestamp"])
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    df = df.sort_values("timestamp").reset_index(drop=True)

    # Basic RSI calculation
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    position = None
    entry_price = 0
    wins = 0
    losses = 0
    total = 0

    for i in range(15, len(df)):
        price = df.loc[i, "close"]
        rsi = df.loc[i, "rsi"]

        if position is None:
            if rsi < rsi_buy:
                position = "long"
                entry_price = price
                entry_index = i
            elif rsi > rsi_sell:
                position = "short"
                entry_price = price
                entry_index = i

        elif position == "long":
            if price - entry_price >= tp_pips * 0.0001:
                wins += 1
                position = None
            elif entry_price - price >= sl_pips * 0.0001:
                losses += 1
                position = None

        elif position == "short":
            if entry_price - price >= tp_pips * 0.0001:
                wins += 1
                position = None
            elif price - entry_price >= sl_pips * 0.0001:
                losses += 1
                position = None

        if position is None:
            total += 1

    print(f"Total trades: {total}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    if total > 0:
        win_rate = wins / total * 100
        print(f"Win rate: {win_rate:.2f}%")
    else:
        print("No trades were made.")

