import pytest
from src.nfa import NFA


def test_nfa_creation_from_string():
    nfa_string = """
    States: 0 1 2 3
    Alphabet: a b
    Start: 0
    Accept: 3
    0 -> a -> 0,1
    0 -> b -> 0
    1 -> a -> 2
    1 -> b -> 2
    2 -> a -> 3
    2 -> b -> 3
    """
    nfa = NFA.from_string(nfa_string)

    assert nfa.states == [0, 1, 2, 3]
    assert nfa.alphabet == {"a", "b"}
    assert nfa.start_state == 0
    assert nfa.accept_states == [3]
    assert nfa.transitions == {
        0: {"a": [0, 1], "b": [0]},
        1: {"a": [2], "b": [2]},
        2: {"a": [3], "b": [3]},
    }


def test_nfa_creation_from_string_with_epsilon():
    nfa_string = """
    States: 0 1 2
    Alphabet: a b 
    Start: 0
    Accept: 2
    0 -> a -> 1
    0 ->  -> 1
    1 -> b -> 2
    """
    nfa = NFA.from_string(nfa_string)

    assert nfa.states == [0, 1, 2]
    assert nfa.alphabet == {"a", "b", ""}
    assert nfa.start_state == 0
    assert nfa.accept_states == [2]
    assert nfa.transitions == {0: {"a": [1], "": [1]}, 1: {"b": [2]}}


def test_nfa_creation_from_string_invalid_input():
    invalid_nfa_string = """
    States: 0 1
    Alphabet: a
    Start: 0
    Accept: 1
    0 -> b -> 1
    """
    with pytest.raises(ValueError):
        NFA.from_string(invalid_nfa_string)


def test_nfa_creation_from_string_missing_sections():
    incomplete_nfa_string = """
    States: 0 1
    Alphabet: a
    Start: 0
    """
    with pytest.raises(ValueError):
        NFA.from_string(incomplete_nfa_string)


def test_nfa_creation_from_string_duplicate_transitions():
    duplicate_transitions_string = """
    States: 0 1 2
    Alphabet: a b
    Start: 0
    Accept: 2
    0 -> a -> 1
    0 -> a -> 2
    """
    nfa = NFA.from_string(duplicate_transitions_string)
    assert nfa.transitions[0]["a"] == [1, 2]
