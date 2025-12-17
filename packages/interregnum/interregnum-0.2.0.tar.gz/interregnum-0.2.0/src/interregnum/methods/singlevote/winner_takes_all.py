#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""First past the post."""

from __future__ import annotations

from ...random import RandomSeed
from ..types import Candidate, AnyName, allocators, Input
from ..adapters.multiwinner import WinnerTakesAllAdapter, MultiWinnerResultData
from .limited_voting import MostVotedRanking
from .. import inputs as ipt


@allocators.register(
    "winner_takes_all",
    "first_past_the_post",
)
class WinnerTakesAllAllocator(WinnerTakesAllAdapter[AnyName, MultiWinnerResultData]):
    """Winner-Takes-All / First past the post.

    Each seat will be assigned to the most voted candidate in different rounds.

    The winner will take all the seats.

    :py:data:`.allocators` collection keys:

    - `winner_takes_all`
    - `first_past_the_post`
    """

    def __init__(self):
        """Create a First Past The Post allocator.

        Examples
        --------
        >>> wta = WinnerTakesAllAllocator()
        """
        super().__init__(
            Candidate.make_input,
            MostVotedRanking,
            Input.CANDIDATES,
            Input.SEATS,
        )

    def calc(
        self,
        candidates: ipt.ICandidates,
        seats: int = 1,
        random_seed: RandomSeed | None = None,
        **kwargs,
    ):
        """Allocate `candidates` to `seats`.

        Args
        ----
        candidates
            list of candidates
        seats
            seats to allocate
        random_seed
            used to break ties
        """
        _state, result = super()._calc(candidates, seats=seats, random_seed=random_seed, **kwargs)
        return result
