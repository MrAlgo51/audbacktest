# backtest/15min_test_engine.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine_15min import run_backtest_audusd  # <-- adjust as needed

if __name__ == "__main__":
    # Path to folder, not a single file!
    data_dir = os.path.join("data")

    run_backtest_audusd(data_dir)
