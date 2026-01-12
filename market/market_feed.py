import yfinance as yf
import numpy as np

class MarketFeed:
    def __init__(self, symbol="AAPL"):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)

    def get_recent_prices(self, window=20):
        data = self.ticker.history(period="1d", interval="1m")
        closes = data["Close"].tail(window).values
        return closes
