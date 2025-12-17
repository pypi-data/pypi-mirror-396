#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Preferential methods common code."""

from __future__ import annotations
from typing import (
    Sequence,
    Any,
    Iterable,
    Iterator,
    Container,
    Mapping,
    Generic,
    Callable,
    Union,
    Tuple,
)
import dataclasses as dt
import enum
from collections import defaultdict
from typing_extensions import TypeIs, TypedDict
from ...exceptions import PreconditionError
from ..types import (
    AnyName,
    AnotherName,
    Allocator,
    Score,
    Candidate,
    Data,
)


PrefPosition = Union[AnyName, Tuple[AnyName, ...]]
"A preference position"

PrefPositionLike = Union[PrefPosition, list[AnyName]]
"Something compatible to a preference position"

PrefLike = Sequence[PrefPositionLike] | tuple[PrefPositionLike, ...]
"Something compatible to a preference"


class PrefDict(TypedDict, Generic[AnyName]):
    """A dict with a preference structure."""

    votes: Score
    "votes associated to this preference"
    preference: PrefLike
    "preference positions"


class PreferenceTie(enum.IntEnum):
    """Types of preference ties."""

    NONE = 1
    "only A>B>C>D allowed"
    TERMINAL = 2
    "A>B>C=D allowed, but not A=B>C=D"
    ANYWHERE = 3
    "A=B>C=D allowed"


# TCandidate = Union[str, int]


def is_tie(
    position: PrefPosition[AnyName] | list[AnyName],
) -> TypeIs[tuple[AnyName, ...] | list[AnyName]]:
    """Return True if the position is a tie."""
    return isinstance(position, (list, tuple))


def check_untied(position: PrefPosition[AnyName]) -> AnyName:
    """Validate that the position is not a tie.

    Raises
    ------
    PreconditionError
        When the position contains a tie
    """
    if is_tie(position):
        raise PreconditionError("preferences with ties are not allowed")
    return position


# def no_tie_in_pref(preferences: tuple[PrefPosition, ...]) -> TypeIs[tuple[AnyName, ...]]:
#     """Return True if a tuple of position does not contain ties."""
#     return not any(is_tie(x) for x in preferences)


def as_tuple(item: Sequence[AnyName]) -> tuple[AnyName, ...]:
    """Convert a sequence of names to a tuple of names."""
    if isinstance(item, tuple):
        return item
    return tuple(item)


def _remove_from_positions(
    items: Iterable[PrefPosition], removable: Container[AnyName]
) -> Iterator[PrefPosition]:
    for item in items:
        if is_tie(item):
            new_item = tuple(x for x in item if x not in removable)
            if len(new_item) == 1:
                yield new_item[0]
            elif new_item:
                yield new_item
        elif item not in removable:
            yield item


