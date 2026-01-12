class MemoryAgent:
    def __init__(self, max_len=10):
        self.memory = []
        self.max_len = max_len

    def log(self, event):
        self.memory.append(event)
        self.memory = self.memory[-self.max_len:]

    def recent(self):
        return self.memory
