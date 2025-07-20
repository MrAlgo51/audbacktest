# indicators/rsi.py

import pandas as pd
import numpy as np

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        df (pd.DataFrame): Must contain 'close' column.
        period (int): RSI period (default is 14)

    Returns:
        pd.Series: RSI values
    """
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain, index=df.index).rolling(window=period).mean()
    avg_loss = pd.Series(loss, index=df.index).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
