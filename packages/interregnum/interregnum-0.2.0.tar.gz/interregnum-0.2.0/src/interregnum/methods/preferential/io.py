#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tools for reading and writing preferential votes."""

from __future__ import annotations
from typing import (
    IO,
    Mapping,
    Iterator,
    Iterable,
    Sequence,
    Callable,
)
import dataclasses as dt
from .types import PrefPosition
from ..types import AnyName

_BLANK = " \r\n"


@dt.dataclass
class PreferenceDialect:
    """A dialect of a preference votes file format.

    Structure
    ---------

    .. code-block:: text

        <preamble>
        <preferences>

    Preamble (optional)
    ===================

    - A line in the preamble starts with ``!``
    - A comment line starts with ``#``

    The preamble defines the escape characters:

    .. code-block:: text

        !preference >
        !equal =
        !votes :

    Then, it can define alias for candidates names:

    .. code-block:: text

        !L=my long party name
        !R=rival party

    Preferences
    ===========

    Preferences can be associated to a number of votes or can represent individual ballots.

    .. code-block:: text

        50:A>B=C>L>R
        C>B>A

    A position with the `equal` character is representing a tie.
    """

    preferent: str = ">"
    "separator for preferences"
    equal: str = "="
    "separator for ties"
    score: str = ":"
    "separator between votes/scores and preferences"
    comment: str = "#"
    "comment line prefix"
    preamble: str = "!"
    "prefix for lines in the preamble"
    _long_names: dict[str, str] = dt.field(default_factory=dict)

    def update_equivalence(self, line: str) -> None:
        """Update equvalence map with this `line` info.

        <short name>=<long name>
        """
        short_name, long_name = line.split(self.equal, 1)
        short_name = short_name.strip()
        long_name = long_name.strip()
        self._long_names[short_name] = long_name

    def check_name(self, name: str) -> str:
        """Check if a name does not have reserved chars."""
        if any(
            x in name for x in (self.preferent, self.equal, self.score, self.comment, self.preamble)
        ):
            raise ValueError(f"a name can not contain reserved sequences: {name}")
        return name

    def is_comment(self, line: str) -> bool:
        """Return True if `line` is a comment."""
        return line.startswith(self.comment)

    def as_preamble(self, line: str) -> str | None:
        """Return the same line without the preamble prefix, or None."""
        if line.startswith(self.preamble):
            return line[len(self.preamble) :]
        return None

    def update_escape(self, line: str) -> None:
        """Update dialect with the escape symbol defined in this line.

        Raises
        ------
        ValueError
            if the equivalence cannot be read
        """
        escape, char = line.split(" ", maxsplit=1)
        escape = escape.strip(_BLANK).lower()
        char = char.strip(_BLANK)
        if not char or any(x in char for x in (self.comment, self.preamble)):
            raise ValueError(
                "a separator can not be empty nor containing reserved chars "
                f"({self.preamble} or {self.comment}): {line}"
            )
        if escape in ("pref", "preference"):
            self.preferent = char
        elif escape in ("eq", "equal"):
            self.equal = char
        elif escape in ("score", "vote", "votes"):
            self.score = char
        else:
            raise ValueError(f"unknown separator: {line}")

    def read_preference(self, converter: Callable[[str], AnyName], line: str) -> _Row:
        """Read a preference line.

        Each name will be converted using `converter`.

        Args
        ----
        convert
            a function that converts a string to a name
        line
            text line with a preference
        """
        votes: int = 1
        if self.score in line:
            str_votes, prefs = line.split(self.score, 1)
            try:
                votes = int(str_votes)
            except ValueError:
                prefs = line.strip()
        else:
            prefs = line.strip()
        out: list[PrefPosition] = []
        for part in prefs.split(self.preferent):
            components = [self._translate_candidate(converter, x) for x in part.split(self.equal)]
            if len(components) == 1:
                out.append(components[0])
            else:
                out.append(tuple(components))
        return votes, out

    def _translate_candidate(self, converter: Callable[[str], AnyName], name: str) -> AnyName:
        name = name.strip()
        if not name:
            raise ValueError("empty candidates are not allowed")
        return converter(self._long_names.get(name, name))

    def write_preamble(self, stream: IO[str], short_names: Mapping[str, str]) -> None:
        """Write a preamble defining this dialect and names equivalences."""
        # preferent
        stream.write(f"{self.preamble}{self.preamble}preference {self.preferent}\n")
        # equal
        stream.write(f"{self.preamble}{self.preamble}equal {self.equal}\n")
        # score
        stream.write(f"{self.preamble}{self.preamble}score {self.score}\n")
        for long_name, short_name in short_names.items():
            stream.write(f"!{short_name}={long_name}\n")

    def write_preferences(
        self,
        stream: IO[str],
        compact: Iterable[str] | None,
        preferences: Iterable[tuple[int, Sequence[str | tuple[str, ...]]]],
    ) -> None:
        """Write preferences to a `stream` using this dialect.

        Args
        ----
        compact
            list of names that will be compacted
        preferences
            list of preferences
        """
        short_name_gen = _short_name_generator()
        # map to short names
        short_names = {}
        names = sorted(frozenset(compact or []), key=lambda x: (len(str(x)), x))
        while names:
            name = names.pop()
            while (short_name := next(short_name_gen)) == str(name):
                pass
            short_names[name] = short_name

        # write preamble
        self.write_preamble(stream, short_names)

        # write preferences
        for score, positions in preferences:
            body = self.preferent.join(self.position_to_str(pos, short_names) for pos in positions)
            if score != 1:
                line = f"{score}{self.score}{body}\n"
            else:
                line = f"{body}\n"
            stream.write(line)

    def position_to_str(
        self, position: str | tuple[str, ...], short_names: Mapping[str, str]
    ) -> str:
        """Convert a preference position (a candidate or a tuple of candidates) to string."""
        if short_names:
            if isinstance(position, (tuple, list)):
                return self.equal.join(self.check_name(short_names[x]) for x in position)
            return self.check_name(short_names[position])
        if isinstance(position, (tuple, list)):
            return self.equal.join(self.check_name(str(x)) for x in position)
        return self.check_name(str(position))


_Row = tuple[int, Sequence[PrefPosition]]


def read_preferences(
    stream: IO[str],
    converter: Callable[[str], AnyName],
) -> Iterator[_Row]:
    """Read a stream with preferences.

    Args
    ----
    converter
        convert names using this function
    """
    dialect = PreferenceDialect()

    preamble = True
    for idx, line in enumerate(stream):
        line = line.strip()
        if not line or dialect.is_comment(line):
            continue
        if preamble_line := dialect.as_preamble(line):
            if not preamble:
                raise ValueError(f"line {idx}: found definition after the preamble: {line}")
            if preamble_line.startswith(dialect.preamble):
                dialect.update_escape(dialect.as_preamble(preamble_line) or "")
            elif dialect.equal in preamble_line:
                dialect.update_equivalence(preamble_line)
            else:
                raise ValueError(f"line {idx}: unknown preamble line: {line}")
        else:
            preamble = False
            yield dialect.read_preference(converter, line)


def _char_range(first: str, last: str) -> Iterator[str]:
    for code in range(ord(first), ord(last) + 1):
        yield chr(code)


def _iter_chars() -> Iterator[str]:
    yield from _char_range("a", "z")
    yield from _char_range("A", "Z")
    yield from _char_range("0", "9")


def _short_name_generator() -> Iterator[str]:
    prefix = ""
    while True:
        for prefix_letter in _iter_chars():
            for letter in _iter_chars():
                yield prefix + letter
            prefix += prefix_letter
