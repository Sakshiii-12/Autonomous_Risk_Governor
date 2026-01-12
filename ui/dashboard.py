# ================== PATH FIX ==================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ================== IMPORTS ==================
import streamlit as st
import time
import random
import requests

from streamlit_autorefresh import st_autorefresh

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

from market.market_feed import MarketFeed
from market.synthetic_market import synthetic_prices

# ================== API ENDPOINTS ==================
BROKER_API_URL = "http://127.0.0.1:9000/place-order"
DECISION_API_URL = "http://127.0.0.1:8000/risk-report"

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="TradeGuard AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CUSTOM CSS STYLING ==================
st.markdown("""
<style>
    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #1a1f2e;
        --bg-tertiary: #252d3d;
        --border-color: #3a4556;
        --text-primary: #e8eaed;
        --text-secondary: #a8adb5;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
    }
    
    body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .stApp {
        background-color: var(--bg-primary);
    }
    
    /* Card/Container styling */
    .dashboard-card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-card-header {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }
    
    /* Status indicators */
    .status-allowed {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 3px solid var(--accent-green);
        color: var(--accent-green);
    }
    
    .status-delayed {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 3px solid var(--accent-amber);
        color: var(--accent-amber);
    }
    
    .status-blocked {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 3px solid var(--accent-red);
        color: var(--accent-red);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-badge-allowed {
        background-color: var(--accent-green);
        color: #000;
    }
    
    .status-badge-delayed {
        background-color: var(--accent-amber);
        color: #000;
    }
    
    .status-badge-blocked {
        background-color: var(--accent-red);
        color: #fff;
    }
    
    /* Metric styling */
    .metric-label {
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 24px;
        font-weight: 700;
        margin-top: 4px;
    }
    
    /* Timeline styling */
    .timeline-entry {
        background-color: var(--bg-tertiary);
        border-left: 2px solid var(--border-color);
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 12px;
        font-family: monospace;
        color: var(--text-secondary);
    }
    
    .divider-subtle {
        border-top: 1px solid var(--border-color);
        margin: 24px 0;
    }
    
    /* Input styling */
    .stButton > button {
        background-color: var(--accent-green) !important;
        color: #000 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }
    
    .stButton > button:hover {
        background-color: #059669 !important;
    }
    
    .stTextInput, .stNumberInput, .stSelectbox {
        background-color: var(--bg-tertiary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
if "state" not in st.session_state:
    st.session_state.state = TraderState(
        balance=100000,
        open_position=0,
        last_trade_time=0,
        consecutive_losses=0,
        trade_count=0
    )

if "memory" not in st.session_state:
    st.session_state.memory = MemoryAgent()

if "last_run" not in st.session_state:
    st.session_state.last_run = 0.0

state = st.session_state.state
memory = st.session_state.memory

# ================== AGENTS (LOCAL SIMULATION) ==================
behavior_agent = BehaviorAgent()
cognitive_agent = CognitiveAgent()
policy_agent = PolicyAgent()
governor = RiskGovernor()
intervention_agent = InterventionAgent()
market_agent = MarketContextAgent()

market_feed = MarketFeed("AAPL")
USE_SYNTHETIC = False

# ================== HEADER ==================
st.markdown("""
<div style="padding: 20px 0; margin-bottom: 30px;">
    <h1 style="margin: 0; font-size: 32px; font-weight: 700;">TradeGuard AI</h1>
    <p style="margin: 8px 0 0 0; color: #a8adb5; font-size: 14px;">Autonomous Risk Governor – Real-time Trade Oversight</p>
</div>
""", unsafe_allow_html=True)

# System status indicator
col_status_l, col_status_r = st.columns([1, 5])
with col_status_l:
    st.markdown("""
    <div style="display: inline-block; width: 12px; height: 12px; background-color: #10b981; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;"></div>
    <span style="font-size: 12px; color: #a8adb5;">System Live</span>
    """, unsafe_allow_html=True)

with col_status_r:
    st.caption("Orders evaluated by Decision API • Metrics show local simulation")

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== SIDEBAR: RISK CONTRACT ==================
st.sidebar.markdown("### Risk Contract")
st.sidebar.markdown("*Define governance rules that AI enforces*")

max_trades = st.sidebar.slider("Max trades per minute", 1, 10, 5, help="Throttle frequency of trades")
max_loss_streak = st.sidebar.slider("Max consecutive losses", 1, 5, 2, help="Stop trading after N losses in a row")

risk_contract = RiskContract(
    max_trades_per_min=max_trades,
    max_loss_streak=max_loss_streak
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Safety Principles:**
- AI enforces YOUR rules
- Regulation-aligned
- Transparent decisions
""")

