import time
import uuid

def generate_trade_event(price):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "symbol": "AAPL",
        "price": price,
        "side": "BUY",
        "quantity": 1
    }
