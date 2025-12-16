from fractions import Fraction
import string

from rector.charset import CharSet, RegexFlavor


def test_charset_defaults_to_explicit_flavor():
    charset = CharSet()
    assert charset.flavor is RegexFlavor.EXPLICIT


def test_charset_flavor_can_be_overridden_with_enum():
    charset = CharSet().with_flavor(RegexFlavor.PCRE)
    assert charset.flavor is RegexFlavor.PCRE


def test_digits_respect_flavor_and_strictness_explicit():
    charset = CharSet().add_from_string("12345678").with_strictness(Fraction(8, 10))
    assert list(charset.blocks()) == ["1-8"]


def test_digits_respect_flavor_and_strictness_pcre():
    charset = (
        CharSet()
        .add_from_string("12345678")
        .with_strictness(Fraction(8, 10))
        .with_flavor(RegexFlavor.PCRE)
    )
    assert list(charset.blocks()) == [r"\d"]


def test_digits_respect_flavor_and_strictness_and_deviation_pcre():
    charset = (
        CharSet()
        .add_from_string("12345678a")
        .with_strictness(Fraction(8, 10))
        .with_flavor(RegexFlavor.PCRE)
    )
    assert list(charset.blocks()) == [r"\d", "a"]


def test_digits_respect_flavor_and_strictness_posix():
    charset = (
        CharSet()
        .add_from_string("12345678")
        .with_strictness(Fraction(8, 10))
        .with_flavor(RegexFlavor.POSIX)
    )
    assert list(charset.blocks()) == [r"[:digit:]"]


def test_word_characters_collapse_to_word_class_when_deviation_zero():
    charset = (
        CharSet()
        .add_from_string(string.ascii_letters + string.digits + "_")
        .with_flavor(RegexFlavor.ECMA)
    )
    assert list(charset.blocks()) == [r"\w"]


def test_whitespace_collapses_when_strictness_met():
    charset = CharSet().add_from_string(" \t\n\r\v\f").with_flavor(RegexFlavor.PCRE)
    assert list(charset.blocks()) == [r"\s"]


def test_whitespace_posix_flavor_renders_posix_class():
    charset = CharSet().add_from_string(" \t\n\r\v\f").with_flavor(RegexFlavor.POSIX)
    assert list(charset.blocks()) == [r"[:space:]"]


def test_digits_and_word_both_meet_strictness_emit_both_tokens():
    charset = (
        CharSet()
        .add_from_string("0123456789_ab")
        .with_strictness(Fraction(1, 5))
        .with_flavor(RegexFlavor.PCRE)
    )
    assert list(charset.blocks()) == [r"\w"]


def test_canonical_tokens_used_when_deviation_non_zero_if_strictness_met():
    charset = (
        CharSet()
        .add_from_string("1234x")
        .with_strictness(Fraction(2, 10))
        .with_flavor(RegexFlavor.PCRE)
    )
    assert list(charset.blocks()) == [r"\d", "x"]


def test_canonical_tokens_used_when_deviation_non_zero_within_block():
    charset = (
        CharSet()
        .add_from_string("/1234")
        .with_strictness(Fraction(2, 10))
        .with_flavor(RegexFlavor.PCRE)
    )
    assert list(charset.blocks()) == [r"\d", "/"]


def test_newline_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\nb")
    assert str(charset) == "[ab\\n]"


def test_carriage_return_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\rb")
    assert str(charset) == "[ab\\r]"


def test_tab_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\tb")
    assert str(charset) == "[ab\\t]"


def test_backslash_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\\b")
    assert str(charset) == "[\\\\ab]"


def test_bracket_escaped_in_string_representation():
    charset = CharSet().add_from_string("a[b]")
    assert str(charset) == "[\\[\\]ab]"


def test_vertical_tab_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\vb")
    assert str(charset) == "[ab\\v]"


def test_form_feed_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\fb")
    assert str(charset) == "[ab\\f]"


def test_bell_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\bb")
    assert str(charset) == "[ab\\b]"


def test_null_char_escaped_in_string_representation():
    charset = CharSet().add_from_string("a\0b")
    assert str(charset) == "[ab\\0]"


def test_characters_return_sorted_list():
    charset = CharSet().add("z").add("a").add("A")
    assert charset.characters() == ["A", "a", "z"]


