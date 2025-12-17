#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Condorcet methods."""
from __future__ import annotations
from functools import partial
from typing_extensions import override

from ...types import (
    PreconditionError,
    allocators,
    Input,
    AnyName,
    RandomSeed,
    CandidateFilter,
)
from ...events import Event
from ...adapters.ranking import Ranking
from ...adapters.multiwinner import (
    MultiWinnerAdapter,
    MultiWinnerResultData,
)
from ... import inputs as ipt
from ..types import Preference
from . import rankings
from .ranked_pairs import CondorcetRankedPairsAllocator

__all__ = [
    "CondorcetCopelandAllocator",
    "CondorcetMinimaxAllocator",
    "CondorcetRankedPairsAllocator",
    "CondorcetAllocator",
]


class CondorcetAllocator(MultiWinnerAdapter[AnyName, MultiWinnerResultData]):
    """An allocator for Condorcet methods."""

    def __init__(self, ranking_f, allow_ties=True, fill_truncated=False):
        """Create a Condorcet method.

        Args
        ----
        ranking_f
            ranking list
        allow_ties
            allow more than one candidate at the same preference position
        fill_truncated
            fill a truncated ballot with a tie of the remaining candidates
        """
        super().__init__(
            partial(Preference.make_input, allow_ties=allow_ties, fill_truncated=fill_truncated),
            ranking_f,
            Input.PREFERENCES,
            Input.SEATS | Input.CANDIDATE_LIST | Input.FILTER_F,
        )

    @override
    def _build_input(self, data, **ranking_kwargs):
        return super()._build_input(data, all_candidates=ranking_kwargs.get("candidate_list"))

    @override
    def _check_precondition(self, score: Ranking[AnyName]):
        if score.empty():
            raise PreconditionError("preferences list is empty and no candidates provided")

    def calc(
        self,
        preferences,
        seats: int = 1,
        candidate_list: ipt.INames | None = None,
        random_seed: RandomSeed | None = None,
        filter_f: CandidateFilter[AnyName, Event] | None = None,
    ):
        """Allocate seats to candidates.

        Args
        ----
        preferences
            list of grouped preference ballots
        seats
            seats to allocate
        candidate_list
            full list of allowed candidates
        random_seed
            used to resolve candidates ties
        filter_f
            filter candidates that can win a seats
        """
        _state, result = self._calc(
            preferences,
            seats=seats,
            random_seed=random_seed,
            filter_f=filter_f,
            candidate_list=candidate_list,
        )
        return result


@allocators.register(
    "copeland",
    "condorcet_copeland",
)
class CondorcetCopelandAllocator(CondorcetAllocator):
    """Copeland's pairwise aggregation method.

    See `<https://en.wikipedia.org/wiki/Copeland%27s_method>`_

    :data:`.allocators` collection keys:

    - `copeland`
    - `condorcet_copeland`
    """

    def __init__(self, allow_ties=True, fill_truncated=False):
        """Create a Copeland allocator.

        Args
        ----
        allow_ties
            allow more than one candidate at the same preference position
        fill_truncated
            fill a truncated ballot with a tie of the remaining candidates
        """
        super().__init__(rankings.Copeland, allow_ties=allow_ties, fill_truncated=fill_truncated)


@allocators.register(
    "minimax",
    "condorcet_minimax",
)
class CondorcetMinimaxAllocator(CondorcetAllocator):
    """Minimax / Simpson-Kramer method.

    See `<https://en.wikipedia.org/wiki/Minimax_Condorcet>`_

    :data:`.allocators` collection keys:

    - `minimax`
    - `condorcet_minimax`
    """

    def __init__(self, margin=False, allow_ties=True, fill_truncated=False):
        """Create a Minimax allocator.

        Args
        ----
        margin
            If margin is True, use vote margins instead of difference of votes
            as the inner score.
        allow_ties
            allow more than one candidate at the same preference position
        fill_truncated
            fill a truncated ballot with a tie of the remaining candidates
        """
        self.use_margin = margin
        super().__init__(rankings.Minimax, allow_ties=allow_ties, fill_truncated=fill_truncated)

    @override
    def _base_ranking_kwargs(self):
        return {"margin": self.use_margin}
