# backtest/sweeper.py

import numpy as np
from engine import run_backtest  # assumes engine.py exposes a run_backtest() function
import pandas as pd

ram_thresholds = np.round(np.arange(-3.0, 2.1, 0.25), 2)  # From -3.0 to +2.0
jpy_block_threshold = 1.0  # You can make this a sweepable param later

results = []

for ram in ram_thresholds:
    stats, logs = run_backtest(ram_threshold=ram, jpy_block_threshold=jpy_block_threshold)
    
    results.append({
        "ram_threshold": ram,
        "final_balance": float(stats['final_balance']),
        "total_trades": stats['total_trades'],
        "win_rate": stats['win_rate'],
        "max_drawdown_pct": float(stats['max_drawdown_pct']),
        "avg_martingale_level": float(stats['avg_martingale_level'])
    })

df = pd.DataFrame(results)
df.to_csv("sweep_results.csv", index=False)
print(df)

