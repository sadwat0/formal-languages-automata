import pytest
from src.regex import RegularExpression


@pytest.mark.parametrize(
    "input_regex, expected_postfix",
    [
        ("a", "a"),
        ("ab", "ab."),
        ("a|b", "ab|"),
        ("a*b", "a*b."),
        ("(a|b)*c", "ab|*c."),
        ("a(b|c)*d", "abc|*.d."),
    ],
)
def test_to_postfix(input_regex, expected_postfix):
    regex = RegularExpression(input_regex)
    assert regex.to_postfix() == expected_postfix


@pytest.mark.parametrize(
    "input_regex, expected_output",
    [
        ("ab", "a.b"),
        ("a*b", "a*.b"),
        ("(ab)*c", "(a.b)*.c"),
        ("a(b|c)d", "a.(b|c).d"),
    ],
)
def test_add_concat_symbol(input_regex, expected_output):
    result = RegularExpression._add_concat_symbol(input_regex)
    assert result == expected_output


def test_invalid_file_path():
    with pytest.raises(FileNotFoundError):
        RegularExpression("@nonexistent_file.txt")


def test_empty_regex():
    regex = RegularExpression("")
    assert regex.get_regex() == ""
    assert regex.to_postfix() == ""


@pytest.mark.parametrize(
    "input_regex, expected_regex",
    [
        ("a+b", "a|b"),
        ("(a+b)*", "(a|b)*"),
        ("a+b+c", "a|b|c"),
    ],
)
def test_plus_to_or_conversion(input_regex, expected_regex):
    regex = RegularExpression(input_regex)
    assert regex.get_regex() == expected_regex


def test_regex_str_representation():
    regex = RegularExpression("a(b|c)*d")
    assert str(regex) == "a(b|c)*d"


@pytest.mark.parametrize(
    "input_regex",
    [
        "a(b|c",
        "a|b)",
        "((a)",
        "a**",
    ],
)
def test_invalid_regex_postfix(input_regex):
    regex = RegularExpression(input_regex)
    with pytest.raises(ValueError):
        regex.to_postfix()
