from copy import deepcopy
from src.nfa import NFA
from src.regex import RegularExpression
from src.finite_automaton import FiniteAutomaton


class DFA(FiniteAutomaton):
    @classmethod
    def from_nfa(cls, nfa: NFA) -> "DFA":
        dfa = cls()
        dfa.alphabet = nfa.alphabet - {""}  # remove epsilon

        epsilon_closure = nfa._compute_epsilon_closure()
        nfa_to_dfa_states: dict[frozenset[int], int] = {}

        dfa.start_state = 0
        start_state_set = frozenset(epsilon_closure[nfa.start_state])
        nfa_to_dfa_states[start_state_set] = 0
        dfa.states = [0]
        dfa.transitions[0] = {}

        stack = [start_state_set]

        while stack:
            current_state_set = stack.pop()
            current_dfa_state = nfa_to_dfa_states[current_state_set]

            for symbol in dfa.alphabet:
                next_state_set = cls._get_next_state_set(
                    nfa, current_state_set, symbol, epsilon_closure
                )

                if next_state_set:
                    next_state_set = frozenset(next_state_set)
                    cls._process_next_state(
                        dfa,
                        nfa_to_dfa_states,
                        next_state_set,
                        current_dfa_state,
                        symbol,
                        stack,
                    )

            if cls._is_accept_state(nfa, current_state_set):
                dfa.accept_states.append(current_dfa_state)

        return dfa

    @staticmethod
    def _get_next_state_set(
        nfa: NFA,
        current_state_set: frozenset[int],
        symbol: str,
        epsilon_closure: dict[int, set[int]],
    ) -> set[int]:
        next_state_set = set()
        for nfa_state in current_state_set:
            next_nfa_states = nfa.transitions.get(nfa_state, {}).get(symbol, [])
            for next_nfa_state in next_nfa_states:
                next_state_set.update(epsilon_closure[next_nfa_state])
        return next_state_set

    @staticmethod
    def _process_next_state(
        dfa: "DFA",
        nfa_to_dfa_states: dict[frozenset[int], int],
        next_state_set: frozenset[int],
        current_dfa_state: int,
        symbol: str,
        stack: list[frozenset[int]],
    ):
        if next_state_set not in nfa_to_dfa_states:
            new_dfa_state = len(dfa.states)
            nfa_to_dfa_states[next_state_set] = new_dfa_state
            dfa.states.append(new_dfa_state)
            dfa.transitions[new_dfa_state] = {}
            stack.append(next_state_set)

        dfa.transitions[current_dfa_state][symbol] = nfa_to_dfa_states[next_state_set]

    @staticmethod
    def _is_accept_state(nfa: NFA, state_set: frozenset[int]) -> bool:
        return any(state in nfa.accept_states for state in state_set)

    @classmethod
    def from_regex(cls, regex: RegularExpression) -> "DFA":
        nfa = NFA.from_regex(regex)
        return cls.from_nfa(nfa)

    def simulate(self, input_str: str) -> bool:
        current_state = self.start_state

        for symbol in input_str:
            if symbol not in self.alphabet:
                return False
            if symbol not in self.transitions[current_state]:
                return False
            current_state = self.transitions[current_state][symbol]

        return current_state in self.accept_states

    def is_complete(self) -> bool:
        return all(
            set(self.transitions.get(state, {}).keys()) == self.alphabet
            for state in self.states
        )

    def make_complete(self) -> "DFA":
        """
        Makes the DFA complete by adding a trap state for missing transitions.
        """
        if self.is_complete():
            return self

        complete_dfa = DFA()
        complete_dfa.states = self.states + [len(self.states)]
        complete_dfa.alphabet = self.alphabet.copy()
        complete_dfa.transitions = {i: {} for i in complete_dfa.states}

        for state, transitions in self.transitions.items():
            complete_dfa.transitions[state] = transitions.copy()

        complete_dfa.start_state = self.start_state
        complete_dfa.accept_states = self.accept_states.copy()

        trap_state = len(self.states)

        for state in complete_dfa.states:
            for symbol in complete_dfa.alphabet:
                if symbol not in complete_dfa.transitions[state]:
                    complete_dfa.transitions[state][symbol] = trap_state

        complete_dfa.transitions[trap_state] = {
            symbol: trap_state for symbol in complete_dfa.alphabet
        }

        return complete_dfa

    def complement(self) -> "DFA":
        """
        Constructs a DFA that accepts the complement language of this DFA.
        """
        if not self.is_complete():
            complete_dfa = self.make_complete()
        else:
            complete_dfa = deepcopy(self)

        complete_dfa.accept_states = [
            state
            for state in complete_dfa.states
            if state not in complete_dfa.accept_states
        ]

        return complete_dfa

    def minimize(self) -> "DFA":
        if not self.is_complete():
            complete_dfa = self.make_complete()
        else:
            complete_dfa = deepcopy(self)

        return complete_dfa._minimize_complete_dfa()

    def _minimize_complete_dfa(self) -> "DFA":
        n = len(self.states)

        reverse_transitions = {
            i: {symbol: [] for symbol in self.alphabet} for i in range(n)
        }
        for state, transitions in self.transitions.items():
            for symbol, next_state in transitions.items():
                reverse_transitions[next_state][symbol].append(state)

        reachable = set()
        stack = [self.start_state]
        while stack:
            state = stack.pop()
            if state not in reachable:
                reachable.add(state)
                for symbol in self.alphabet:
                    next_state = self.transitions[state][symbol]
                    if next_state not in reachable:
                        stack.append(next_state)

        marked = [[False] * n for _ in range(n)]
        queue = []

        for i in range(n):
            for j in range(i + 1, n):
                if (i in self.accept_states) != (j in self.accept_states):
                    marked[i][j] = marked[j][i] = True
                    queue.append((i, j))

        while queue:
            u, v = queue.pop(0)
            for symbol in self.alphabet:
                for r in reverse_transitions[u][symbol]:
                    for s in reverse_transitions[v][symbol]:
                        if not marked[r][s]:
                            marked[r][s] = marked[s][r] = True
                            queue.append((r, s))

        component = [-1] * n
        components_count = 0

        for i in range(n):
            if i not in reachable:
                continue
            if component[i] == -1:
                component[i] = components_count
                for j in range(i + 1, n):
                    if not marked[i][j]:
                        component[j] = components_count
                components_count += 1

        minimized_dfa = DFA()
        minimized_dfa.states = list(range(components_count))
        minimized_dfa.alphabet = self.alphabet.copy()
        minimized_dfa.start_state = component[self.start_state]
        minimized_dfa.accept_states = list(
            set(component[state] for state in self.accept_states)
        )

        minimized_dfa.transitions = {i: {} for i in minimized_dfa.states}
        for state in reachable:
            for symbol in self.alphabet:
                next_state = self.transitions[state][symbol]
                minimized_dfa.transitions[component[state]][symbol] = component[
                    next_state
                ]

        return minimized_dfa

    def to_regex(self) -> "RegularExpression":
        dfa = deepcopy(self)

        regex_transitions = {}
        for state in dfa.states:
            regex_transitions[state] = {}
        for state in dfa.states:
            for symbol in dfa.alphabet:
                next_state = dfa.transitions.get(state, {}).get(symbol)
                if next_state is not None:
                    if next_state not in regex_transitions[state]:
                        regex_transitions[state][next_state] = set()
                    regex_transitions[state][next_state].add(symbol)

        new_start_state = max(dfa.states) + 1
        dfa.states.append(new_start_state)
        regex_transitions[new_start_state] = {}
        regex_transitions[new_start_state][dfa.start_state] = set(["ε"])
        dfa.start_state = new_start_state

        new_accept_state = max(dfa.states) + 1
        dfa.states.append(new_accept_state)
        for accept_state in dfa.accept_states:
            if accept_state not in regex_transitions:
                regex_transitions[accept_state] = {}
            if new_accept_state not in regex_transitions[accept_state]:
                regex_transitions[accept_state][new_accept_state] = set()
            regex_transitions[accept_state][new_accept_state].add("ε")
        dfa.accept_states = [new_accept_state]

        states_to_eliminate = [
            state
            for state in dfa.states
            if state not in (dfa.start_state, dfa.accept_states[0])
        ]

        while states_to_eliminate:
            state_to_remove = states_to_eliminate.pop(0)

            incoming = {}
            outgoing = {}
            self_loop = regex_transitions[state_to_remove].get(state_to_remove, set())
            for src in regex_transitions:
                for dst in regex_transitions[src]:
                    if dst == state_to_remove and src != state_to_remove:
                        incoming[src] = regex_transitions[src][dst]
            for dst in regex_transitions[state_to_remove]:
                if dst != state_to_remove:
                    outgoing[dst] = regex_transitions[state_to_remove][dst]

            if self_loop:
                R_jj = (
                    "+".join(sorted(self_loop))
                    if len(self_loop) > 1
                    else next(iter(self_loop))
                )
                R_jj_star = f"({R_jj})*"
            else:
                R_jj_star = "ε"

            for src in incoming:
                for dst in outgoing:
                    for R_ij in incoming[src]:
                        for R_jk in outgoing[dst]:
                            R_ij_adj = "" if R_ij == "ε" else R_ij
                            R_jj_star_adj = "" if R_jj_star == "ε" else R_jj_star
                            R_jk_adj = "" if R_jk == "ε" else R_jk

                            if R_ij_adj and ("+" in R_ij_adj or "*" in R_ij_adj):
                                R_ij_adj = f"({R_ij_adj})"
                            if R_jj_star_adj and (
                                "+" in R_jj_star_adj or "*" in R_jj_star_adj
                            ):
                                R_jj_star_adj = f"({R_jj_star_adj})"
                            if R_jk_adj and ("+" in R_jk_adj or "*" in R_jk_adj):
                                R_jk_adj = f"({R_jk_adj})"

                            new_regex = R_ij_adj + R_jj_star_adj + R_jk_adj

                            if not new_regex:
                                new_regex = "ε"

                            if dst not in regex_transitions[src]:
                                regex_transitions[src][dst] = set()
                            regex_transitions[src][dst].add(new_regex)

            for src in list(regex_transitions.keys()):
                regex_transitions[src].pop(state_to_remove, None)
            regex_transitions.pop(state_to_remove, None)

        start = dfa.start_state
        accept = dfa.accept_states[0]
        res = ""
        if accept in regex_transitions[start]:
            final_regexes = regex_transitions[start][accept]
            res = (
                "+".join(sorted(final_regexes))
                if len(final_regexes) > 1
                else next(iter(final_regexes))
            )
        else:
            res = "∅"

        final_regex = RegularExpression(res.replace("ε", "")).fix()

        return final_regex

    @staticmethod
    def _combine_regexes(regexes):
        """Helper method to combine multiple regexes with the OR operator."""
        if not regexes:
            return ""
        return (
            "|".join(f"({regex})" for regex in regexes)
            if len(regexes) > 1
            else regexes[0]
        )

    @classmethod
    def from_string(cls, input_str: str) -> "DFA":
        lines = input_str.strip().split("\n")
        dfa = cls()

        dfa.states = [int(s) for s in lines[0].split()[1:]]
        dfa.alphabet = set(lines[1].split()[1:])
        dfa.start_state = int(lines[2].split()[1])
        dfa.accept_states = [int(s) for s in lines[3].split()[1:]]

        dfa.transitions = {}
        for line in lines[4:]:
            state, symbol, next_state = line.split(" -> ")
            state = int(state)
            next_state = int(next_state)
            if state not in dfa.transitions:
                dfa.transitions[state] = {}
            dfa.transitions[state][symbol] = next_state

        return dfa

    def __str__(self):
        output = [
            f"States: {' '.join(map(str, self.states))}",
            f"Alphabet: {' '.join(sorted(self.alphabet))}",
            f"Start: {self.start_state}",
            f"Accept: {' '.join(map(str, self.accept_states))}",
        ]

        for state in sorted(self.transitions.keys()):
            for symbol in sorted(self.transitions[state].keys()):
                next_state = self.transitions[state][symbol]
                output.append(f"{state} -> {symbol} -> {next_state}")

        return "\n".join(output)
