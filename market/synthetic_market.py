import random
import numpy as np

def synthetic_prices(window=20):
    base = 100
    prices = [base]
    for _ in range(window - 1):
        prices.append(prices[-1] * (1 + random.uniform(-0.01, 0.01)))
    return np.array(prices)