# ================== SECTION 1: PLACE TRADE ==================
st.markdown("### Trade Execution")

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.5])

with col1:
    symbol = st.text_input("Symbol", "AAPL", label_visibility="collapsed")
with col2:
    side = st.selectbox("Side", ["BUY", "SELL"], label_visibility="collapsed")
with col3:
    quantity = st.number_input("Quantity", min_value=1, value=1, label_visibility="collapsed")
with col4:
    price = st.number_input("Price", value=187.5, label_visibility="collapsed")
with col5:
    place_order = st.button("Send Order", use_container_width=True)

# Broker Response Section
if place_order:
    st.markdown("### Broker Response")
    
    payload = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price
    }

    try:
        resp = requests.post(BROKER_API_URL, json=payload, timeout=2)
        response_data = resp.json()
        
        # Display response in a formatted way
        st.markdown("""
        <div class="dashboard-card">
            <div class="dashboard-card-header">Order Forwarded to Broker</div>
        </div>
        """, unsafe_allow_html=True)
        st.json(response_data)
    except Exception as e:
        st.error(f"⚠️ Broker API not reachable: {str(e)}")

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== SECTION 2: AUTONOMOUS MODE ==================
st.markdown("### Autonomous Risk Governance")

autonomous_mode = st.toggle("Enable autonomous mode", value=False, help="AI automatically executes trades with risk checks")

def process_autonomous_trade():
    pnl = random.choice([-800, -400, 300])
    simulate_trade(state, pnl)

    prices = synthetic_prices() if USE_SYNTHETIC else market_feed.get_recent_prices()
    market_regime, volatility = market_agent.assess(prices)

    flags = behavior_agent.evaluate(state, risk_contract)
    cognitive = cognitive_agent.compute(state)
    policy_signal = policy_agent.adapt(memory.recent())

    decision = governor.decide(
        flags=flags,
        cognitive=cognitive,
        state=state,
        policy_signal=policy_signal,
        market_regime=market_regime
    )

    intervention_agent.execute(decision, state)

    memory.log({
        "trade": state.trade_count,
        "flags": flags,
        "cognitive": cognitive,
        "decision": decision,
        "market": market_regime
    })

    return cognitive, decision, market_regime, volatility, flags

if autonomous_mode:
    st_autorefresh(interval=1000, key="autonomous_refresh")

    if time.time() - st.session_state.last_run > 0.9:
        st.session_state.last_run = time.time()
        cognitive, decision, market_regime, volatility, flags = process_autonomous_trade()

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== SECTION 3: SYSTEM DASHBOARD ==================
st.markdown("### System Overview")

# Row 1: Trader State
col_trader1, col_trader2, col_trader3 = st.columns(3)

with col_trader1:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Account Balance</div>
        <div class="metric-value">₹{:,.0f}</div>
    </div>
    """.format(state.balance), unsafe_allow_html=True)

with col_trader2:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Total Trades</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(state.trade_count), unsafe_allow_html=True)

with col_trader3:
    loss_streak = state.consecutive_losses
    loss_color = "#10b981" if loss_streak < max_loss_streak else "#ef4444"
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Loss Streak</div>
        <div class="metric-value" style="color: {};">{}/{}</div>
    </div>
    """.format(loss_color, loss_streak, max_loss_streak), unsafe_allow_html=True)

# Row 2: System State
col_sys1, col_sys2, col_sys3 = st.columns(3)

