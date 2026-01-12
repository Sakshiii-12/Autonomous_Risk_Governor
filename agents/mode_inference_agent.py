class ModeInferenceAgent:
    """
    Infers trader mode dynamically based on behavior patterns.
    """

    def infer(self, state):
        # High frequency + very short gaps → HFT
        if getattr(state, "trades_last_minute", 0) > 10:
            return "HFT"

        # Large balance + many trades → PROP
        if state.balance > 500_000 and state.trade_count > 20:
            return "PROP"

        # Default
        return "RETAIL"
