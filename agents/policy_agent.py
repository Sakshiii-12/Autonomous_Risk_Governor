class PolicyAgent:
    def adapt(self, memory):
        if len(memory) < 3:
            return "NO_CHANGE"

        last = memory[-3:]
        hard_blocks = sum(1 for m in last if m["decision"] == "HARD_BLOCK")

        if hard_blocks >= 3:
            return "RELAX"

        return "NO_CHANGE"
