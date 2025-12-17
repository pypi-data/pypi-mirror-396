#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Ranking list object for Condorcet methods."""
from __future__ import annotations
from typing import (
    Sequence,
    Iterable,
    Iterator,
)
import itertools
from collections import defaultdict

from ... import inputs as ipt
from ...types import (
    Candidate,
    Score,
    AnyName,
)
from ..types import (
    Preference,
)
from ...adapters.ranking import Ranking
from .pairwise import PairwiseTable


class Copeland(Ranking[AnyName]):
    """Copeland's pairwise aggregation method.

    See `<https://en.wikipedia.org/wiki/Copeland%27s_method>`_
    """

    def __init__(
        self, candidates: Iterable[Preference[AnyName]], candidate_list: ipt.INames | None = None
    ):
        """Create a Copeland ranking.

        Args
        ----

        candidates
            list of preferences
        candidate_list
            full list of allowed candidates
        """
        super().__init__(ascending=False)

        self._pairwise = PairwiseTable.from_preferences(candidates, all_nodes=candidate_list)
        self._update_score()

    def _update_score(self) -> None:
        contenders = tuple(self._pairwise.keys())

        scores: dict[AnyName, int] = defaultdict(lambda: 0)

        for idx, cand in enumerate(contenders):
            # against candidates after `cand`
            for rival in contenders[(idx + 1) :]:
                assert cand != rival
                duel = self._pairwise.compare(cand, rival)
                if duel:
                    scores[duel[0]] += 2
                else:
                    scores[cand] += 1
                    scores[rival] += 1

        self._diff = sorted(
            [Candidate(name=cand, votes=scores[cand]) for cand in contenders],
            # descending votes
            # names introduced for reproducibility
            key=lambda x: (-x.votes, x.name),
        )

    def __iter__(self) -> Iterator[tuple[Score, Iterable[Candidate[AnyName]]]]:
        """Iterate candidates grouped by score."""
        return itertools.groupby(self._diff, key=lambda x: x.votes)

    def winners(self) -> list[Candidate[AnyName]]:
        """Get winners sorted by score."""
        assert self._diff
        max_diff = self._diff[0].votes
        return list(itertools.takewhile(lambda x: x.votes >= max_diff, self._diff))

    def remove_name(self, name: AnyName) -> None:
        """Remove candidate by name."""
        self._pairwise.purge(name)
        self._update_score()

    def empty(self) -> bool:
        """Return True if the score is empty."""
        return not self._diff


class Minimax(Ranking[AnyName]):
    """Minimax / Simpson-Kramer method.

    See `<https://en.wikipedia.org/wiki/Minimax_Condorcet>`_
    """

    def __init__(
        self,
        candidates: Iterable[Preference[AnyName]],
        margin: bool = False,
        candidate_list: ipt.INames | None = None,
    ):
        """Create a Minimax ranking.

        Args
        ----

        candidates
            list of preferences
        candidate_list
            full list of allowed candidates
        """
        super().__init__(ascending=True)
        self._use_margin = margin

        self._pairwise: PairwiseTable[AnyName] = PairwiseTable.from_preferences(
            candidates, all_nodes=candidate_list
        )
        self._score_f = self._pairwise.win if not self._use_margin else self._pairwise.margin
        self._update_score()

    def _update_score(self) -> None:
        contenders = tuple(self._pairwise.keys())

        self._row_values: list[Candidate[AnyName]] = sorted(
            [
                Candidate(
                    name=cand,
                    votes=max(self._score_f(rival, cand) for rival in contenders if rival != cand),
                )
                for cand in contenders
            ],
            # ascending
            # names included for reproducibility
            key=lambda x: (x.votes, x.name),
        )

    def __iter__(self) -> Iterator[tuple[Score, Iterable[Candidate[AnyName]]]]:
        """Iterate candidates grouped by score."""
        return itertools.groupby(self._row_values, key=lambda x: x.votes)

    def winners(self) -> list[Candidate[AnyName]]:
        """Get winners sorted by score."""
        assert self._row_values
        min_score = self._row_values[0].votes
        return list(itertools.takewhile(lambda x: x.votes <= min_score, self._row_values))

    def remove_name(self, name: AnyName) -> None:
        """Remove candidate by name."""
        self._pairwise.purge(name)
        self._update_score()

    def empty(self) -> bool:
        """Return True if there is no contender."""
        return not self._row_values


class RankedPairs(Ranking[tuple[AnyName, AnyName]]):
    """Ranked pairs / Tideman method.

    See `<https://en.wikipedia.org/wiki/Ranked_pairs>`_
    """

    def __init__(
        self, candidates: Sequence[Preference[AnyName]], candidate_list: ipt.INames | None = None
    ):
        """Create a ranked pairs ranking.

        candidates
            list of preferences
        candidate_list
            full list of allowed candidates
        """
        super().__init__(ascending=True)
        table = PairwiseTable.from_preferences(candidates, all_nodes=candidate_list)

        self._contenders = list(table.keys())

        self._pairs: list[tuple[AnyName, AnyName, tuple[Score, Score]]] = []
        for idx, cand in enumerate(self._contenders):
            for rival in self._contenders[(idx + 1) :]:
                maj1, maj2 = table[cand, rival], table[rival, cand]
                if maj1 == maj2:
                    continue
                if maj2 > maj1:
                    pair = rival, cand, (maj2, maj1)
                else:
                    pair = cand, rival, (maj1, maj2)
                self._pairs.append(pair)

        self._pairs = sorted(self._pairs, key=lambda x: (x[2], x[:2]), reverse=True)

    def contenders(self) -> list[AnyName]:
        """List of contenders."""
        return self._contenders

    def __iter__(self) -> Iterator[list[Candidate[tuple[AnyName, AnyName]]]]:
        """Iterate candidates grouped by score."""
        grouped = itertools.groupby(self._pairs, key=lambda x: x[-1])
        votes = len(self._pairs)
        for _, group in grouped:
            yield [Candidate(name=x[:-1], votes=votes) for x in group]
            votes -= 1

    def winners(self) -> list[Candidate[tuple[AnyName, AnyName]]]:
        """Get winners sorted by score."""
        assert self._pairs
        min_score = self._pairs[0][-1]
        votes = len(self._pairs)
        return [
            Candidate(name=x[:-1], votes=votes)
            for x in itertools.takewhile(lambda x: x[-1] >= min_score, self._pairs)
        ]

    def remove_name(self, name: tuple[AnyName, AnyName]):
        """Remove candidate by name from calculations."""
        self._pairs = [x for x in self._pairs if name != x[:-1]]

    def remove_candidate(self, cand: Candidate[AnyName]):
        """Remove candidate from calculations."""
        self._contenders.remove(cand.name)
        self._pairs = [x for x in self._pairs if cand.name not in x[:-1]]

    def empty(self) -> bool:
        """Return True if there is no contender."""
        return not self._contenders and not self._pairs
