#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Instant Run-off."""
from __future__ import annotations
from typing import (
    Sequence,
    Iterable,
    Generic,
)
import dataclasses as dt
from collections import defaultdict
import itertools
from ...types import (
    Candidate,
    NonDeterministicAllocator,
    NonDeterministicState,
    Score,
    PreconditionError,
    allocators,
    Input,
    AnyName,
)
from ... import inputs as ipt
from ...events import (
    EventLog,
    QuotaWinnerEvent,
    TieEvent,
    IneligibleEvent,
    TransferredVotesEvent,
)
from ..types import (
    Preference,
)
from ...adapters.ranking import (
    break_tie_ranking,
    RankingTable,
)
from ....bidimensional.dataframe import DataFrame
from ....quotas import majority_quota

from ....random import RandomSeed
from ..ties import PartialTieBreak


@dt.dataclass
class TVResultData(EventLog):
    """Transerable vote result data."""

    threshold: Score = 0
    rounds: int = 0


@dt.dataclass
class TVTallyBoard(NonDeterministicState, Generic[AnyName]):
    """Data needed for the tally."""

    mode: PartialTieBreak
    batches: list[Preference[AnyName]] = dt.field(default_factory=list)
    history: dict[AnyName, list[Score]] = dt.field(default_factory=lambda: defaultdict(list))
    elected: list[Candidate[AnyName]] = dt.field(default_factory=list)
    data: TVResultData = dt.field(default_factory=TVResultData)

    def initial_exclusion(self, candidates: Iterable[AnyName] | None):
        """Prepare initial exclusion list."""
        if candidates is None:
            return
        excluded = frozenset(candidates or [])
        for name in excluded:
            if name in self.history:
                del self.history[name]
        temp_batches = (batch.remove(excluded) for batch in self.batches)
        self.batches = [batch for batch in temp_batches if batch.preference]

        if not self.history and not self.batches:
            raise PreconditionError("preferences list is empty and no candidates provided")

    def collect(self, preferences: Iterable[Sequence], candidate_list: Iterable[AnyName] | None):
        """Collect preferences to the tally board.

        Args
        ----
        preferences
            list of grouped preferences
        candidate_list
            full list of contenders
        """
        if candidate_list:
            for name in candidate_list:
                self.history[name] = []

        self.batches = Preference.make_input(
            preferences,
            allow_ties=False,
            all_candidates=self.history.keys(),
            skip_empty=True,
            raise_empty=False,
        )

        if not self.history and not self.batches:
            raise PreconditionError("preferences list is empty and no candidates provided")

    def get_eligible_candidates(self) -> list[Candidate[AnyName]]:
        """Get the list of eligible candidates, sorted by most voted to less voted."""
        out = Preference.get_front_candidates(
            self.batches, only_first_option=False, candidate_list=self.history.keys()
        )
        for cand in out:
            self.history[cand.name].append(cand.votes)

        return out

    def exclude(self, name: AnyName) -> None:
        """Exclude candidate 'name' from the tally."""
        if name in self.history:
            del self.history[name]

    def transfer_votes(self, source) -> None:
        """Transfer votes from candidate `source`."""
        out = []
        for batch in self.batches:
            if not batch.preference:
                continue
            new_batch = batch.remove([source])
            if batch.preference[0] == source:
                self.data.log.append(
                    TransferredVotesEvent(
                        source=source,
                        target=new_batch.preference[0] if new_batch.preference else None,
                        votes=batch.votes,
                    )
                )
            if new_batch.preference:
                out.append(new_batch)

        self.batches = out
        self.data.rounds += 1

    def remove_loser(self, losers: list[Candidate[AnyName]], lowest):
        """Remove loser from eligible and transfer votes."""
        if len(losers) > 1:
            self.data.log.append(
                TieEvent(
                    candidates=tuple(elem.name for elem in losers), condition=("less_voted", lowest)
                )
            )
            final_losers = self.break_tie(losers, ascending=True)
        else:
            final_losers = {"less_voted": [losers[0]]}

        assert len(final_losers) == 1
        for criterion, inelegible_set in final_losers.items():
            for loser in inelegible_set:
                self.data.log.append(
                    IneligibleEvent(
                        target=loser.name,
                        criterion=criterion,
                        condition={
                            "votes": loser.votes,
                            "threshold": lowest,
                            "round": self.data.rounds,
                        },
                    )
                )
                self.transfer_votes(loser.name)
                self.exclude(loser.name)
        return self.get_eligible_candidates()

    def add_winner(self, winners: list[Candidate[AnyName]], criterion):
        """Add winner to elected."""
        if len(winners) > 1:
            self.data.log.append(
                TieEvent(
                    candidates=tuple(w.name for w in winners),
                    condition={"most_voted": self.data.threshold, "round": self.data.rounds},
                )
            )
            winner_batches = self.break_tie(winners)
        else:
            winner_batches = {criterion: winners}

        for crit, items in winner_batches.items():
            for winner in items:
                # TODO add round
                self.data.log.append(
                    QuotaWinnerEvent(target=winner.name, quota=self.data.threshold, criterion=crit)
                )
                self.elected.append(winner.with_seats(1))

    def break_tie(
        self, candidates: Sequence[Candidate[AnyName]], ascending: bool = False
    ) -> dict[str, list[Candidate[AnyName]]]:
        """Break candidates ties using partial score rankings."""
        if self.mode == PartialTieBreak.RANDOM:
            return self.random_tie_break(candidates, 1)

        table: DataFrame[AnyName, Score] = DataFrame()
        for cand in candidates:
            table.insert_row(cand.name, self.history[cand.name][:-1])

        from_first = self.mode == PartialTieBreak.FROM_FIRST_VOTE

        return break_tie_ranking(
            RankingTable(table, 1, ascending=ascending, from_first=from_first),
            1,
            fallback=self.random_tie_break,
            first_criterion="tie_break_partial_vote",
        )


