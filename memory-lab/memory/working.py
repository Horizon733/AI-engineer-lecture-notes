"""Working memory - the current conversation.

LIVES IN: a Python list in RAM.
LIFESPAN: current session. Lost on restart.
INJECTED AS: the messages[] list passed to the LLM.
"""


class WorkingMemory:
    def __init__(self, max_turns: int = 20):
        self.turns: list[dict] = []
        self.max_turns = max_turns

    def add_user(self, text: str):
        self.turns.append({"role": "user", "content": text})
        print(f"[WORKING] added user turn (total: {len(self.turns)})")
        self._trim()

    def add_assistant(self, text: str):
        self.turns.append({"role": "assistant", "content": text})
        print(f"[WORKING] added assistant turn (total: {len(self.turns)})")
        self._trim()

    def recent(self, n: int = 10) -> list[dict]:
        return self.turns[-n:]

    def all(self) -> list[dict]:
        return list(self.turns)

    def clear(self):
        self.turns.clear()
        print("[WORKING] cleared")

    def _trim(self):
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
            print(f"[WORKING] trimmed to last {self.max_turns} turns")
