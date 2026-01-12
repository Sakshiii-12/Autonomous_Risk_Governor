class BehaviorAgent:
    def evaluate(self, state, risk_contract):
        flags = []

        if state.trades_last_minute >= risk_contract.max_trades_per_min:
            flags.append("HFT_BURST")

        if state.consecutive_losses >= risk_contract.max_loss_streak:
            flags.append("REVENGE_TRADING")

        if state.avg_inter_trade_time > 0 and state.avg_inter_trade_time < 0.5:
            flags.append("RUNAWAY_ALGO")

        return flags
