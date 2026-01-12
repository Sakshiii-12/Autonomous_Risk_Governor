class RiskGovernor:
    def decide(self, flags, cognitive, state, policy_signal, market_regime):

        # Cooldown always wins
        if state.in_cooldown():
            return "HARD_BLOCK"

        # ================= MODE-BASED LOGIC =================

        if state.mode == "HFT":
            # HFT tolerates frequency, but not runaway
            if "RUNAWAY_ALGO" in flags:
                return "HARD_BLOCK"
            if cognitive >= 90:
                return "SOFT_DELAY"
            return "ALLOW"

        if state.mode == "PROP":
            # Prop traders tolerate frequency, not drawdown
            if state.consecutive_losses >= 3:
                return "HARD_BLOCK"
            if cognitive >= 80:
                return "SOFT_DELAY"
            return "ALLOW"

        # Default: RETAIL
        if market_regime == "HIGH_VOL" and cognitive > 50:
            return "SOFT_DELAY"

        if "HFT_BURST" in flags and cognitive > 70:
            return "SOFT_DELAY"

        if cognitive >= 90:
            return "HARD_BLOCK"

        if cognitive >= 60:
            return "SOFT_DELAY"

        return "ALLOW"
