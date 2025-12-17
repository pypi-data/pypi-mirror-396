#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Borda Count methods for preferential votes.

References
----------
TODO - references
"""

from __future__ import annotations
from typing import (
    Sequence,
    Iterable,
)
import dataclasses as dt
from fractions import Fraction
import enum
from typing_extensions import override

from ...types import enum_from_string
from ...exceptions import PreconditionError
from ...random import RandomSeed
from ...ranks import (
    RankFunction,
    ranks,
)
from ...bidimensional.sparse import SparseTable
from ...bidimensional.dataframe import DataFrame
from .. import inputs as ipt
from ..adapters.ranking import (
    RankingList,
    RankingTable,
    break_tie_ranking,
)
from ..adapters.multiwinner import (
    MultiWinnerAdapter,
    MultiWinnerResultData,
    MultiWinnerState,
)
from ..types import (
    Score,
    Candidate,
    Result,
    allocators,
    Input,
    AnyName,
)
from .types import (
    Preference,
    PreferenceTie,
    PrefPosition,
    is_tie,
)
from .ties import PartialTieBreak


class BallotTieCounting(enum.Enum):
    """Ballot ties counting methods."""

    NONE = 1
    "do not allows ties"
    DOWN = 2
    "set the last position score to the tie"
    UP = 3
    "set the first position score to the tie"
    AVERAGE = 4
    "set the averaged position scores to the tie"

    @classmethod
    def parse(cls, text: str | None) -> BallotTieCounting:
        """Parse from string.

        Raises
        ------
        ValueError
            When the `text` could not be parsed.
        """
        text = enum_from_string(text or "")
        if text in ("DOWN", "ROUND_DOWN", "ROUNDING_DOWN"):
            return cls.DOWN
        if text in ("UP", "ROUND_UP", "ROUNDING_UP"):
            return cls.UP
        if text in ("AVERAGE", "AVERAGING"):
            return cls.AVERAGE
        if text:
            raise ValueError(f"tie counting mode unknown: {text}")
        return cls.NONE

    @classmethod
    def get_value(cls, value: str | BallotTieCounting | None):
        """Get a value from string or return the same value."""
        if isinstance(value, BallotTieCounting):
            return value
        return cls.parse(value)


@dt.dataclass
class BordaResultData(MultiWinnerResultData):
    """Additional result data."""

    ballot_size: int = 0
    "Number of preferences on the ballot"


PartialScore = SparseTable[AnyName, int, Score]
"A score for a candidate after N steps"


def check_ballots(tie_counting: BallotTieCounting, ballots: Iterable[Preference]):
    """Check that the ballots are valid for the tie counting mode.

    - `AVERAGE` tie counting allows ties at any position.
    - `UP` and `DOWN` only allow terminal ties.
    """
    # no -> no
    if tie_counting == BallotTieCounting.NONE:
        target = PreferenceTie.NONE
    elif tie_counting == BallotTieCounting.AVERAGE:
        target = PreferenceTie.ANYWHERE
    else:
        target = PreferenceTie.TERMINAL
    Preference.validate_ties(ballots, target)


# https://study.com/learn/lesson/borda-count-method-system.html
class BordaRanking(RankingList[AnyName]):
    """A ranking list based on Borda counting."""

    def __init__(
        self,
        preferences: Sequence[Preference[AnyName]],
        rank_f: RankFunction,
        candidate_list: ipt.INames | None = None,
        ballot_size: int | None = None,
        modified_borda=False,
        tie_counting: BallotTieCounting = BallotTieCounting.NONE,
    ):
        """Create a Borda ranking list.

        Args
        ----
        preferences
            ballots
        rank_f
            a ranking function
        candidate_list
            full list of contenders
        ballot_size
            set a fixed ballot size
        modified_borda
            use dynamic ballot size (scores will be adjusted to each ballot size)
        tie_counting
            ballot tie counting mode
        """
        self.rank_f = rank_f
        self.ballot_size = ballot_size
        self.tie_counting = tie_counting
        self.modified_borda = modified_borda

        check_ballots(self.tie_counting, preferences)

        if not self.ballot_size:
            self.ballot_size = max(len(x.preference) for x in preferences)

        if not self.ballot_size:
            raise PreconditionError("ballot size must be >= 1")

        partials: PartialScore = SparseTable(0)

        for row in preferences:
            if not row.preference:
                continue

            # modified borda: dynamic ballot size, with max declared
            ballot_size = (
                self.ballot_size
                if not self.modified_borda
                else min(self.ballot_size, len(row.preference))
            )

            pos = 0
            name: PrefPosition
            for group in row.preference:
                if not is_tie(group):
                    group = (group,)

                pos_score, pos = self.get_score(ballot_size, pos, len(group))
                points = row.votes * pos_score
                for name in group:
                    partials[name, pos - 1] += points

        if not candidate_list:
            candidate_list = partials.iter_row_keys()

        scores = []
        self._partials: dict[AnyName, list[Score]] = {}

        for cand in candidate_list:
            series: list[Score] = [0] * self.ballot_size
            for pos in range(self.ballot_size):
                series[pos] = partials[cand, pos] + series[pos - 1]
            self._partials[cand] = series
            scores.append(Candidate(cand, series[-1]))

        if not scores:
            raise PreconditionError("must be at least 1 candidate")

        scores.sort(key=lambda x: (-x.votes, x.name))
        super().__init__(scores, ascending=False)

    def get_score(self, ballot_size: int, position: int, cardinality: int) -> tuple[Score, int]:
        """Return score, next position."""
        # pos=1, [A, (B, C, *D*)] -> pos=3
        if self.tie_counting == BallotTieCounting.DOWN:
            position += cardinality - 1
            return self.rank_f(ballot_size, position), position + 1

        # pos=1, [A, (*B*, *C*, *D*)] -> pos=1,2,3
        if self.tie_counting == BallotTieCounting.AVERAGE:
            score = Fraction(
                sum(
                    self.rank_f(ballot_size, delta)
                    for delta in range(position, position + cardinality)
                ),
                cardinality,
            )
            return score, position + cardinality

        # UP and NONE
        # pos=1, [A, (*B*, C, D)] -> pos=1
        if (self.tie_counting == BallotTieCounting.NONE) and (cardinality > 1):
            raise PreconditionError("ballots with ties are not allowed")

        return self.rank_f(ballot_size, position), position + cardinality

    def get_partials(self, name):
        """Get a partial score for a given ballot position."""
        return self._partials[name]


def _make_input(ties):
    def _pref_make_input(ballots, candidate_list):
        return Preference.make_input(
            ballots, allow_ties=ties, fill_truncated=ties, all_candidates=candidate_list
        )

    return _pref_make_input


@dt.dataclass
class BordaCountState(MultiWinnerState[BordaResultData]):
    """A calculation state for Borda count."""

    mode: PartialTieBreak
    borda_score: BordaRanking | None = None

    def break_tie(
        self, candidates: Iterable[Candidate[AnyName]], ascending: bool
    ) -> dict[str, list[Candidate[AnyName]]]:
        """Resolve tie affecting `candidates`.

        return criterion, winner
        """
        assert self.borda_score
        if self.mode == PartialTieBreak.RANDOM:
            return self.random_tie_break(candidates, self.data.remaining_seats)

        table: DataFrame[AnyName, Score] = DataFrame()
        for cand in candidates:
            table.insert_row(cand.name, self.borda_score.get_partials(cand.name)[:-1])

        from_first = self.mode == PartialTieBreak.FROM_FIRST_VOTE

        return break_tie_ranking(
            RankingTable(
                table, self.data.remaining_seats, ascending=ascending, from_first=from_first
            ),
            self.data.remaining_seats,
            fallback=self.random_tie_break,
            first_criterion="tie_break_partial_vote",
        )


@allocators.register("borda", "borda_count")
class BordaCountAllocator(MultiWinnerAdapter[AnyName, BordaResultData]):
    """Borda count allocator.

    See `<https://en.wikipedia.org/wiki/Borda_count>`_

    :py:data:`.allocators` keys:

    - `borda`
    - `borda_count`
    """

    def __init__(
        self,
        rank_f: str | RankFunction,
        tie_counting: str | BallotTieCounting | None = None,
        tie_break: PartialTieBreak | str = "from_first_vote",
    ):
        """Create a borda count allocator.

        Args
        ----
        rank_f
            score function
        tie_counting
            ballot tie counting mode
        tie_break
            strategies for breaking candidate ties


        Examples
        --------
        >>> # use the Nauru score
        >>> # allow ballot ties (tie members will get the average score)
        >>> # in case of a candidates tie, use partial votes to break it,
        >>> # starting from the first position
        >>> borda = BordaCountAllocator(
        >>>     "nauru",
        >>>     tie_counting="average",
        >>>     tie_break="from_first_vote"
        >>> )
        """
        self.tie_counting_mode = tie_counting
        self.rank_f = rank_f
        self.tie_break_rule = tie_break
        super().__init__(
            _make_input(BallotTieCounting.get_value(tie_counting) != BallotTieCounting.NONE),
            BordaRanking,
            Input.PREFERENCES,
            Input.SEATS | Input.CANDIDATE_LIST | Input.RANDOM_SEED | Input.MAX_BALLOTS_SIZE,
        )

    @override
    def _init_data(self):
        return BordaResultData()

    @override
    def _reset(self, random_seed):
        return BordaCountState(
            random_seed=random_seed,
            data=self._init_data(),
            mode=PartialTieBreak.get_value(self.tie_break_rule),
        )

    @override
    def _base_ranking_kwargs(self):
        return {
            "rank_f": ranks.get(self.rank_f),
            "tie_counting": BallotTieCounting.get_value(self.tie_counting_mode),
        }

    @override
    def _build_input(self, data, **ranking_kwargs):
        return super()._build_input(data, candidate_list=ranking_kwargs.get("candidate_list"))

    def calc(
        self,
        preferences,
        seats: int = 1,
        random_seed: RandomSeed | None = None,
        max_ballot_size: int | None = None,
        candidate_list: ipt.INames | None = None,
        **kwargs,
    ) -> Result:
        """Allocate seats to candidates.

        Args
        ----
        preferences
            preferential votes
        seats
            allocatable seats
        max_ballot_size
            fixed ballot size (if empty, get the size of the larger ballot)
        random_seed
            used by tie-breakers
        """
        _state, result = super()._calc(
            preferences,
            seats=seats,
            random_seed=random_seed,
            ballot_size=max_ballot_size,
            candidate_list=candidate_list,
            **kwargs,
        )
        return result

    @override
    def _build_ranking(self, state, candidates, **ranking_args):
        state.borda_score = super()._build_ranking(state, candidates, **ranking_args)
        return state.borda_score

    @override
    def _build_result(self, state, elected):
        state.data.ballot_size = state.borda_score.ballot_size
        return super()._build_result(state, elected)
