from src.dfa import DFA
from src.regex import RegularExpression


def test_dfa_minimization():
    dfa = DFA.from_regex(RegularExpression("(a|b)*ab"))

    minimized_dfa = dfa.minimize()

    assert minimized_dfa.simulate("ab")
    assert minimized_dfa.simulate("aaab")
    assert minimized_dfa.simulate("bab")
    assert not minimized_dfa.simulate("a")
    assert not minimized_dfa.simulate("b")
    assert not minimized_dfa.simulate("ba")

    assert len(minimized_dfa.states) < len(dfa.states)


def test_dfa_minimization_already_minimal():
    dfa_str = """
    States: 0 1
    Alphabet: a b
    Start: 0
    Accept: 0
    0 -> a -> 1
    0 -> b -> 0
    1 -> a -> 0
    1 -> b -> 1
    """
    dfa = DFA.from_string(dfa_str)

    minimized_dfa = dfa.minimize()

    assert len(minimized_dfa.states) == len(dfa.states)
    assert minimized_dfa.alphabet == dfa.alphabet
    assert minimized_dfa.start_state == dfa.start_state
    assert set(minimized_dfa.accept_states) == set(dfa.accept_states)
    assert minimized_dfa.transitions == dfa.transitions


def test_dfa_minimization_complex():
    dfa_str = """
    States: 0 1 2 3 4 5
    Alphabet: a b
    Start: 0
    Accept: 2 3 4
    0 -> a -> 1
    0 -> b -> 2
    1 -> a -> 3
    1 -> b -> 4
    2 -> a -> 5
    2 -> b -> 5
    3 -> a -> 3
    3 -> b -> 3
    4 -> a -> 4
    4 -> b -> 4
    5 -> a -> 5
    5 -> b -> 5
    """
    dfa = DFA.from_string(dfa_str)

    minimized_dfa = dfa.minimize()

    assert minimized_dfa.simulate("b")
    assert minimized_dfa.simulate("aa")
    assert minimized_dfa.simulate("ab")
    assert not minimized_dfa.simulate("a")
    assert not minimized_dfa.simulate("ba")
    assert not minimized_dfa.simulate("bba")

    assert len(minimized_dfa.states) < len(dfa.states)
