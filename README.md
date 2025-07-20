# audbacktest

Backtesting framework for evaluating 15-minute martingale strategies on AUD pairs.

## Structure

- `backtest/`: Core backtest engines and batch runners
- `data/`: Historical price data and cleaned sets
- `indicators/`: Custom technical indicators
- `logic/`: Entry logic and martingale manager
- `utils/`: Loaders and support utilities

## Usage

```bash
python run_test.py


python backtest/run_15min_batch.py


---

### 🔹 3. Add `requirements.txt` (optional)

Want to track dependencies? If so:

```powershell
pip freeze > requirements.txt

