# TradeGuard AI

## Problem Statement

Most retail traders lose capital due to behavioral and psychological biases rather than lack of market information. Common issues include overtrading, revenge trading, ignoring predefined risk limits, and trading during unstable market conditions.

Existing trading platforms primarily provide indicators, alerts, or post-loss analytics. These tools rely heavily on trader self-control and rational decision-making, which often fails during emotionally stressful situations. There is a lack of autonomous systems that actively prevent risky trades at the moment of execution.


## Proposed Solution

Autonomous Risk Governor, also referred to as TradeGuard AI, is a real-time autonomous risk control system designed for retail trading platforms. The system evaluates every trade request before execution by monitoring trader behavior, account-level risk exposure, and current market conditions.

The goal of the system is to enforce risk discipline automatically without interfering with the trader’s strategy or providing financial advice.


## System Architecture

The system follows a modular multi-agent architecture. Each agent operates independently with a clearly defined responsibility. This design improves scalability, interpretability, and reliability.

### Agents Used

**Behavior Monitoring Agent**
Monitors trading patterns to detect emotional or impulsive behavior such as overtrading and revenge trading.

**Risk Management Agent**
Evaluates account-level risk metrics including drawdown, loss limits, margin usage, and position sizing.

**Market Context Agent**
Identifies high-risk market conditions such as volatility spikes and unstable trading periods.

**Personalization Agent**
Learns individual trader behavior and adapts risk thresholds accordingly.

**Coordination Agent**
Aggregates signals from all agents and determines the overall risk level.

**Intervention Agent**
Applies real-time actions such as trade restriction, cooldown periods, or confirmation requirements.


## System Workflow

1. A trader attempts to place a trade
2. Behavioral patterns are analyzed
3. Account risk exposure is evaluated
4. Market conditions are assessed
5. Personalized thresholds are applied
6. A final risk decision is made
7. The trade is allowed or restricted before execution

All steps occur in real time.


## Key Features

* Real-time trade risk evaluation
* Behavioral pattern detection
* Personalized risk enforcement
* Market-aware risk control
* Autonomous intervention at execution time
* Modular and scalable architecture
* Ethical and non-advisory design



## Tools and Technologies

| Category               | Tools and Technologies      | Purpose                                       |
| ---------------------- | --------------------------- | --------------------------------------------- |
| Programming Language   | Python                      | Core system logic and agent implementation    |
| Data Processing        | NumPy, Pandas               | Behavioral data analysis and risk computation |
| Machine Learning       | scikit-learn                | Pattern detection and personalization logic   |
| Backend Framework      | FastAPI or Flask            | API services and system integration           |
| System Architecture    | Event-driven processing     | Real-time trade evaluation                    |
| Risk Logic             | Rule-based and hybrid logic | Enforcement of risk constraints               |
| Data Storage           | SQLite or PostgreSQL        | Trader profiles and system logs               |
| Monitoring and Logging | Logging module              | Auditing and system observability             |
| Visualization          | Streamlit                   | Behavioral and risk insights                  |



## Use Case Example

If a trader experiences a loss and immediately attempts to place a larger trade, the system detects emotional behavior, evaluates account risk exposure, considers current market instability, and applies a restriction or cooldown. This prevents further capital loss caused by impulsive decisions.



## Ethical and Regulatory Considerations

The system does not predict market movements.
The system does not recommend buy or sell actions.
The trader retains full control over strategy and intent.
Only risk discipline is enforced at execution time.

This design ensures ethical operation and regulatory safety.



## Hackathon Context

This project was developed during Autonomous Hacks - 26 organized by Google Developers Group Gandhinagar. The focus of development was on autonomy, real-time decision-making, and responsible fintech system design under time constraints.
