# utils/loader.py

import pandas as pd
import os

def load_clean_csv(pair: str, base_dir: str = "data/clean") -> pd.DataFrame:
    """
    Loads resampled 1H OHLCV data for a given forex pair.

    Args:
        pair (str): Forex pair code, e.g., "AUDUSD" or "AUDJPY"
        base_dir (str): Relative path to the clean data folder

    Returns:
        pd.DataFrame: DataFrame with datetime index and OHLC columns
    """
    filename = f"{pair}_1H_202502.csv"
    filepath = os.path.join(base_dir, filename)
    df = pd.read_csv(filepath, parse_dates=["timestamp"], index_col="timestamp")
    return df
