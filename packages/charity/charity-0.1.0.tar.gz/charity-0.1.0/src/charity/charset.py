"""Efficient character-set representation and utilities."""

from __future__ import annotations

from enum import Enum
from fractions import Fraction
from typing import Iterable, Mapping


class RegexFlavor(str, Enum):
    """Supported regex flavor variants for rendering character classes."""

    PCRE = "pcre"
    POSIX = "posix"
    ECMA = "ecma"
    EXPLICIT = "explicit"  # Use explicit ranges instead of flavor-specific shorthands.


class CharSet:
    """A set of characters with efficient membership testing."""

    def __init__(self) -> None:
        self._bits: int = 0
        self.strictness: Fraction = Fraction(1, 1)
        self.flavor: RegexFlavor = RegexFlavor.EXPLICIT

    def with_strictness(self, strictness: Fraction) -> CharSet:
        """Set the strictness level for the character set."""
        self.strictness = strictness
        return self

    def with_flavor(self, flavor: RegexFlavor) -> CharSet:
        """Set the flavor for the character set."""
        self.flavor = flavor
        return self

    @classmethod
    def from_char(cls, char: str) -> CharSet:
        """Create a CharSet containing only the given character."""
        return cls().add(char)

    @classmethod
    def from_range(cls, start: str, end: str) -> CharSet:
        """Create a CharSet containing the inclusive range start..end."""
        return cls().add_range(start, end)

    @classmethod
    def from_string(cls, s: str) -> CharSet:
        """Create a CharSet from every character in the provided string."""
        return cls().add_from_string(s)

    @classmethod
    def from_charset(cls, other: CharSet) -> CharSet:
        """Duplicate another CharSet."""
        return cls.from_bits(other._bits)

    @classmethod
    def from_bits(cls, bits: int) -> CharSet:
        """Create a CharSet from the given bit representation."""
        result = cls()
        result._bits = bits
        return result

    def add(self, char: str) -> CharSet:
        """Add a character to the set."""
        self._bits |= 1 << ord(char)
        return self

    def add_range(self, start: str, end: str) -> CharSet:
        """Add a range of characters to the set."""
        for code in range(ord(start), ord(end) + 1):
            self._bits |= 1 << code
        return self

    def add_from_set(self, other: CharSet) -> CharSet:
        """Add all characters from another CharSet to this set."""
        self._bits |= other._bits
        return self

    def add_from_string(self, s: str) -> CharSet:
        """Add all characters from a string to the set."""
        for char in s:
            self._bits |= 1 << ord(char)
        return self

    def remove(self, char: str) -> CharSet:
        """Remove a character from the set."""
        self._bits &= ~(1 << ord(char))
        return self

    def clear(self) -> CharSet:
        """Clear all characters from the set."""
        self._bits = 0
        return self

    def contains(self, char: str) -> bool:
        """Check if the character is in the set."""
        return bool(self._bits & (1 << ord(char)))

    def intersection(self, other: CharSet) -> CharSet:
        """Return the intersection of this set with another set."""
        return CharSet.from_bits(self._bits & other._bits)

    def union(self, other: CharSet) -> CharSet:
        """Return the union of this set with another set."""
        return CharSet.from_bits(self._bits | other._bits)

    def difference(self, other: CharSet) -> CharSet:
        """Return the difference of this set with another set."""
        return CharSet.from_bits(self._bits & ~other._bits)

    def blocks(self) -> Iterable[str]:
        """Yield ranges of one or more consecutive characters in the set as string in the form '<character> for 1-3 consecutive characters, otherwise '<first>-<last>'."""
        tokens, remaining_bits = self._canonical_decomposition()
        mask = (1 << 256) - 1
        active_bits = remaining_bits & mask if tokens else self._bits & mask

        for token in tokens:
            yield token

        index = 0
        while index < 256:
            if active_bits & (1 << index):
                start_index = index
                while index + 1 < 256 and active_bits & (1 << (index + 1)):
                    index += 1
                end_index = index
                yield from self._charset_blocks(start_index, end_index)
            index += 1

    def range_pattern(self) -> str:
        """Return a regex character class pattern representing the character set."""
        tokens, remaining_bits = self._canonical_decomposition()
        mask = (1 << 256) - 1

        if tokens and remaining_bits == 0:
            token = tokens[0]
            if self.flavor is RegexFlavor.POSIX:
                return f"[{token}]"
            return token

        active_bits = remaining_bits & mask if tokens else self._bits & mask

        class_parts: list[str] = []
        class_parts.extend(tokens)

        index = 0
        while index < 256:
            if active_bits & (1 << index):
                start_index = index
                while index + 1 < 256 and active_bits & (1 << (index + 1)):
                    index += 1
                end_index = index
                class_parts.extend(self._charset_blocks(start_index, end_index))
            index += 1

        return f"[{''.join(class_parts)}]"

    def count(self) -> int:
        """Return the number of characters in the set in an efficient way."""
        count = 0
        active_bits = self._bits & ((1 << 256) - 1)
        while active_bits:
            active_bits &= active_bits - 1
            count += 1
        return count

    def bits(self) -> int:
        """Return the internal bit representation of the character set."""
        return self._bits

    def characters(self) -> list[str]:
        """Return a list of characters in the set."""
        result: list[str] = []
        active_bits = self._bits & ((1 << 256) - 1)
        while active_bits:
            lowest_bit = active_bits & -active_bits
            index = lowest_bit.bit_length() - 1
            result.append(chr(index))
            active_bits &= active_bits - 1
        return result

    def word_coverage(self) -> Fraction:
        """Return the fraction of word characters in the set."""
        return coverage(self, WORD_CHARS)

    def digit_coverage(self) -> Fraction:
        """Return the fraction of digit characters in the set."""
        return coverage(self, DIGIT_CHARS)

    def space_coverage(self) -> Fraction:
        """Return the fraction of space characters in the set."""
        return coverage(self, SPACE_CHARS)

    def blank_coverage(self) -> Fraction:
        """Return the fraction of blank characters in the set."""
        return coverage(self, BLANK_CHARS)

    def word_deviation(self) -> Fraction:
        """Return the fraction of non-word characters in the set."""
        return deviation(self, WORD_CHARS)

    def digit_deviation(self) -> Fraction:
        """Return the fraction of non-digit characters in the set."""
        return deviation(self, DIGIT_CHARS)

    def space_deviation(self) -> Fraction:
        """Return the fraction of non-space characters in the set."""
        return deviation(self, SPACE_CHARS)

    def blank_deviation(self) -> Fraction:
        """Return the fraction of non-blank characters in the set."""
        return deviation(self, BLANK_CHARS)

    def _canonical_decomposition(self) -> tuple[list[str], int]:
        """
        Return canonical tokens plus remaining bits when coverage meets strictness.
        """

        if self.count() == 0:
            return [], 0

        tokens: list[str] = []
        mask = (1 << 256) - 1
        remaining_bits = self._bits & mask

        candidates: list[tuple[CharSet, Mapping[RegexFlavor, str | None]]] = [
            (
                WORD_CHARS,
                {
                    RegexFlavor.ECMA: r"\w",
                    RegexFlavor.PCRE: r"\w",
                    RegexFlavor.POSIX: r"[:word:]",
                    RegexFlavor.EXPLICIT: None,
                },
            ),
            (
                DIGIT_CHARS,
                {
                    RegexFlavor.ECMA: r"\d",
                    RegexFlavor.PCRE: r"\d",
                    RegexFlavor.POSIX: r"[:digit:]",
                    RegexFlavor.EXPLICIT: None,
                },
            ),
            (
                SPACE_CHARS,
                {
                    RegexFlavor.ECMA: r"\s",
                    RegexFlavor.PCRE: r"\s",
                    RegexFlavor.POSIX: r"[:space:]",
                    RegexFlavor.EXPLICIT: None,
                },
            ),
        ]

        for target, token_map in candidates:
            token = token_map.get(self.flavor)
            if not token:
                continue

            target_bits = target.bits()
            intersection = remaining_bits & target_bits
            if intersection == 0:
                continue

            target_count = target.count()
            coverage_fraction = Fraction(_bit_count(intersection), target_count)
            if coverage_fraction < self.strictness:
                continue

            tokens.append(token)
            remaining_bits &= ~target_bits

        return tokens, remaining_bits

    def _charset_blocks(self, start_index: int, end_index: int) -> Iterable[str]:
        if end_index - start_index >= 3:
            yield f"{chr(start_index)}-{chr(end_index)}"
        else:
            yield from (chr(i) for i in range(start_index, end_index + 1))

    def _sorted_characters(self) -> list[str]:
        """Return characters sorted by readability (printable first) then codepoint."""

        active_chars = [chr(idx) for idx in range(256) if self._bits & (1 << idx)]
        return sorted(active_chars, key=lambda ch: (not ch.isprintable(), ord(ch)))

    def __str__(self) -> str:
        """String representation of the character set."""
        ordered = self._sorted_characters()
        escaped = "".join(_escape_for_display(ch) for ch in ordered)
        return f"[{escaped}]"


