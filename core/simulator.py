import time

def simulate_trade(state, pnl):
    now = time.time()
    delta = now - state.last_trade_time if state.last_trade_time else 1

    state.avg_inter_trade_time = (
        (state.avg_inter_trade_time + delta) / 2
        if state.trade_count > 0 else delta
    )

    state.trades_last_minute = (
        state.trades_last_minute + 1 if delta < 60 else 1
    )

    state.trade_count += 1
    state.last_trade_time = now

    if pnl < 0:
        state.consecutive_losses += 1
    else:
        state.consecutive_losses = 0

    state.balance += pnl
