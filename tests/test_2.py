from src.nfa import NFA
from src.dfa import DFA
from src.regex import RegularExpression


def test_dfa_creation_from_nfa():
    nfa = NFA.from_regex(RegularExpression("a(b|c)*"))
    dfa = DFA.from_nfa(nfa)
    assert isinstance(dfa, DFA)


def test_dfa_simulation():
    dfa = DFA.from_regex(RegularExpression("a(b|c)*"))
    assert dfa.simulate("a")
    assert dfa.simulate("abc")
    assert dfa.simulate("acbcb")
    assert not dfa.simulate("b")
    assert not dfa.simulate("cab")


def test_dfa_from_string():
    dfa_str = """
    States: 0 1 2
    Alphabet: a b
    Start: 0
    Accept: 2
    0 -> a -> 1
    0 -> b -> 0
    1 -> a -> 1
    1 -> b -> 2
    2 -> a -> 1
    2 -> b -> 0
    """
    dfa = DFA.from_string(dfa_str)
    assert isinstance(dfa, DFA)
    assert dfa.states == [0, 1, 2]
    assert dfa.alphabet == {"a", "b"}
    assert dfa.start_state == 0
    assert dfa.accept_states == [2]
    assert dfa.transitions == {
        0: {"a": 1, "b": 0},
        1: {"a": 1, "b": 2},
        2: {"a": 1, "b": 0},
    }


def test_dfa_to_string():
    dfa = DFA.from_regex(RegularExpression("a(b|c)*"))
    dfa_str = str(dfa)
    assert "States:" in dfa_str
    assert "Alphabet:" in dfa_str
    assert "Start:" in dfa_str
    assert "Accept:" in dfa_str
    assert "->" in dfa_str


def test_dfa_nfa_equivalence():
    regex = RegularExpression("a(b|c)*d")
    nfa = NFA.from_regex(regex)
    dfa = DFA.from_nfa(nfa)

    test_strings = ["ad", "abd", "acd", "abcbcd", "abcbcbd", "a", "abc", "abcd", "acbd"]
    for string in test_strings:
        assert nfa.simulate(string) == dfa.simulate(string)
