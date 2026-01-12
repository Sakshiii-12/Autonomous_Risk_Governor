import time
from market.market_feed import MarketFeed
from events.trade_event import generate_trade_event

def run_autonomous(state, pipeline):
    feed = MarketFeed("AAPL")

    while True:
        price = feed.get_price()
        trade_event = generate_trade_event(price)

        decision, result = pipeline.process(state, trade_event)

        print(trade_event["price"], decision, result)
        time.sleep(2)