@dt.dataclass(frozen=True)
class Preference(Generic[AnyName]):
    """A batch of preferential votes with the same options.

    .. admonition:: Warning

        :py:mod:`.AnyName` can not be a list or a tuple.
    """

    votes: Score
    "indicates how many ballots there are with this preference sequence"

    preference: tuple[PrefPosition, ...]
    "sequence of candidates from the most preferent to the less preferent"

    def remove(self, candidates: Container[AnyName]) -> Preference[AnyName]:
        """Remove candidates from the preference."""
        return Preference(
            votes=self.votes, preference=tuple(_remove_from_positions(self.preference, candidates))
        )

    def with_votes(self, votes: Score) -> Preference[AnyName]:
        """Return the same preference with 'votes'."""
        if votes == self.votes:
            return self
        return Preference(votes=votes, preference=self.preference)

    def transform(self, converter: Callable[[AnyName], AnotherName]) -> Preference[AnotherName]:
        """Transform names in this preference."""
        out: list[AnotherName | tuple[AnotherName, ...]] = []
        seen: set[AnotherName] = set()
        for pos in self.preference:
            if isinstance(pos, (list, tuple)):
                tie: list[AnotherName] = []
                for tied in pos:
                    repl = converter(tied)
                    if repl not in seen:
                        tie.append(repl)
                        seen.add(repl)
                if not tie:
                    continue
                if len(tie) == 1:
                    out.append(tie[0])
                else:
                    out.append(tuple(tie))
            else:
                repl = converter(pos)
                if repl not in seen:
                    out.append(repl)
                    seen.add(repl)
        return Preference(votes=self.votes, preference=tuple(out))

    @staticmethod
    def _prepare_ballot(preferences: PrefLike) -> PrefPosition:
        for item in preferences:
            if is_tie(item):
                yield as_tuple(item)
            else:
                yield item

    @classmethod
    def make(cls, data: Iterable[PreferenceLike[AnyName]]) -> Iterator[Preference[AnyName]]:
        """Convert a sequence of preferential votes to Preference objects."""
        for item in data:
            if isinstance(item, Preference):
                yield item
            elif isinstance(item, Mapping):
                yield Preference(
                    votes=item["votes"],
                    preference=tuple(cls._prepare_ballot(item["preference"])),
                )
            else:
                yield Preference(
                    votes=item[0],
                    preference=tuple(cls._prepare_ballot(item[1])),
                )

    @staticmethod
    def _make_sequence(sequence: Iterable[AnyName], allow_ties=False) -> PrefPosition:
        for item in sequence:
            if is_tie(item):
                if not allow_ties:
                    raise PreconditionError("preferences with ties are not allowed")
                yield as_tuple(item)
            else:
                yield item

    @classmethod
    def convert(cls, candidate: Sequence, *, allow_ties=False) -> Preference[AnyName]:
        """Convert a sequence to a preference."""
        if isinstance(candidate, cls):
            return candidate
        votes, prefs = tuple(candidate)
        return cls(votes, tuple(cls._make_sequence(prefs, allow_ties=allow_ties)))

    @classmethod
    def make_input(
        cls,
        ballots: Iterable,
        *,
        allow_ties=False,
        fill_truncated=False,
        all_candidates: Iterable[AnyName] | None = None,
        skip_empty: bool = False,
        raise_empty: bool = False,
    ) -> list[Preference[AnyName]]:
        """Make preference input from generic data.

        Args
        ----
        ballots
            iterable of ballots
        allow_ties
            if ties are not allowed, a :py:exc:`PreconditionError` will raise
            when a tie is found
        all_candidates
            whole list of allowed candidates
        fill_truncated
            fill truncated ballots with the list of all candidates

            eg. ``all_candidates``: A, B, C.

            If this ballot is A>B, then returns A>B>C.
            If this ballot is A, then returns A>B=C
        skip_empty
            skip empty preferences
        raise_empty
            raise :py:exc:`PreconditionError` if an empty preference was found.
        """
        if fill_truncated and not allow_ties:
            raise PreconditionError("truncated ballots are not allowed without ties")

        output = [cls.convert(x, allow_ties=allow_ties) for x in ballots]

        if fill_truncated:
            # complete truncated ballots
            if all_candidates is None:
                candidates: set[AnyName] = set()
                for ballot in output:
                    candidates.update(ballot.specified_candidates())
            else:
                candidates = set(all_candidates)
            output = [ballot.complete(candidates) for ballot in output]

        if skip_empty:
            output = [x for x in output if x.preference]

        if not output and raise_empty:
            raise PreconditionError("preferences list is empty")
        return output

    def specified_candidates(self) -> Iterator[AnyName]:
        """Iterate candidates that appear in this ballot.

        Ej.

        preference = ["A", "B", ["C", "D"], "E"]

        yield "A" -> "B" -> "C" -> "D" -> "E"
        """
        for item in self.preference:
            if is_tie(item):
                yield from item
            else:
                yield item

    def complete(self, all_candidates: Iterable[AnyName]) -> Preference[AnyName]:
        """Fill a truncated ballot at the end.

        Ej.

        preference = ["A", "B"]
        all_candidates = ["A", "B", "C", "D"]

        return ["A", "B", ["C", "D"]]
        """
        unseen = set(all_candidates)
        unseen.difference_update(self.specified_candidates())

        if not unseen:
            return self

        tail: tuple[PrefPosition, ...]
        if len(unseen) == 1:
            tail = tuple(unseen)
        else:
            tail = (tuple(unseen),)

        return Preference(
            votes=self.votes,
            preference=self.preference + tail,
        )

    def tie_type(self) -> PreferenceTie:
        """Return the type of tie in this preference."""
        pos = -1
        for idx, item in enumerate(self.preference):
            if is_tie(item):
                pos = idx
                break
        if pos < 0:
            return PreferenceTie.NONE
        if pos == (len(self.preference) - 1):
            return PreferenceTie.TERMINAL
        return PreferenceTie.ANYWHERE

    @staticmethod
    def validate_ties(batches: Iterable[Preference], tie_type: PreferenceTie):
        """Validate that 'batches' conforms with 'tie_type'."""
        valid = all(batch.tie_type() <= tie_type for batch in batches)
        if not valid:
            raise PreconditionError(f"Not allowed tie type found (allowed: {tie_type}")

    @staticmethod
    def compact_preferences(
        data: Iterable[Preference[AnyName]], skip_empty: bool = True
    ) -> list[Preference[AnyName]]:
        """Return groups with the same preferences and the accumulated votes."""
        out: dict[Any, Score] = defaultdict(lambda: 0)

        for batch in data:
            if not batch.preference and skip_empty:
                continue
            out[batch.preference] += batch.votes

        return [
            Preference(preference=key, votes=votes)
            for key, votes in sorted(out.items(), key=lambda x: (x[1], x[0]))
        ]

    @staticmethod
    def get_front_candidates(
        data: Iterable[Preference[AnyName]],
        only_first_option=True,
        candidate_list: Iterable[AnyName] | None = None,
    ) -> list[Candidate[AnyName]]:
        """Return first preference scores sorted by high score.

        if 'only_first_option', all the candidates are returned, but
        with score=0 if the candidate didn't get any vote as first preference
        """
        # first preference scores
        scores: dict[Any, Score] = defaultdict(lambda: 0)
        pool: set[Any] = set()
        if candidate_list:
            pool.update(candidate_list)

        for batch in data:
            pool.update(batch.preference)
            if batch.preference:
                preference = batch.preference[0]
                scores[preference] += batch.votes

        if not only_first_option:
            losers = pool.difference(scores.keys())

            for loser in losers:
                scores[loser] = 0

        return sorted([Candidate(*x) for x in scores.items()], key=lambda x: x.votes, reverse=True)


