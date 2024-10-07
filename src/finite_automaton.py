from abc import ABC, abstractmethod


class FiniteAutomaton(ABC):
    def __init__(self):
        self.states = []
        self.alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = []

    @abstractmethod
    def simulate(self, input_str: str) -> bool:
        pass

    def __str__(self):
        output = [
            f"{self.__class__.__name__} Information:",
            f"Alphabet: {sorted(self.alphabet)}",
            f"States: {self.states}",
            f"Start State: {self.start_state}",
            f"Accept States: {self.accept_states}",
            "Transitions:",
        ]

        for state in sorted(self.transitions.keys()):
            for symbol in sorted(self.transitions[state].keys()):
                next_states = self.transitions[state][symbol]
                if next_states == []:
                    continue
                if isinstance(next_states, list):
                    next_states = sorted(next_states)
                output.append(f"  {state} --({symbol})--> {next_states}")

        return "\n".join(output)

    def print(self):
        print(str(self))

    @classmethod
    @abstractmethod
    def from_string(cls, input_str: str) -> "FiniteAutomaton":
        pass

    @abstractmethod
    def to_regex(self) -> str:
        pass
