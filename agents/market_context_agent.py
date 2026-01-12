import numpy as np

class MarketContextAgent:
    def assess(self, prices):
        if len(prices) < 2:
            return "UNKNOWN", 0.0

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * 100  # %

        if volatility < 0.2:
            regime = "LOW_VOL"
        elif volatility < 0.5:
            regime = "MEDIUM_VOL"
        else:
            regime = "HIGH_VOL"

        return regime, round(volatility, 3)