PreferenceLike = Preference[AnyName] | PrefDict[AnyName] | tuple[Score, PrefLike] | Sequence


class PreferentialAllocator(Allocator[AnyName, Data]):
    """A preferential allocator."""

    # def __init__(self, input_type: Input):
    #     super().__init__(input_type | Input.PREFERENCES | Input.CANDIDATES)

    @staticmethod
    def get_max_ballot_size(data: Iterable[Preference]) -> int:
        """Return the size of the longest preference sequence."""
        return max(len(x.preference) for x in data)

    @staticmethod
    def _shrink_positions(votes: Sequence[Score]) -> Sequence[Score]:
        """Shrink positional votes from the end (less preferent).

        positions - candidate votes by positional preference
        """
        last_position = len(votes)
        for score in reversed(votes):
            if score > 0:
                break
            last_position -= 1

        return tuple(votes[:last_position])

    @classmethod
    def positional_votes(
        cls,
        data: Iterable[Preference[AnyName]],
        ballot_size=None,
        whitelist: frozenset | None = None,
        shrink: bool = True,
    ) -> tuple[dict[AnyName, Sequence[Score]], int]:
        """Return positional votes by candidate."""
        if ballot_size is None:
            ballot_size = cls.get_max_ballot_size(data)

        # votes summed by a candidate by positional preferences
        scores: dict[AnyName, list[Score]] = {}

        for batch in iter(data):
            if not batch.preference:
                continue

            for position, name in enumerate(batch.preference):
                assert not isinstance(name, (tuple, list))
                if (whitelist is not None) and (name not in whitelist):
                    continue
                if name not in scores:
                    scores[name] = [0] * ballot_size
                scores[name][position] += batch.votes

        if shrink:
            return {
                name: cls._shrink_positions(votes) for name, votes in scores.items()
            }, ballot_size
        return {name: tuple(votes) for name, votes in scores.items()}, ballot_size
