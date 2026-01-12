class AgentPipeline:
    def __init__(self, behavior, cognitive, policy, governor, intervention, memory):
        self.behavior = behavior
        self.cognitive = cognitive
        self.policy = policy
        self.governor = governor
        self.intervention = intervention
        self.memory = memory

    def process(self, state, trade_event):
        flags = self.behavior.evaluate(state)
        cognitive_score = self.cognitive.compute(state)
        policy_signal = self.policy.adapt(self.memory.recent())

        decision = self.governor.decide(
            flags, cognitive_score, state, policy_signal
        )

        result = self.intervention.execute(decision, state)

        self.memory.log({
            "event": trade_event,
            "flags": flags,
            "cognitive": cognitive_score,
            "decision": decision
        })

        return decision, result