def test_contains_existing_character():
    charset = CharSet().add_from_string("a")
    assert charset.contains("a")


def test_contains_missing_character():
    charset = CharSet().add_from_string("a")
    assert not charset.contains("Z")


def test_range_addition_produces_expected_characters():
    charset = CharSet().add_range("x", "z")
    assert charset.characters() == ["x", "y", "z"]


def test_remove_updates_characters():
    charset = CharSet().add_range("x", "z")
    charset.remove("y")
    assert charset.characters() == ["x", "z"]


def test_clear_empties_charset():
    charset = CharSet().add_range("x", "z")
    charset.clear()
    assert charset.characters() == []


def test_union_produces_new_characters():
    left = CharSet().add_from_string("ab0")
    right = CharSet().add_from_string("0cd")
    union = left.union(right)
    assert union.characters() == ["0", "a", "b", "c", "d"]


def test_original_set_unchanged_after_union():
    left = CharSet().add_from_string("ab0")
    left.union(CharSet().add_from_string("0cd"))
    assert left.characters() == ["0", "a", "b"]


def test_intersection_produces_shared_characters():
    left = CharSet().add_from_string("ab0")
    right = CharSet().add_from_string("0cd")
    intersection = left.intersection(right)
    assert intersection.characters() == ["0"]


def test_add_from_set_merges_characters():
    target = CharSet().add("z")
    source = CharSet().add_from_string("xy")
    target.add_from_set(source)
    assert target.characters() == ["x", "y", "z"]


def test_difference_produces_remaining_characters():
    left = CharSet().add_from_string("ab0")
    right = CharSet().add_from_string("0cd")
    difference = left.difference(right)
    assert difference.characters() == ["a", "b"]


def test_blocks_returns_correct_ranges():
    charset = CharSet().add_from_string("abcdwxyz")
    blocks = list(charset.blocks())
    assert blocks == ["a-d", "w-z"]


def test_blocks_single_characters():
    charset = CharSet().add_from_string("ace")
    blocks = list(charset.blocks())
    assert blocks == ["a", "c", "e"]


def test_blocks_mixed_ranges_and_singletons():
    charset = CharSet().add_from_string("abcefghwxyz")
    assert "".join(charset.blocks()) == "abce-hw-z"


def test_range_pattern_correctness():
    charset = CharSet().add_from_string("abcefghijklmxyz")
    assert charset.range_pattern() == "[abce-mxyz]"


def test_string_representation_matches_characters():
    charset = CharSet().add("z").add_range("x", "y")
    assert str(charset) == "[xyz]"


def test_word_coverage_full():
    charset = CharSet().add_from_string("abc012_")
    assert charset.word_coverage() == Fraction(7, 63)


def test_digit_coverage_fraction():
    charset = CharSet().add_from_string("12ab3")
    assert charset.digit_coverage() == Fraction(3, 10)


def test_space_coverage_mixed_whitespace():
    charset = CharSet().add_from_string(" \t\nx")
    assert charset.space_coverage() == Fraction(3, 6)


def test_space_coverage_no_spaces():
    charset = CharSet().add_from_string("abc")
    assert charset.space_coverage() == Fraction(0)


def test_blank_coverage_mixed_whitespace():
    charset = CharSet().add_from_string(" \tx")
    assert charset.blank_coverage() == Fraction(2, 2)


def test_word_deviation_partial():
    charset = CharSet().add_from_string("abc$%")
    assert charset.word_deviation() == Fraction(2, 5)


def word_deviation_none():
    charset = CharSet().add_from_string("abc_123")
    assert charset.word_deviation() == Fraction(0)


def word_deviation_all():
    charset = CharSet().add_from_string("$%&")
    assert charset.word_deviation() == Fraction(1)


def digit_deviation_partial():
    charset = CharSet().add_from_string("0123abc")
    assert charset.digit_deviation() == Fraction(3, 7)


def space_deviation_partial():
    charset = CharSet().add_from_string(" \tabc")
    assert charset.space_deviation() == Fraction(3, 6)


def blank_deviation_partial():
    charset = CharSet().add_from_string(" \tabc\n")
    assert charset.blank_deviation() == Fraction(2, 4)
