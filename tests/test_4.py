import pytest
from src.regex import RegularExpression
from src.nfa import NFA
from src.dfa import DFA


@pytest.mark.parametrize(
    "regex_str, valid_inputs, invalid_inputs",
    [
        ("a(b|c)*d", ["ad", "abcd", "abbbccbd"], ["abc", "abdc", ""]),
        ("(a|b)*abb", ["abb", "aabb", "babb", "ababb"], ["ab", "ba", "bba", ""]),
    ],
)
def test_nfa_from_regex(regex_str, valid_inputs, invalid_inputs):
    regex = RegularExpression(regex_str)
    nfa = NFA.from_regex(regex)

    assert isinstance(nfa, NFA)
    for input_str in valid_inputs:
        assert nfa.simulate(input_str)
    for input_str in invalid_inputs:
        assert not nfa.simulate(input_str)


@pytest.mark.parametrize(
    "regex_str, valid_inputs, invalid_inputs",
    [
        ("a(b|c)*d", ["ad", "abcd", "abbbccbd"], ["abc", "abdc", ""]),
        ("(a|b)*abb", ["abb", "aabb", "babb", "ababb"], ["ab", "ba", "bba", ""]),
    ],
)
def test_dfa_from_regex(regex_str, valid_inputs, invalid_inputs):
    regex = RegularExpression(regex_str)
    dfa = DFA.from_regex(regex)

    assert isinstance(dfa, DFA)
    for input_str in valid_inputs:
        assert dfa.simulate(input_str)
    for input_str in invalid_inputs:
        assert not dfa.simulate(input_str)


def test_regex_from_string():
    regex_str = "a(b|c)*d"
    regex = RegularExpression(regex_str)

    assert isinstance(regex, RegularExpression)
    assert str(regex) == regex_str
