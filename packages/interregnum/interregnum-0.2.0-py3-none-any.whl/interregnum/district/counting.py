#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Utilities related to counting votes."""
from __future__ import annotations
from typing import (
    Sequence,
    Iterable,
)
import dataclasses as dt
import enum
from collections import defaultdict

from ..types import parse_enum
from ..methods.preferential.types import Preference
from ..methods.types import Score
from .contenders import (
    Alliance,
    Contender,
    ContenderId,
)


__all__ = [
    "TotalVotes",
    "Votes",
    "Counting",
    "Ballots",
    "InitialSeatsSource",
]


class InitialSeatsSource(enum.Enum):
    """Origin for initial seats."""

    MIN_SEATS = enum.auto()
    """Get initial seats from the contender's `min_seats` field.

    Alternative names:

    - MIN_SEAT
    - FROM_MIN_SEATS
    - FROM_MIN_SEAT
    """

    RESULT = enum.auto()
    """Get initial seats from a node result.

    Alternative names:

    - RESULTS
    - FROM_RESULT
    - FROM_RESULTS
    """

    @classmethod
    def parse(cls, value: str | InitialSeatsSource) -> InitialSeatsSource:
        """Parse an InitialSeatsSource value from text."""
        if not isinstance(value, (str, InitialSeatsSource)):
            raise ValueError(f"value {value:r} could not be parsed")
        if isinstance(value, InitialSeatsSource):
            return value
        value = value.strip().upper().rstrip("S")
        if value.startswith("FROM_"):
            value = value[5:]
        return parse_enum(cls, value)

    def __str__(self):
        """Return value as text."""
        return self.name.lower()


class TotalVotes(enum.Enum):
    """How to compute total votes."""

    CANDIDATES = enum.auto()
    "total votes is the sum of the votes given to any candidate"

    VALID_VOTES = enum.auto()
    "total_votes is the sum of the votes considered as valid"

    ALL = enum.auto()
    "total_votes is the sum of every vote, valid or not"

    @classmethod
    def parse(cls, value: str) -> TotalVotes:
        """Parse a TotalVotes value from text."""
        return parse_enum(cls, value)

    def __str__(self):
        """Return this value as string."""
        return self.name.lower()


@dt.dataclass
class Votes:
    """Count of votes by origin."""

    candidates: Score = 0
    "votes given to candidates"

    blank: Score = 0
    "blank votes"

    void: Score = 0
    "void/null votes"

    def valid_votes(self) -> Score:
        """Return the sum of candidates votes and blank votes."""
        return self.candidates + self.blank

    def all_votes(self) -> Score:
        """Return the sum of valid votes and invalid votes."""
        return self.candidates + self.blank + self.void

    def usable_votes(self, usable: TotalVotes) -> Score:
        """Return usable votes given a criterion."""
        if usable == TotalVotes.VALID_VOTES:
            return self.valid_votes()
        if usable == TotalVotes.ALL:
            return self.all_votes()
        if usable == TotalVotes.CANDIDATES:
            return self.candidates
        raise ValueError(f"unknown criterion: {usable}")


@dt.dataclass
class Counting:
    """Collection candidates votes, preferences and alliances from a node."""

    candidates: Ballots | None = None
    "candidates votes"

    preferences: Sequence[Preference] | None = None
    "preferential ballots"

    alliances: Sequence[Alliance] | None = None
    "alliances definition"

    def seat_rules(self) -> list[tuple[int, Sequence[ContenderId]]]:
        """Compute seat restrictions for candidates and alliances.

        Each item ``(Max seats, [candidate 1, ..., candidate N])``
        as a rule like ``seats(candidate1) + ... + seats(candidateN) <= Max seats``
        """
        out: list[tuple[int, Sequence[ContenderId]]] = []
        alliances = defaultdict(list)
        if self.candidates:
            for contender in self.candidates.ballots or []:
                if contender.alliance:
                    alliances[contender.alliance].append(contender.get_id())
                if contender.max_seats is not None:
                    out.append((contender.max_seats, [contender.get_id()]))
        for alliance in self.alliances or []:
            if alliance.max_seats is not None:
                out.append((alliance.max_seats, alliances[alliance.name]))
        return out

    def get_bundle(self) -> Ballots | Sequence[Preference] | None:
        """Return preferences if not empty, or candidates."""
        if self.preferences:
            return self.preferences
        return self.candidates

    def total_votes(self) -> Votes:
        """Contender ballots, blank ballots, spoilt ballots."""
        bundle = self.get_bundle()
        if not bundle:
            return Votes(0)
        if isinstance(bundle, Ballots):
            return bundle.votes()
        return Votes(sum(b.votes for b in bundle))


@dt.dataclass
class Ballots:
    """A collection of ballots useful for counting total votes."""

    blank: Score = 0
    void: Score = 0
    ballots: Sequence[Contender] | None = None

    @staticmethod
    def build(candidates: Iterable[Contender] | None) -> Ballots:
        """Build a collection from a list of contenders."""
        out = Ballots()
        ballots = []
        if candidates is not None:
            for cand in candidates:
                if cand.is_blank():
                    out.blank += cand.votes or 0
                elif cand.is_void():
                    out.void += cand.votes or 0
                else:
                    ballots.append(cand)
            out.ballots = ballots
        return out

    def contenders_votes(self) -> Score:
        """Return the sum of votes given to contenders."""
        return sum(cand.votes or 0 for cand in self.ballots or [])

    def votes(self) -> Votes:
        """Return a Votes object."""
        return Votes(
            self.contenders_votes(),
            self.blank,
            self.void,
        )

    def contenders_seats(self) -> int:
        """Return seats won by contenders."""
        return sum(cand.seats or 0 for cand in self.ballots or [])
