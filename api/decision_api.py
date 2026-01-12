# ================= PATH FIX =================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ================= IMPORTS =================
from fastapi import FastAPI
from pydantic import BaseModel
import random

from core.state import TraderState
from core.simulator import simulate_trade
from core.risk_contract import RiskContract

from agents.behavior_agent import BehaviorAgent
from agents.cognitive_agent import CognitiveAgent
from agents.policy_agent import PolicyAgent
from agents.risk_governor import RiskGovernor
from agents.intervention_agent import InterventionAgent
from agents.memory_agent import MemoryAgent
from agents.market_context_agent import MarketContextAgent
from agents.mode_inference_agent import ModeInferenceAgent   # ✅ FIX

from market.market_feed import MarketFeed
from market.synthetic_market import synthetic_prices

# ================= APP =================
app = FastAPI(title="TradeGuard AI – Decision API")

# ================= GLOBAL STATE =================
state = TraderState(
    balance=100000,
    open_position=0,
    last_trade_time=0,
    consecutive_losses=0,
    trade_count=0
)

memory = MemoryAgent()

risk_metrics = {
    "executed": 0,
    "delayed": 0,
    "blocked": 0,
    "estimated_loss_prevented": 0
}

# ================= AGENTS =================
behavior_agent = BehaviorAgent()
cognitive_agent = CognitiveAgent()
policy_agent = PolicyAgent()
governor = RiskGovernor()
intervention_agent = InterventionAgent()
market_agent = MarketContextAgent()
mode_agent = ModeInferenceAgent()   # ✅ FIX

# ================= MARKET =================
market_feed = MarketFeed("AAPL")
USE_SYNTHETIC = True   # ✅ STRONGLY RECOMMENDED FOR DEMO STABILITY

# ================= RISK CONTRACT =================
risk_contract = RiskContract(
    max_trades_per_min=5,
    max_loss_streak=2
)

# ================= MODELS =================
class TradeRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    price: float

class DecisionResponse(BaseModel):
    decision: str
    flags: list
    cognitive_score: int
    market_regime: str
    volatility: float
    cooldown_active: bool

# ================= ENDPOINTS =================
@app.post("/evaluate-trade", response_model=DecisionResponse)
def evaluate_trade(trade: TradeRequest):

    # ---- Simulate PnL ----
    pnl = random.choice([-300, -200, 300])
    simulate_trade(state, pnl)

    # ---- Market Context ----
    prices = synthetic_prices() if USE_SYNTHETIC else market_feed.get_recent_prices()
    market_regime, volatility = market_agent.assess(prices)

    # ---- Agent Signals ----
    flags = behavior_agent.evaluate(state, risk_contract)
    cognitive = cognitive_agent.compute(state)
    policy_signal = policy_agent.adapt(memory.recent())

    # ---- MODE INFERENCE (SAFE) ----
    try:
        state.mode = mode_agent.infer(state)
    except Exception:
        state.mode = "RETAIL"

    # ---- GOVERNANCE DECISION (SAFE) ----
    try:
        decision = governor.decide(
            flags=flags,
            cognitive=cognitive,
            state=state,
            policy_signal=policy_signal,
            market_regime=market_regime
        )
    except Exception:
        decision = "HARD_BLOCK"
        flags.append("ENGINE_ERROR")

    # ---- GRACE PERIOD ----
    GRACE_TRADES = 2
    if state.trade_count <= GRACE_TRADES:
        decision = "ALLOW"

    # ---- EXECUTE INTERVENTION ----
    intervention_agent.execute(decision, state)

    # ---- MEMORY ----
    memory.log({
        "flags": flags,
        "cognitive": cognitive,
        "decision": decision,
        "market": market_regime,
        "mode": state.mode
    })

    # ---- RISK METRICS ----
    if decision == "ALLOW":
        risk_metrics["executed"] += 1
    elif decision == "SOFT_DELAY":
        risk_metrics["delayed"] += 1
        risk_metrics["estimated_loss_prevented"] += abs(pnl)
    else:
        risk_metrics["blocked"] += 1
        risk_metrics["estimated_loss_prevented"] += abs(pnl)

    return DecisionResponse(
        decision=decision,
        flags=flags,
        cognitive_score=cognitive,
        market_regime=market_regime,
        volatility=volatility,
        cooldown_active=state.in_cooldown()
    )

@app.get("/risk-report")
def risk_report():
    return risk_metrics

@app.get("/engine-state")
def engine_state():
    return {
        "balance": state.balance,
        "trade_count": state.trade_count,
        "loss_streak": state.consecutive_losses,
        "mode": getattr(state, "mode", "RETAIL")
    }
