from utils.loader import load_clean_csv
from indicators.atr import calculate_atr
from indicators.rsi import calculate_rsi
from indicators.ram_ema_reversion import ram_ema_reversion

# Load and preprocess AUDUSD data
df = load_clean_csv("AUDUSD")
df["ATR_14"] = calculate_atr(df)
df["RSI_14"] = calculate_rsi(df)
df["VWAP_24"] = df["close"].rolling(window=24).mean()  # Just a moving average placeholder

# Run RAM + EMA reversion signal logic
df = ram_ema_reversion(df)

# View final signals and data
print(df[['close', 'long_signal', 'short_signal']].tail(20))
print(df.tail())
