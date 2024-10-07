import pytest
from src.regex import RegularExpression
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
        (
            "(a|b)*c",
            ["c", "ac", "bc", "abc", "abbc", "d", ""],
            [True, True, True, True, True, False, False],
        ),
        (
            "a(b|c)*d",
            ["ad", "abd", "acd", "abcd", "a", "abc", ""],
            [True, True, True, True, False, False, False],
        ),
        (
            "a*|b*",
            ["", "a", "aa", "aaa", "b", "bb", "bbb", "ab", "ba"],
            [True, True, True, True, True, True, True, False, False],
        ),
        (
            "(a|b)*",
            ["", "a", "b", "ab", "ba", "aab", "aba", "bab", "c"],
            [True, True, True, True, True, True, True, True, False],
        ),
        (
            "a*b*",
            ["", "a", "aa", "b", "bb", "ab", "aab", "abb", "ba"],
            [True, True, True, True, True, True, True, True, False],
        ),
        (
            "(a|b)*(c|d)",
            ["c", "d", "ac", "bd", "abcd", "ababc", "abab", ""],
            [True, True, True, True, False, True, False, False],
        ),
        (
            "a*(b|c)*d*",
            ["", "a", "b", "c", "d", "ab", "ac", "ad", "bcd", "abcd", "aaabbbcccddd"],
            [True, True, True, True, True, True, True, True, True, True, True],
        ),
        (
            "(a|b|c)*d(e|f)*",
            ["d", "ade", "bdf", "abcd", "abcdef", "def", "abc", "efg"],
            [True, True, True, True, True, True, False, False],
        ),
        (
            "(a|b|c)*d(e|f)*",
            ["d", "ade", "bdf", "abcd", "abcdef", "def", "abc", "efg"],
            [True, True, True, True, True, True, False, False],
        ),
        (
            "(a*b|ac)d*",
            ["a", "ab", "ac", "acd", "aabd", "abcd", "acdd", "aaabddd", "aaabbbbddd"],
            [False, True, True, True, True, False, True, True, False],
        ),
        (
            "a*|b*|c*",
            [
                "",
                "a",
                "aa",
                "aaa",
                "b",
                "bb",
                "bbb",
                "c",
                "cc",
                "ccc",
                "ab",
                "bc",
                "ca",
                "abc",
            ],
            [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
            ],
        ),
        (
            "(a*b*)*|(c*d*)*",
            [
                "",
                "a",
                "b",
                "c",
                "d",
                "ab",
                "cd",
                "aabb",
                "ccdd",
                "abcd",
                "aaabbbcccddd",
            ],
            [True, True, True, True, True, True, True, True, True, False, False],
        ),
        (
            "((a|b)*ab(a|b)*)*",
            [
                "",
                "ab",
                "abab",
                "aabb",
                "baba",
                "aaaabaaab",
                "bbbabbbb",
                "a",
                "b",
                "aa",
                "bb",
            ],
            [True, True, True, True, True, True, True, False, False, False, False],
        ),
    ],
)
def test_nfa_simulation(regex_str, test_strings, expected_results):
    regex = RegularExpression(regex_str)
    nfa = NFA.from_regex(regex)
    nfa = nfa.remove_epsilon_transitions()

    for test_str, expected in zip(test_strings, expected_results):
        assert nfa.simulate(test_str) == expected


def test_epsilon_transition_removal():
    regex = RegularExpression("a*b(d|e)*(aa(b*|c))")
    nfa = NFA.from_regex(regex)
    nfa = nfa.remove_epsilon_transitions()

    has_epsilon_after = any(
        "" in transitions for transitions in nfa.transitions.values()
    )
    assert not has_epsilon_after


def test_unknown_symbols():
    regex = RegularExpression("ab")
    nfa = NFA.from_regex(regex)

    assert not nfa.simulate("abc")
    assert not nfa.simulate("c")


def test_remove_useless_vertices():
    regex = RegularExpression("a(b|c)*d")
    nfa = NFA.from_regex(regex)

    useless_state = max(nfa.states) + 1
    nfa.states.append(useless_state)
    nfa.transitions[useless_state] = {a: [] for a in nfa.alphabet}

    original_state_count = len(nfa.states)
    nfa = nfa.remove_useless_vertices()

    assert len(nfa.states) < original_state_count
    assert useless_state not in nfa.states
    assert nfa.simulate("ad")
    assert nfa.simulate("abcd")
    assert not nfa.simulate("abc")


def test_epsilon_closure():
    regex = RegularExpression("a(b|c)*d")
    nfa = NFA.from_regex(regex)

    start_state = nfa.start_state

    epsilon_closure = nfa._epsilon_closure({start_state})

    assert start_state in epsilon_closure

    for state in epsilon_closure:
        if "" in nfa.transitions[state]:
            for next_state in nfa.transitions[state][""]:
                assert next_state in epsilon_closure

    for state in nfa.states:
        if state not in epsilon_closure:
            assert all(
                "" not in nfa.transitions[s] or state not in nfa.transitions[s][""]
                for s in epsilon_closure
            )


def test_complex_regex_with_nested_groups():
    regex = RegularExpression("((a|b)*c(d|e)*f)g")
    nfa = NFA.from_regex(regex)
    nfa.remove_epsilon_transitions()

    assert nfa.simulate("acfg")
    assert nfa.simulate("bbbcdddefg")
    assert nfa.simulate("acfg")
    assert nfa.simulate("abcdefg")
    assert not nfa.simulate("acf")
    assert not nfa.simulate("g")


def test_complex_regex_with_multiple_kleene_stars():
    regex = RegularExpression("(a*b*)*c*(d*e*)*f*")
    nfa = NFA.from_regex(regex)
    nfa.remove_epsilon_transitions()

    assert nfa.simulate("")
    assert nfa.simulate("aaabbbcccdddeee")
    assert nfa.simulate("abcdef")
    assert nfa.simulate("aabbccddee")
    assert nfa.simulate("aaabbbfff")
    assert not nfa.simulate("g")


def test_complex_regex_with_lookahead():
    regex = RegularExpression("a*b(c|d)e*")
    nfa = NFA.from_regex(regex)
    nfa.remove_epsilon_transitions()

    assert nfa.simulate("aaabce")
    assert nfa.simulate("abdeee")
    assert nfa.simulate("bc")
    assert not nfa.simulate("aaab")
    assert not nfa.simulate("ace")
    assert not nfa.simulate("abcde")


def test_nfa_state_explosion():
    regex = RegularExpression("(a|b|c|d|e)*f")
    nfa = NFA.from_regex(regex)
    nfa.remove_epsilon_transitions()

    assert nfa.simulate("f")
    assert nfa.simulate("aabbccdeef")
    assert nfa.simulate("abcdeabcdeabcdeabcdef")
    assert not nfa.simulate("abcde")
    assert not nfa.simulate("fffff")


def test_nfa_with_complex_alternation():
    regex = RegularExpression("(ab|cd)*(ef|gh)*")
    nfa = NFA.from_regex(regex)
    nfa.remove_epsilon_transitions()

    assert nfa.simulate("ef")
    assert nfa.simulate("abcdef")
    assert nfa.simulate("cdabefgh")
    assert nfa.simulate("abcdabcdefefef")
    assert nfa.simulate("abcd")
    assert nfa.simulate("efgh")
    assert not nfa.simulate("abcdefg")
