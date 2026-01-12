from dataclasses import dataclass
import time

@dataclass
class TraderState:
    balance: float
    open_position: float
    last_trade_time: float
    consecutive_losses: int
    trade_count: int

    # --- HFT / temporal ---
    trades_last_minute: int = 0
    avg_inter_trade_time: float = 0.0

    # --- Autonomy ---
    cooldown_until: float = 0.0
    last_intervention: str = "NONE"

    mode: str = "RETAIL"   # RETAIL | HFT | PROP
    
    risk_tolerance: str = "medium"

    def in_cooldown(self):
        return time.time() < self.cooldown_until
