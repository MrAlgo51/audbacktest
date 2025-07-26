# AUD Backtest Framework

A modular Python backtesting framework for exploring algorithmic trading strategies, with an emphasis on the AUDJPY and AUDUSD currency pairs.

## 🧠 Hypothesis

This project is built around a central hypothesis:

> **AUDJPY functions as a global "risk-on/risk-off" barometer.**  
> During periods of broad market optimism ("risk-on"), the Japanese Yen tends to weaken while the Australian Dollar strengthens, pushing AUDJPY higher.  
> Conversely, in "risk-off" environments, capital flows into safer assets like JPY, driving AUDJPY lower.

By identifying regime shifts in AUDJPY behavior and pairing them with tactical entry/exit logic, this framework aims to exploit short- to medium-term edge through reversion, trend, or volatility strategies.

---

## 📂 Project Structure

<pre>audbacktest/
│
├── backtest/ # Engines, batch runners, sweeper logic
│ ├── engine.py
│ ├── engine_15min.py
│ ├── run_15min_batch.py
│ └── ...
│
├── data/ # Raw and cleaned datasets
│ ├── AUDJPY_15.csv
│ └── clean/
│ └── AUDJPY_1H_202502.csv
│
├── indicators/ # Custom indicators
│ ├── atr.py
│ ├── ram_ema_reversion.py
│ └── rsi.py
│
├── logic/ # Entry and risk logic modules
│ ├── entry_logic.py
│ └── martingale_manager.py
│
├── utils/ # Data loaders and helpers
│ └── loader.py
│
├── main.py # Top-level test or run script
├── run_test.py # Shortcut runner for single config
└── sweep_results.csv # Batch test output (ignored by .gitignore)</pre>
📬 Contributing
This project is under active development.
Pull requests, issues, and ideas welcome — especially from traders with macro, FX, or volatility experience.

🧠 Future Work
Add regime classifier (risk-on vs risk-off) using volatility and macro triggers

Integrate with broker APIs or paper trading layer

Build a Discord/Telegram alert bot for real-time signal generation

📜 License
MIT License — do what you want, no guarantees
