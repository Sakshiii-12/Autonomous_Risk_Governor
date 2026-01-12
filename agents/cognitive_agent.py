class CognitiveAgent:
    def compute(self, state):
        score = 0
        score += state.trades_last_minute * 15
        score += state.consecutive_losses * 25
        return min(score, 100)
