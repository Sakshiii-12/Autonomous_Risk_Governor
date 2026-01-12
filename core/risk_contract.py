class RiskContract:
    def __init__(self, max_trades_per_min=5, max_loss_streak=2):
        self.max_trades_per_min = max_trades_per_min
        self.max_loss_streak = max_loss_streak
