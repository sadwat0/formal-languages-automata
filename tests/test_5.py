from src.nfa import NFA
from src.dfa import DFA
from src.regex import RegularExpression


def test_nfa_to_regex():
    nfa = NFA.from_regex(RegularExpression("a(b|c)*"))
    regex = nfa.to_regex()
    assert isinstance(regex, RegularExpression)
    regex_str = regex.get_regex()
    assert "a" in regex_str
    assert "b" in regex_str
    assert "c" in regex_str
    assert "*" in regex_str
    assert "|" in regex_str


def test_dfa_to_regex():
    dfa = DFA.from_regex(RegularExpression("a(b|c)*"))
    regex = dfa.to_regex()
    assert isinstance(regex, RegularExpression)
    regex_str = regex.get_regex()
    print(regex_str)
    assert "a" in regex_str
    assert "b" in regex_str
    assert "c" in regex_str
    assert "*" in regex_str
    assert "|" in regex_str


def test_regex_equivalence():
    original_regex = RegularExpression("a(b|c)*")
    nfa = NFA.from_regex(original_regex)
    dfa = DFA.from_nfa(nfa)

    nfa_regex = nfa.to_regex()
    dfa_regex = dfa.to_regex()

    nfa_from_nfa_regex = NFA.from_regex(nfa_regex)
    nfa_from_dfa_regex = NFA.from_regex(dfa_regex)

    test_strings = ["a", "ab", "ac", "abc", "acb", "abcbcbcb", ""]
    for string in test_strings:
        assert nfa.simulate(string) == nfa_from_nfa_regex.simulate(string)
        assert nfa.simulate(string) == nfa_from_dfa_regex.simulate(string)


def test_complex_regex_to_automaton_to_regex():
    complex_regex = RegularExpression("(a|b)*c(d|e)|f")
    nfa = NFA.from_regex(complex_regex)
    dfa = DFA.from_nfa(nfa)

    nfa_regex = nfa.to_regex()
    dfa_regex = dfa.to_regex()

    new_nfa_from_nfa = NFA.from_regex(nfa_regex)
    new_dfa_from_dfa = DFA.from_regex(dfa_regex)

    test_strings = ["c", "cd", "ce", "acdf", "bbcef", "abcde", "cdf", ""]
    for string in test_strings:
        assert nfa.simulate(string) == new_nfa_from_nfa.simulate(string)
        assert dfa.simulate(string) == new_dfa_from_dfa.simulate(string)