with col_sys1:
    market_regime_text = market_regime if "market_regime" in locals() else "—"
    volatility_val = f"{volatility:.1f}%" if "volatility" in locals() else "—"
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Market Context</div>
        <div style="margin-top: 8px;">
            <div style="color: #a8adb5; font-size: 12px; margin-bottom: 4px;">Volatility</div>
            <div class="metric-value">{}</div>
            <div style="color: #a8adb5; font-size: 12px; margin-top: 8px;">Regime</div>
            <div style="color: #e8eaed; font-weight: 600;">{}</div>
        </div>
    </div>
    """.format(volatility_val, market_regime_text), unsafe_allow_html=True)

with col_sys2:
    cognitive_score = cognitive if "cognitive" in locals() else 0
    cognitive_pct = (cognitive_score / 100) if cognitive_score else 0
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Cognitive Load</div>
        <div class="metric-value">{:.0f}</div>
        <div style="background-color: #3a4556; height: 4px; border-radius: 2px; margin-top: 12px; overflow: hidden;">
            <div style="background-color: #10b981; height: 100%; width: {}%; transition: width 0.3s;"></div>
        </div>
    </div>
    """.format(cognitive_score, cognitive_pct * 100), unsafe_allow_html=True)

with col_sys3:
    cooldown_active = state.in_cooldown()
    cooldown_status = "Yes" if cooldown_active else "No"
    cooldown_color = "#f59e0b" if cooldown_active else "#10b981"
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-header">Risk Governor Status</div>
        <div style="margin-top: 8px;">
            <div style="color: #a8adb5; font-size: 12px; margin-bottom: 4px;">Cooldown Active</div>
            <div style="color: {}; font-weight: 700; font-size: 18px;">{}</div>
            <div style="color: #a8adb5; font-size: 12px; margin-top: 8px;">Last Action</div>
            <div style="color: #e8eaed; font-family: monospace; font-size: 11px;">{}</div>
        </div>
    </div>
    """.format(cooldown_color, cooldown_status, state.last_intervention or "—"), unsafe_allow_html=True)

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== SECTION 4: DECISION TIMELINE ==================
st.markdown("### Recent Decisions")

if memory.recent():
    for i, m in enumerate(reversed(memory.recent()[-10:])):  # Show last 10
        decision_val = m.get('decision', 'NEUTRAL')
        
        # Determine decision color
        if decision_val == 'ALLOW':
            status_class = 'status-allowed'
            badge_class = 'status-badge-allowed'
        elif decision_val == 'DELAY':
            status_class = 'status-delayed'
            badge_class = 'status-badge-delayed'
        elif decision_val == 'BLOCK':
            status_class = 'status-blocked'
            badge_class = 'status-badge-blocked'
        else:
            status_class = 'status-delayed'
            badge_class = 'status-badge-delayed'
        
        st.markdown(f"""
        <div class="timeline-entry {status_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Trade #{m.get('trade', '?')}</strong> — 
                    Flags: {m.get('flags', '?')} | 
                    Cognitive: {m.get('cognitive', '?')} | 
                    Market: {m.get('market', '?')}
                </div>
                <span class="status-badge {badge_class}">→ {decision_val}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No decisions recorded yet. Enable autonomous mode to begin.")

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== SECTION 5: RISK REPORT ==================
st.markdown("### Risk Engine Diagnostics")

diag_col1, diag_col2 = st.columns(2)

with diag_col1:
    if st.button("View Engine State", use_container_width=True):
        try:
            engine_state = requests.get("http://127.0.0.1:8000/engine-state", timeout=2).json()
            st.json(engine_state)
        except Exception as e:
            st.error(f"⚠️ Decision API not reachable: {str(e)}")

with diag_col2:
    if st.button("Generate Risk Report", use_container_width=True):
        try:
            report = requests.get(DECISION_API_URL, timeout=3).json()
            st.json(report)
        except Exception as e:
            st.error(f"⚠️ Decision API not reachable: {str(e)}")

st.markdown('<div class="divider-subtle"></div>', unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("""
<div style="padding-top: 12px; border-top: 1px solid #3a4556; color: #a8adb5; font-size: 12px;">
    <strong>Disclaimer:</strong> TradeGuard AI does not predict prices or provide trading advice. 
    It autonomously governs execution behavior under stress conditions. Use at your own risk.
</div>
""", unsafe_allow_html=True)
