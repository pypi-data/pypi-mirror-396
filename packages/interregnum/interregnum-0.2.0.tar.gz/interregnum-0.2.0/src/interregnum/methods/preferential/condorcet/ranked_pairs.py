#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Ranked pairs Condorcet allocator."""

from __future__ import annotations
from functools import partial
from typing import (
    Iterable,
    Iterator,
)
import dataclasses as dt

from ...types import (
    NonDeterministicAllocator,
    NonDeterministicState,
    Candidate,
    PreconditionError,
    allocators,
    Input,
    check_seats,
    AnyName,
    AnotherName,
)
from ... import inputs as ipt
from ..types import (
    Preference,
)
from ....graphs import UnweightedGraph
from ...adapters.multiwinner import MultiWinnerResultData
from ...events import (
    TieEvent,
    WinnerEvent,
)
from ....random import RandomSeed
from .rankings import RankedPairs


@dt.dataclass
class RPResultData(MultiWinnerResultData):
    """Result data for ranked pairs."""

    rounds: int = 0


@dt.dataclass
class RPState(NonDeterministicState):
    """Ranked-pairs allocator state."""

    data: RPResultData = dt.field(default_factory=RPResultData)

    def break_tie(
        self, candidates: Iterable[AnotherName], limit: int
    ) -> tuple[str, list[AnotherName]]:
        """Break a candidates tie.

        Args
        ----
        candidates
            list of tied candidates
        limit
            number of desired winners
        """
        return list(self.random_tie_break(candidates, limit).items())[0]

    def find_winners(self, score: RankedPairs[AnyName]) -> list[Candidate[AnyName]]:
        """Find winners given a ranked pairs score."""
        graph: UnweightedGraph[AnyName] = UnweightedGraph(score.contenders(), loops=False)

        for pair in self.iter_pairs(score):
            cand_x, cand_y = pair.name
            if not graph.reachable(cand_y, cand_x, closure=True):
                graph.connect(cand_x, cand_y)

        # can be multiple sources
        votes = len(score.contenders())
        return sorted(
            [Candidate(name=x, votes=votes) for x in graph.sources()], key=lambda x: x.name
        )

    def iter_pairs(
        self, score: RankedPairs[AnyName]
    ) -> Iterator[Candidate[tuple[AnyName, AnyName]]]:
        """Iterate ranked pairs."""
        grouped_pairs = list(score)

        while grouped_pairs:
            pairs = grouped_pairs[0]
            if len(pairs) > 1:
                # tie
                self.data.log.append(
                    TieEvent(
                        candidates=tuple(elem.name for elem in pairs),
                        condition={"type": "ranked_pairs", "round": self.data.rounds},
                    )
                )
                winner = self.break_tie(pairs, 1)[1][0]
            else:
                winner = pairs[0]
            yield winner
            pairs.remove(winner)
            if pairs:
                grouped_pairs[0] = pairs
            else:
                grouped_pairs.pop(0)


@allocators.register(
    "ranked_pairs",
    "condorcet_ranked_pairs",
)
class CondorcetRankedPairsAllocator(
    NonDeterministicAllocator[AnyName, RPResultData],
):
    """Ranked pairs Condorcet allocator.

    :data:`.allocators` collection keys:

    - `ranked_pairs`
    - `condorcet_ranked_pairs`
    """

    def __init__(self, allow_ties=True, fill_truncated=False):
        """Create a ranked pairs allocator.

        Args
        ----
        allow_ties
            allow more than one candidate at the same preference position
        fill_truncated
            fill a truncated ballot with a tie of the remaining candidates
        """
        super().__init__(Input.PREFERENCES, Input.CANDIDATE_LIST | Input.SEATS | Input.RANDOM_SEED)
        self._make_input_f = partial(
            Preference.make_input, allow_ties=allow_ties, fill_truncated=fill_truncated
        )

    def calc(
        self,
        preferences,
        seats: int = 1,
        random_seed: RandomSeed | None = None,
        candidate_list: ipt.INames | None = None,
    ):
        """Allocate seats to candidates.

        Args
        ----
        preferences
            list of grouped preference ballots
        seats
            seats to allocate
        random_seed
            used to break ties
        candidate_list
            full list of allowed candidates
        """
        check_seats(seats)
        state = RPState(random_seed=random_seed)
        data = state.data
        batches = self._make_input_f(preferences, all_candidates=candidate_list)

        elected: list[Candidate[AnyName]] = []
        data.remaining_seats = seats
        score: RankedPairs[AnyName] = RankedPairs(batches, candidate_list=candidate_list)

        if score.empty():
            raise PreconditionError("preferences list is empty and no candidates provided")

        while not score.empty() and data.remaining_seats:
            # get winners
            winners = state.find_winners(score)
            if len(winners) > data.remaining_seats:
                # tie
                data.log.append(
                    TieEvent(
                        candidates=tuple(elem.name for elem in winners),
                        condition={"type": "graph_sources", "round": data.rounds},
                    )
                )
                criterion, winners = state.break_tie(winners, data.remaining_seats)
            else:
                criterion = "graph_source"

            for cand in winners:
                elected.append(cand.with_seats(1))
                data.log.append(WinnerEvent(target=cand.name, criterion=criterion))
                data.remaining_seats -= 1
                if data.remaining_seats:
                    score.remove_candidate(cand)
            data.rounds += 1

        return state.make_result(elected, state.data)
