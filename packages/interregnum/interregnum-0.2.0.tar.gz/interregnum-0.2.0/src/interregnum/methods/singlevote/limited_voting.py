#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""
Limited voting / Partial block voting.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Loreg:1985]_

----
"""
from __future__ import annotations
from typing import (
    Iterable,
)
from ..types import Candidate, AnyName, allocators, Input, CandidateFilter

from ...random import RandomSeed
from ..adapters.ranking import RankingList
from ..adapters.multiwinner import MultiWinnerAdapter, MultiWinnerResultData
from ..events import Event
from .. import inputs as ipt


class MostVotedRanking(RankingList[AnyName]):
    """Ranking based on votes."""

    def __init__(self, scores: Iterable[Candidate[AnyName]]):
        """Create a ranking list from a list of candidates."""
        super().__init__(sorted(scores, key=lambda x: (-x.votes, x.name)), ascending=False)


@allocators.register(
    "limited_voting",
    "partial_block_voting",
)
class LimitedVotingAllocator(MultiWinnerAdapter[AnyName, MultiWinnerResultData]):
    """Limited voting / Partial block voting.

    Given that there are N available seats, the N most voted
    candidates win a seat each one.

    Used in the election to the Spanish Senate.

    See [Loreg:1985]_ and `<https://en.wikipedia.org/wiki/Limited_voting>`_

    :data:`.allocators` collection keys:

    - `limited_voting`
    - `partial_block_voting`
    """

    def __init__(self):
        """Create a limited voting allocator.

        Examples
        --------
        >>> limited_voting = LimitedVotingAllocator()
        """
        super().__init__(
            Candidate.make_input,
            MostVotedRanking[AnyName],
            Input.CANDIDATES | Input.SEATS,
            Input.FILTER_F | Input.RANDOM_SEED,
        )

    def calc(
        self,
        candidates: ipt.ICandidates,
        seats: int,
        random_seed: RandomSeed | None = None,
        filter_f: CandidateFilter[AnyName, Event] | None = None,
        **ranking_args,
    ):
        """Allocate `candidates` to `seats`.

        Initial seats will be ignored.

        Args
        ----
        candidates
            list of candidates
        seats
            number of expected winners
        random_seed
            used to break ties
        filter_f
            restrict to filtered candidates
        """
        _state, result = super()._calc(
            candidates, seats=seats, random_seed=random_seed, filter_f=filter_f, **ranking_args
        )
        return result
