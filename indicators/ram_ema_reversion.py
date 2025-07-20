import pandas as pd
import numpy as np

def ram_ema_reversion(df, ema_period=20, atr_period=14, atr_mult=1.5, ram_period=50):
    """
    Detects long/short signals based on RAM + EMA Band reversion logic.

    Params:
        df (pd.DataFrame): OHLCV data with ['open', 'high', 'low', 'close']
        ema_period (int): EMA window size
        atr_period (int): ATR window size for bands
        atr_mult (float): Band multiplier
        ram_period (int): Rolling average mean window

    Returns:
        df (pd.DataFrame): With 'long_signal' and 'short_signal' columns added
    """
    df = df.copy()

    # EMA
    df['ema'] = df['close'].ewm(span=ema_period, adjust=False).mean()

    # ATR
    df['tr'] = np.maximum(df['high'] - df['low'],
                          np.maximum(abs(df['high'] - df['close'].shift()),
                                     abs(df['low'] - df['close'].shift())))
    df['atr'] = df['tr'].rolling(window=atr_period).mean()

    # EMA bands
    df['upper_band'] = df['ema'] + (atr_mult * df['atr'])
    df['lower_band'] = df['ema'] - (atr_mult * df['atr'])

    # RAM (Rolling Average Mean of Close)
    df['ram'] = df['close'].rolling(window=ram_period).mean()

    # Signal conditions
    df['long_signal'] = (df['close'] < df['lower_band']) & (df['close'] < df['ram'])
    df['short_signal'] = (df['close'] > df['upper_band']) & (df['close'] > df['ram'])

    return df
