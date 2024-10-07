import pytest
from src.regex import RegularExpression
from src.dfa import DFA
from src.nfa import NFA


@pytest.mark.parametrize(
    "regex_str, test_strings, expected_results",
    [
        ("a", ["a", "b", "aa", ""], [True, False, False, False]),
        ("ab", ["ab", "a", "b", "abc", ""], [True, False, False, False, False]),
        ("a|b", ["a", "b", "c", "ab", ""], [True, True, False, False, False]),
        (
            "a*b",
            ["b", "ab", "aab", "aaab", "a", ""],
            [True, True, True, True, False, False],
        ),
        (
            "(ab)*(a|ab)(b|ca)*",
            ["a", "ab", "abab", "ababca", "abca", ""],
            [True, True, True, True, True, False],
        ),
    ],
)
def test_dfa_simulation(regex_str, test_strings, expected_results):
    regex = RegularExpression(regex_str)
    dfa = DFA.from_regex(regex)

    for test_str, expected in zip(test_strings, expected_results):
        assert (
            dfa.simulate(test_str) == expected
        ), f"Failed for regex '{regex_str}' and input '{test_str}'"


def test_dfa_from_nfa():
    nfa = NFA()
    nfa.states = [0, 1, 2]
    nfa.alphabet = {"a", "b"}
    nfa.start_state = 0
    nfa.accept_states = [2]
    nfa.transitions = {
        0: {"a": [1], "b": []},
        1: {"a": [], "b": [2]},
        2: {"a": [], "b": []},
    }

    dfa = DFA.from_nfa(nfa)

    assert set(dfa.alphabet) == {"a", "b"}
    assert dfa.start_state == 0
    assert len(dfa.accept_states) == 1
    assert len(dfa.states) == 3

    assert any(dfa.simulate("ab" * i) for i in range(5))

    assert dfa.transitions[0]["a"] == 1
    assert "b" not in dfa.transitions[0]
    assert dfa.transitions[1]["b"] == 2
    assert "a" not in dfa.transitions[1]
    assert "a" not in dfa.transitions[2]
    assert "b" not in dfa.transitions[2]


def test_dfa_is_complete():
    dfa = DFA()
    dfa.states = [0, 1]
    dfa.alphabet = {"a", "b"}
    dfa.start_state = 0
    dfa.accept_states = [1]
    dfa.transitions = {
        0: {"a": 1, "b": 0},
        1: {"a": 1, "b": 0},
    }

    assert dfa.is_complete()

    del dfa.transitions[0]["a"]
    assert not dfa.is_complete()


def test_unknown_symbols():
    regex = RegularExpression("ab")
    dfa = DFA.from_regex(regex)

    assert not dfa.simulate("abc"), "DFA should reject input with invalid symbols"
    assert not dfa.simulate("c"), "DFA should reject input with invalid symbols"