@allocators.register(
    "instant_runoff",
    "instant_run_off",
    "alternative_voting",
    "ranked_choice",
    "ranked_choice_voting",
    "transferable_voting",
)
class InstantRunOffAllocator(
    NonDeterministicAllocator[AnyName, TVResultData],
):
    """Transferable vote / Instant run-off voting.

    The most voted candidate which reaches the absolute majority wins
    the seats. If any candidate has the majority of the votes, the less
    voted candidate is removed and the votes are assigned to the next preferences.

    See `<https://en.wikipedia.org/wiki/Instant-runoff_voting>`_

    :data:`.allocators` collection keys:

    - `instant_runoff`
    - `instant_run_off`
    - `alternative_voting`
    - `ranked_choice`
    - `ranked_choice_voting`
    - `transferable_voting`
    """

    def __init__(self, tie_break: PartialTieBreak | str = "from_first_vote"):
        """Create an Instant Run-off allocator.

        Args
        ----

        tie_break
            strategy for breaking candidates ties using partial scores.
        """
        super().__init__(
            Input.PREFERENCES, Input.RANDOM_SEED | Input.CANDIDATE_LIST | Input.TOTAL_VOTES
        )
        self.tie_break_rule = tie_break

    def calc(
        self,
        preferences,
        random_seed: RandomSeed | None = None,
        candidate_list: ipt.INames | None = None,
        total_votes: Score | None = None,
        exclude_candidates: ipt.INames | None = None,
    ):
        """Allocate seats to candidates.

        Args
        ----
        preferences
            list of grouped preference ballots
        random_seed
            used to break ties
        candidate_list
            full list of allowed candidates
        total_votes
            total number of votes used when calculating the majority quota (if
            empty, the number of ballots will be used.)
        exclude_candidates
            exclude the provided candidates from winning seats
        """
        state: TVTallyBoard[AnyName] = TVTallyBoard(
            mode=PartialTieBreak.get_value(self.tie_break_rule), random_seed=random_seed
        )
        state.collect(preferences, candidate_list)
        state.initial_exclusion(exclude_candidates)

        total_votes = total_votes or sum(x.votes for x in state.batches)
        assert total_votes is not None

        majority = majority_quota(total_votes)
        state.data.threshold = majority.reference

        state.data.rounds = 0
        eligible = state.get_eligible_candidates()

        while eligible:
            if len(eligible) > 1:
                winners = list(itertools.takewhile(lambda x: majority.reached(x.votes), eligible))
                criterion = "majority_reached"
            else:
                winners = eligible
                criterion = "last_candidate"

            if winners:
                state.add_winner(winners, criterion)
                break

            assert eligible
            # majority not reached
            # remove round candidate with less votes
            lowest = eligible[-1].votes

            losers = list(itertools.takewhile(lambda x: x.votes <= lowest, reversed(eligible)))

            eligible = state.remove_loser(losers, lowest)

        return state.make_result(state.elected, state.data)