WORD_CHARS = CharSet().add_from_string(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
)
DIGIT_CHARS = CharSet().add_from_string("0123456789")
SPACE_CHARS = CharSet().add_from_string(" \t\n\r\v\f")
BLANK_CHARS = CharSet().add_from_string(" \t")
ALL_CHARS = CharSet().add_range("\x01", "\xff").remove("\n")


def coverage(sample: CharSet, target: CharSet) -> Fraction:
    """Calculate the coverage of target characters in the sample set."""
    if target.count() == 0:
        return Fraction(0)
    return Fraction(sample.intersection(target).count(), target.count())


def deviation(sample: CharSet, target: CharSet) -> Fraction:
    """Calculate the deviation from target characters in the sample set."""
    len(sample.characters())
    return Fraction(sample.difference(target).count(), sample.count())


def _bit_count(value: int) -> int:
    """Return number of set bits in integer value."""

    return value.bit_count()


def _escape_for_display(char: str) -> str:
    """Escape control and special characters for stable string output."""

    escape_map = {
        "\n": r"\n",
        "\r": r"\r",
        "\t": r"\t",
        "\v": r"\v",
        "\f": r"\f",
        "\b": r"\b",
        "\0": r"\0",
        "\\": r"\\",
        "[": r"\[",
        "]": r"\]",
    }
    return escape_map.get(char, char)
