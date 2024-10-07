import copy
from src.regex import RegularExpression
from src.finite_automaton import FiniteAutomaton


class NFA(FiniteAutomaton):
    @classmethod
    def from_regex(cls, regex: RegularExpression) -> "NFA":
        postfix_exp = regex.to_postfix()
        nfa_stack = []
        alphabet = set(char for char in postfix_exp if char.isalnum())
        alphabet.add("")

        for char in postfix_exp:
            if char.isalnum():
                nfa_stack.append(cls._get_alphabet_nfa(char, alphabet))
            elif char == "|":
                cls._handle_union(nfa_stack)
            elif char == "*":
                cls._handle_kleene_star(nfa_stack)
            elif char == ".":
                cls._handle_concatenation(nfa_stack)
            elif char in ["(", ")"]:
                raise ValueError(f"Unexpected character in postfix expression: {char}")
            else:
                raise ValueError(f"Invalid character in regex: {char}")

        if len(nfa_stack) != 1:
            raise ValueError("Invalid regex: mismatched operands")

        return nfa_stack.pop()

    @staticmethod
    def _handle_union(nfa_stack):
        if len(nfa_stack) < 2:
            if not nfa_stack:
                nfa_stack.append(NFA._get_alphabet_nfa("", set("")))
        else:
            nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
            nfa_stack.append(NFA._union_nfa(nfa1, nfa2))

    @staticmethod
    def _handle_kleene_star(nfa_stack):
        if not nfa_stack:
            raise ValueError(
                "Invalid regex: not enough operands for Kleene star operation"
            )
        nfa_stack.append(NFA._kleene_star_nfa(nfa_stack.pop()))

    @staticmethod
    def _handle_concatenation(nfa_stack):
        if len(nfa_stack) < 2:
            raise ValueError("Invalid regex: not enough operands for concatenation")
        nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
        nfa_stack.append(NFA._concat_nfa(nfa1, nfa2))

    @staticmethod
    def _get_alphabet_nfa(character: str, alphabet: set[str]) -> "NFA":
        nfa = NFA()
        nfa.states = [0, 1]
        nfa.start_state = 0
        nfa.accept_states = [1]
        nfa.alphabet = alphabet
        nfa.transitions = {state: {a: [] for a in alphabet} for state in nfa.states}
        nfa.transitions[0][character] = [1]
        return nfa

    @staticmethod
    def _concat_nfa(nfa1: "NFA", nfa2: "NFA") -> "NFA":
        nfa = NFA()
        offset = max(nfa1.states) + 1
        nfa.states = nfa1.states + [state + offset for state in nfa2.states]
        nfa.start_state = nfa1.start_state
        nfa.accept_states = [state + offset for state in nfa2.accept_states]
        nfa.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        nfa.transitions = {
            **nfa1.transitions,
            **{
                state
                + offset: {
                    a: [s + offset for s in next_states]
                    for a, next_states in transitions.items()
                }
                for state, transitions in nfa2.transitions.items()
            },
        }
        for state in nfa1.accept_states:
            nfa.transitions.setdefault(state, {}).setdefault("", []).append(
                nfa2.start_state + offset
            )
        return nfa

    @staticmethod
    def _union_nfa(nfa1: "NFA", nfa2: "NFA") -> "NFA":
        nfa = NFA()
        offset1, offset2 = 1, max(nfa1.states) + 2
        new_start = 0
        nfa.states = (
            [new_start]
            + [state + offset1 for state in nfa1.states]
            + [state + offset2 for state in nfa2.states]
        )
        nfa.start_state = new_start
        nfa.accept_states = [state + offset1 for state in nfa1.accept_states] + [
            state + offset2 for state in nfa2.accept_states
        ]
        nfa.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        nfa.transitions = {
            **{
                state
                + offset1: {
                    a: [s + offset1 for s in next_states]
                    for a, next_states in transitions.items()
                }
                for state, transitions in nfa1.transitions.items()
            },
            **{
                state
                + offset2: {
                    a: [s + offset2 for s in next_states]
                    for a, next_states in transitions.items()
                }
                for state, transitions in nfa2.transitions.items()
            },
        }
        nfa.transitions[new_start] = {a: [] for a in nfa.alphabet}
        nfa.transitions[new_start][""] = [
            nfa1.start_state + offset1,
            nfa2.start_state + offset2,
        ]
        return nfa

    @staticmethod
    def _kleene_star_nfa(nfa1: "NFA") -> "NFA":
        nfa = NFA()
        offset = 1
        new_start, new_final = 0, max(nfa1.states) + offset + 1
        nfa.states = (
            [new_start] + [state + offset for state in nfa1.states] + [new_final]
        )
        nfa.start_state = new_start
        nfa.accept_states = [new_start, new_final]
        nfa.alphabet = nfa1.alphabet
        nfa.transitions = {
            state
            + offset: {
                a: [s + offset for s in next_states]
                for a, next_states in transitions.items()
            }
            for state, transitions in nfa1.transitions.items()
        }
        nfa.transitions[new_start] = {a: [] for a in nfa.alphabet}
        nfa.transitions[new_final] = {a: [] for a in nfa.alphabet}
        nfa.transitions[new_start][""] = [nfa1.start_state + offset, new_final]
        for final_state in nfa1.accept_states:
            nfa.transitions.setdefault(final_state + offset, {}).setdefault(
                "", []
            ).extend([nfa1.start_state + offset, new_final])
        return nfa

    def remove_epsilon_transitions(self) -> "NFA":
        new_nfa = NFA()
        new_nfa.states = self.states.copy()
        new_nfa.start_state = self.start_state
        new_nfa.alphabet = self.alphabet.copy()
        new_nfa.alphabet.discard("")  # Remove epsilon from the alphabet

        epsilon_closure = self._compute_epsilon_closure()
        new_transitions = {}
        new_accept_states = set()

        for state in self.states:
            new_transitions[state] = {}
            for symbol in new_nfa.alphabet:
                new_transitions[state][symbol] = list(
                    {
                        next_state
                        for eps_state in epsilon_closure[state]
                        for next_state in self.transitions.get(eps_state, {}).get(
                            symbol, []
                        )
                    }
                )

            if set(self.accept_states).intersection(epsilon_closure[state]):
                new_accept_states.add(state)

        new_nfa.transitions = new_transitions
        new_nfa.accept_states = list(new_accept_states)
        return new_nfa

    def _compute_epsilon_closure(self) -> dict[int, set[int]]:
        epsilon_closure = {state: {state} for state in self.states}

        for state in self.states:
            stack = list(self.transitions.get(state, {}).get("", []))
            while stack:
                current = stack.pop()
                if current not in epsilon_closure[state]:
                    epsilon_closure[state].add(current)
                    stack.extend(self.transitions.get(current, {}).get("", []))

        return epsilon_closure

    def simulate(self, input_str: str) -> bool:
        current_states = self._epsilon_closure({self.start_state})

        for symbol in input_str:
            if symbol not in self.alphabet:
                return False
            next_states = set()
            for state in current_states:
                next_states.update(self.transitions.get(state, {}).get(symbol, []))
            current_states = self._epsilon_closure(next_states)

        return bool(current_states.intersection(self.accept_states))

    def _epsilon_closure(self, states: set[int]) -> set[int]:
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in self.transitions.get(state, {}).get("", []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def remove_useless_vertices(self) -> "NFA":
        new_nfa = self.remove_epsilon_transitions() if "" in self.alphabet else NFA()
        new_nfa.states = self.states.copy()
        new_nfa.start_state = self.start_state
        new_nfa.alphabet = self.alphabet.copy()
        new_nfa.accept_states = self.accept_states.copy()
        new_nfa.transitions = {
            state: transitions.copy() for state, transitions in self.transitions.items()
        }

        useful_states = new_nfa._get_reachable_states().intersection(
            new_nfa._get_productive_states()
        )

        new_nfa.states = list(useful_states)
        new_nfa.accept_states = [
            state for state in new_nfa.accept_states if state in useful_states
        ]
        new_nfa.transitions = {
            state: {
                symbol: [s for s in next_states if s in useful_states]
                for symbol, next_states in transitions.items()
                if any(s in useful_states for s in next_states)
            }
            for state, transitions in new_nfa.transitions.items()
            if state in useful_states
        }

        return new_nfa

    def _get_reachable_states(self):
        reachable = set()
        stack = [self.start_state]

        while stack:
            state = stack.pop()
            if state not in reachable:
                reachable.add(state)
                for next_states in self.transitions.get(state, {}).values():
                    stack.extend(next_states)

        return reachable

    def _get_productive_states(self):
        productive = set(self.accept_states)
        changed = True

        while changed:
            changed = False
            for state in self.states:
                if state not in productive:
                    if any(
                        any(s in productive for s in next_states)
                        for next_states in self.transitions.get(state, {}).values()
                    ):
                        productive.add(state)
                        changed = True

        return productive

    @classmethod
    def from_string(cls, input_str: str) -> "NFA":
        lines = input_str.strip().split("\n")
        nfa = cls()

        if len(lines) < 4:
            raise ValueError("Invalid NFA string: missing required sections")

        try:
            nfa.states = [int(s) for s in lines[0].split(":")[1].strip().split()]
            nfa.alphabet = set(lines[1].split(":")[1].strip().split())
            nfa.start_state = int(lines[2].split(":")[1].strip())
            nfa.accept_states = [int(s) for s in lines[3].split(":")[1].strip().split()]
        except (ValueError, IndexError) as exc:
            raise ValueError(
                "Invalid NFA string: error in state or alphabet definition"
            ) from exc

        nfa.transitions = {}
        for line in lines[4:]:
            parts = line.split("->")
            if len(parts) != 3:
                raise ValueError(f"Invalid transition format: {line}")
            state = int(parts[0].strip())
            symbol = parts[1].strip()
            next_states = [int(s.strip()) for s in parts[2].split(",")]

            if symbol not in nfa.alphabet:
                if symbol == "":
                    nfa.alphabet.add("")
                else:
                    raise ValueError(f"Invalid symbol in transition: {symbol}")

            nfa.transitions.setdefault(state, {}).setdefault(symbol, []).extend(
                next_states
            )

        for state in nfa.transitions:
            for symbol in nfa.transitions[state]:
                nfa.transitions[state][symbol] = list(
                    set(nfa.transitions[state][symbol])
                )

        return nfa

    def __str__(self):
        output = [
            f"States: {' '.join(map(str, self.states))}",
            f"Alphabet: {' '.join(sorted(self.alphabet))}",
            f"Start: {self.start_state}",
            f"Accept: {' '.join(map(str, self.accept_states))}",
        ]

        for state in sorted(self.transitions.keys()):
            for symbol in sorted(self.transitions[state].keys()):
                next_states = ",".join(
                    map(str, sorted(self.transitions[state][symbol]))
                )
                output.append(f"{state} -> {symbol} -> {next_states}")

        return "\n".join(output)

    def to_regex(self) -> str:
        nfa = copy.deepcopy(self)

        regex_transitions = {state: {} for state in nfa.states}
        for state in nfa.states:
            for symbol, next_states in nfa.transitions.get(state, {}).items():
                for next_state in next_states:
                    regex_transitions[state].setdefault(next_state, set()).add(
                        "ε" if symbol == "" else symbol
                    )

        new_start_state = max(nfa.states) + 1
        nfa.states.append(new_start_state)
        regex_transitions[new_start_state] = {nfa.start_state: {"ε"}}
        nfa.start_state = new_start_state

        new_accept_state = max(nfa.states) + 1
        nfa.states.append(new_accept_state)
        for accept_state in nfa.accept_states:
            regex_transitions[accept_state].setdefault(new_accept_state, set()).add("ε")
        nfa.accept_states = [new_accept_state]

        states_to_eliminate = [
            state
            for state in nfa.states
            if state not in (nfa.start_state, nfa.accept_states[0])
        ]

        while states_to_eliminate:
            state_to_remove = states_to_eliminate.pop(0)

            incoming = {
                src: regex_transitions[src][state_to_remove]
                for src in regex_transitions
                if state_to_remove in regex_transitions[src]
            }
            outgoing = regex_transitions[state_to_remove]
            self_loop = regex_transitions[state_to_remove].get(state_to_remove, set())

            R_jj_star = f"({'|'.join(sorted(self_loop))})*" if self_loop else "ε"

            for src in incoming:
                for dst in outgoing:
                    new_regexes = set()
                    for R_ij in incoming[src]:
                        for R_jk in outgoing[dst]:
                            new_regex = NFA._combine_regexes(R_ij, R_jj_star, R_jk)
                            new_regexes.add(new_regex)

                    regex_transitions[src].setdefault(dst, set()).update(new_regexes)

            for src in list(regex_transitions.keys()):
                regex_transitions[src].pop(state_to_remove, None)
            regex_transitions.pop(state_to_remove, None)

        start, accept = nfa.start_state, nfa.accept_states[0]
        final_regexes = regex_transitions.get(start, {}).get(accept, set())
        res = "|".join(sorted(final_regexes)) if final_regexes else "∅"

        return RegularExpression(res.replace("ε", "")).fix()

    @staticmethod
    def _combine_regexes(R_ij, R_jj_star, R_jk):
        parts = []
        for part in (R_ij, R_jj_star, R_jk):
            if part not in ("", "ε"):
                if "|" in part or "*" in part:
                    part = f"({part})"
                parts.append(part)
        return "".join(parts) or "ε"
