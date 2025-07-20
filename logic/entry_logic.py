# logic/entry_logic.py

import pandas as pd

def generate_signals(df: pd.DataFrame, atr_col="ATR_14", rsi_col="RSI_14", vwap_col="VWAP_24", atr_multiplier=1.5, rsi_threshold=80) -> pd.Series:
    """
    Generate entry signals based on price being stretched above VWAP and RSI overbought.

    Args:
        df (pd.DataFrame): DataFrame with columns ['close', atr_col, rsi_col, vwap_col]
        atr_col (str): Name of ATR column
        rsi_col (str): Name of RSI column
        vwap_col (str): Name of VWAP column
        atr_multiplier (float): How far price must be from VWAP in ATRs
        rsi_threshold (float): RSI value that must be exceeded

    Returns:
        pd.Series: Boolean Series of entry signals (True = signal)
    """
    atr = df[atr_col]
    vwap = df[vwap_col]
    rsi = df[rsi_col]
    price = df["close"]

    stretched = price > (vwap + atr * atr_multiplier)
    overheated = rsi > rsi_threshold

    return stretched & overheated
