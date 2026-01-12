import time

class InterventionAgent:
    def execute(self, decision, state):
        if decision == "HARD_BLOCK":
            state.cooldown_until = time.time() + 30
            state.last_intervention = "BLOCK"
            return "🚫 HARD BLOCK: 30s cooldown enforced"

        if decision == "SOFT_DELAY":
            state.last_intervention = "DELAY"
            return "⏳ SOFT DELAY: Trade execution slowed"

        state.last_intervention = "ALLOW"
        return "✅ Trade allowed"
