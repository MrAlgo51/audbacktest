# logic/martingale_manager.py

class MartingaleManager:
    def __init__(self, base_size=100, atr_step=0.5, max_tiers=5, timeout_hours=24):
        self.base_size = base_size
        self.atr_step = atr_step
        self.max_tiers = max_tiers
        self.timeout_candles = timeout_hours  # assuming 1H candles
        self.reset()

    def reset(self):
        self.active = False
        self.tiers = []
        self.avg_entry = 0
        self.total_size = 0
        self.entry_index = None

    def start_trade(self, price, index):
        self.reset()
        self.active = True
        self.entry_index = index
        self._add_tier(price)

    def _add_tier(self, price):
        tier_num = len(self.tiers)
        size = self.base_size * (2 ** tier_num)
        self.tiers.append((price, size))
        self.total_size += size
        self.avg_entry = sum(p * s for p, s in self.tiers) / self.total_size

    def check_add_tier(self, price, atr):
        if not self.active or len(self.tiers) >= self.max_tiers:
            return False

        last_entry_price = self.tiers[-1][0]
        threshold = last_entry_price + self.atr_step * atr
        if price > threshold:
            self._add_tier(price)
            return True
        return False

    def check_exit(self, price, vwap, current_index):
        if not self.active:
            return False

        timeout = (current_index - self.entry_index) >= self.timeout_candles
        vwap_reversion = price <= vwap

        return vwap_reversion or timeout

    def get_position_info(self):
        return {
            "active": self.active,
            "tiers": self.tiers,
            "avg_entry": self.avg_entry,
            "total_size": self.total_size,
            "tier_count": len(self.tiers)
        }
