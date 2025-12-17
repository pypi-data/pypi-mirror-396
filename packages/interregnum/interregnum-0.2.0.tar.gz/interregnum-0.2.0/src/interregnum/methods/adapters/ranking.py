#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Utilities to create rankings."""

from __future__ import annotations
from typing import (
    Callable,
    Sequence,
    Generic,
    Iterable,
)
import math
from collections import defaultdict
import itertools
from typing_extensions import override

from ...exceptions import UnsolvableError
from ..types import (
    Score,
    Candidate,
)
from ...bidimensional import Bidimensional
from . import CandLike


class Ranking(Generic[CandLike]):
    """A method that finds the most ranked candidates based on an internal criterion."""

    def __init__(self, ascending: bool):
        """Create an `ascending` (or descending) ranking."""
        self._ascending = ascending

    def winners(self) -> list[Candidate[CandLike]]:
        """Return winners sorted by score."""
        raise NotImplementedError()

    def remove(self, candidate: Candidate[CandLike] | CandLike) -> None:
        """Remove a candidate from this ranking list."""
        if isinstance(candidate, Candidate):
            self.remove_name(candidate.name)
        else:
            self.remove_name(candidate)

    def remove_name(self, name: CandLike) -> None:
        """Remove a candidate by name."""
        raise NotImplementedError()

    def ascending(self) -> bool:
        """Return True if the best score is the lowest one."""
        return self._ascending

    def empty(self) -> bool:
        """Return True if the ranking list is empty."""
        raise NotImplementedError()


class RankingList(Ranking[CandLike]):
    """A ranking based on a sorted list."""

    def __init__(self, sorted_scores: Iterable[Candidate[CandLike]], ascending: bool):
        """Create a ranking based on the value of the `votes` property."""
        super().__init__(ascending)
        self._scores = list(sorted_scores)

    @override
    def remove_name(self, name):
        self._scores = [x for x in self._scores if x.name != name]

    @override
    def winners(self):
        threshold = self._scores[0].votes
        if self._ascending:
            return list(itertools.takewhile(lambda x: x.votes <= threshold, self._scores))
        return list(itertools.takewhile(lambda x: x.votes >= threshold, self._scores))

    @override
    def empty(self):
        return not self._scores


class RankingTable(Ranking[CandLike]):
    """Ranking for partial votes.

    Each candidate owns a tuple of partial votes. Useful for ordering candidates
    by votes or scores earned in different rounds.
    """

    def __init__(
        self,
        scores: Bidimensional[CandLike, int, Score],
        limit: int,
        ascending: bool,
        from_first: bool,
    ):
        """Create a ranking table.

        Args
        ----
        limit
            explore a limited number of rounds
        ascending
            set to False for descending scores
        from_first
            explore from the first round, otherwise, explore from the last round
        """
        super().__init__(ascending)
        self._scores = scores
        if limit < 1:
            raise ValueError(f"limit ({limit}) must be >= 1")
        self._limit = limit
        self._from_first = from_first

    @override
    def remove_name(self, name) -> None:
        self._scores.remove_row(name)

    @override
    def winners(self) -> list[Candidate[CandLike]]:
        steps = self._scores.col_size()
        final_position = -1
        candidates = [Candidate(cand, 0) for cand in self._scores.iter_row_keys()]

        if self._from_first:
            seq = range(0, steps)
        else:
            seq = range(steps - 1, -1, -1)

        if not self._ascending:
            cmp_f = max
            threshold0 = -math.inf
        else:
            cmp_f = min
            threshold0 = math.inf

        for pos in seq:
            threshold: Score | float = threshold0
            candidates = []
            for cand, score in self._scores.iter_col(pos):
                candidates.append(Candidate(cand, score))
                threshold = cmp_f(score, threshold)
            if not self._ascending:
                candidates = [x for x in candidates if x.votes >= threshold]
            else:
                candidates = [x for x in candidates if x.votes <= threshold]
            if len(candidates) <= self._limit:
                final_position = pos
                break

        return [c.with_seats(final_position) for c in candidates]

    @override
    def empty(self):
        return self._scores.empty()


TieBreakFunction = Callable[[Sequence[CandLike], int], dict[str, list[CandLike]]]


def break_tie_ranking(
    ranking: Ranking[CandLike],
    limit: int,
    *,
    fallback: TieBreakFunction | None = None,
    first_criterion: str = "tie_break_best_score",
) -> dict[str, list[Candidate[CandLike]]]:
    """Break a tie based on a ranking.

    Args
    ----
    limit
        return no more than `limit` candidates as winners
    fallback
        alternative tie-breaking method if an unsolvable tie is found.
    first_criterion
        criterion applied to ties broken by this function (not the callback)
    """
    criterion = first_criterion
    out: dict[str, list[Candidate]] = defaultdict(list)
    while not ranking.empty() and (limit > 0):
        winners = ranking.winners()
        if len(winners) > limit:
            if not fallback:
                raise UnsolvableError()
            batches = fallback(winners, limit)
        else:
            batches = {first_criterion: winners}

        for criterion, batch in batches.items():
            for winner in batch:
                out[criterion].append(winner)
                ranking.remove(winner)
                limit -= 1

    return out
